import reflex as rx
from typing import TypedDict, Any, Optional
import datetime
from sqlalchemy import text
import logging
from app.states.hei_state import HEIState


class IndicatorScore(TypedDict):
    id: int
    assessment_id: int
    indicator_name: str
    category: str
    points_achieved: float
    max_score: float
    target_score: float
    notes: str


class PostAssessmentState(rx.State):
    assessment_id: int = -1
    audit_start_date: str = datetime.date.today().isoformat()
    audit_delivery_date: str = datetime.date.today().isoformat()
    audit_validity_date: str = (
        datetime.date.today() + datetime.timedelta(days=365 * 3)
    ).isoformat()
    methodology_version: str = "5.2"
    overall_stars: int = 0
    teaching_stars: int = 0
    employability_stars: int = 0
    academic_development_stars: int = 0
    inclusiveness_stars: int = 0
    indicator_scores: list[IndicatorScore] = []
    is_loading: bool = False
    is_saving: bool = False

    @rx.var
    def days_until_expiry(self) -> int:
        try:
            if not self.audit_validity_date:
                return 0
            validity = datetime.date.fromisoformat(self.audit_validity_date)
            today = datetime.date.today()
            return (validity - today).days
        except (ValueError, TypeError) as e:
            logging.exception(f"Error parsing audit validity date: {e}")
            return 0

    @rx.var
    def audit_status(self) -> str:
        days = self.days_until_expiry
        if days < 0:
            return "Expired"
        elif days <= 90:
            return "Expiring Soon"
        return "Valid"

    @rx.var
    def audit_status_color(self) -> str:
        status = self.audit_status
        if status == "Expired":
            return "red"
        elif status == "Expiring Soon":
            return "amber"
        return "emerald"

    @rx.var
    def weak_indicators_count(self) -> int:
        """Count indicators with score < 50% of max."""
        count = 0
        for ind in self.indicator_scores:
            if ind["max_score"] > 0 and ind["points_achieved"] / ind["max_score"] < 0.5:
                count += 1
        return count

    @rx.var
    def audit_time_elapsed_percent(self) -> float:
        """Calculate percentage of time elapsed in the audit validity period."""
        try:
            if not self.audit_start_date or not self.audit_validity_date:
                return 0.0
            start = datetime.date.fromisoformat(self.audit_start_date)
            validity = datetime.date.fromisoformat(self.audit_validity_date)
            today = datetime.date.today()
            total_days = (validity - start).days
            elapsed = (today - start).days
            if total_days <= 0:
                return 100.0
            return max(0.0, min(100.0, elapsed / total_days * 100))
        except Exception as e:
            logging.exception(f"Error calculating audit time elapsed: {e}")
            return 0.0

    @rx.event
    def set_audit_start_date(self, value: str):
        self.audit_start_date = value

    @rx.event
    def set_audit_delivery_date(self, value: str):
        self.audit_delivery_date = value

    @rx.event
    def set_audit_validity_date(self, value: str):
        self.audit_validity_date = value

    @rx.event
    def set_methodology_version(self, value: str):
        self.methodology_version = value

    @rx.event
    def set_indicator_target(self, indicator_name: str, value: str):
        """Update target score in local state."""
        try:
            val = float(value)
        except ValueError as e:
            logging.exception(
                f"Error converting indicator target value '{value}' to float: {e}"
            )
            val = 0.0
        new_scores = []
        for ind in self.indicator_scores:
            if ind["indicator_name"] == indicator_name:
                ind = ind.copy()
                ind["target_score"] = val
            new_scores.append(ind)
        self.indicator_scores = new_scores

    @rx.event
    def set_indicator_notes(self, indicator_name: str, value: str):
        """Update notes in local state."""
        new_scores = []
        for ind in self.indicator_scores:
            if ind["indicator_name"] == indicator_name:
                ind = ind.copy()
                ind["notes"] = value
            new_scores.append(ind)
        self.indicator_scores = new_scores

    @rx.event(background=True)
    async def save_indicator_plan(self, indicator_name: str):
        """Persist action plan for a single indicator to DB."""
        async with self:
            target_ind = next(
                (
                    i
                    for i in self.indicator_scores
                    if i["indicator_name"] == indicator_name
                ),
                None,
            )
            if not target_ind:
                return
            current_score = target_ind["points_achieved"]
            target_score = target_ind["target_score"]
            notes = target_ind["notes"]
            assessment_id = self.assessment_id
        async with rx.asession() as session:
            await session.execute(
                text("""
                INSERT INTO qs_action_plans (assessment_id, indicator_name, current_score, target_score, notes)
                VALUES (:aid, :name, :curr, :targ, :notes)
                ON CONFLICT (assessment_id, indicator_name)
                DO UPDATE SET target_score = EXCLUDED.target_score, notes = EXCLUDED.notes, updated_at = CURRENT_TIMESTAMP
                """),
                {
                    "aid": assessment_id,
                    "name": indicator_name,
                    "curr": current_score,
                    "targ": target_score,
                    "notes": notes,
                },
            )
            await session.commit()
        yield rx.toast(f"Action plan for '{indicator_name}' saved.")

    @rx.event(background=True)
    async def on_load(self):
        """Initialize tables and load data."""
        async with self:
            self.is_loading = True
        async with rx.asession() as session:
            await self._ensure_tables(session)
            async with self:
                hei_state = await self.get_state(HEIState)
            if not hei_state.selected_hei:
                async with self:
                    self.is_loading = False
                return
            inst_id = int(hei_state.selected_hei["id"])
            result = await session.execute(
                text(
                    "SELECT id, audit_start_date, audit_delivery_date, audit_validity_date, methodology_version, overall_stars, teaching_stars, employability_stars, academic_development_stars, inclusiveness_stars FROM qs_stars_assessments WHERE institution_id = :iid"
                ),
                {"iid": inst_id},
            )
            row = result.first()
            if row:
                assessment_id = row[0]
                async with self:
                    self.assessment_id = row[0]
                    self.audit_start_date = row[1].isoformat() if row[1] else ""
                    self.audit_delivery_date = row[2].isoformat() if row[2] else ""
                    self.audit_validity_date = row[3].isoformat() if row[3] else ""
                    self.methodology_version = row[4]
                    self.overall_stars = row[5]
                    self.teaching_stars = row[6]
                    self.employability_stars = row[7]
                    self.academic_development_stars = row[8]
                    self.inclusiveness_stars = row[9]
            else:
                await session.execute(
                    text(
                        "INSERT INTO qs_stars_assessments (institution_id, methodology_version) VALUES (:iid, '5.2')"
                    ),
                    {"iid": inst_id},
                )
                await session.commit()
                result = await session.execute(
                    text(
                        "SELECT id FROM qs_stars_assessments WHERE institution_id = :iid"
                    ),
                    {"iid": inst_id},
                )
                row = result.first()
                assessment_id = row[0]
                async with self:
                    self.assessment_id = assessment_id
                    self.methodology_version = "5.2"
                    self.overall_stars = 0
                    self.teaching_stars = 0
                    self.employability_stars = 0
                    self.academic_development_stars = 0
                    self.inclusiveness_stars = 0
            ind_res = await session.execute(
                text(
                    "SELECT id, assessment_id, indicator_name, category, points_achieved, max_score FROM qs_indicator_scores WHERE assessment_id = :aid ORDER BY category, indicator_name"
                ),
                {"aid": assessment_id},
            )
            ind_rows = ind_res.fetchall()
            if not ind_rows:
                await self._seed_default_indicators(session, assessment_id)
                ind_res = await session.execute(
                    text(
                        "SELECT id, assessment_id, indicator_name, category, points_achieved, max_score FROM qs_indicator_scores WHERE assessment_id = :aid ORDER BY category, indicator_name"
                    ),
                    {"aid": assessment_id},
                )
                ind_rows = ind_res.fetchall()
            plan_res = await session.execute(
                text(
                    "SELECT indicator_name, target_score, notes FROM qs_action_plans WHERE assessment_id = :aid"
                ),
                {"aid": assessment_id},
            )
            plans_map = {
                r[0]: {"target": float(r[1]), "notes": r[2]}
                for r in plan_res.fetchall()
            }
            merged_scores = []
            for r in ind_rows:
                ind_name = r[2]
                current_score = float(r[4])
                plan = plans_map.get(ind_name, {"target": current_score, "notes": ""})
                merged_scores.append(
                    {
                        "id": r[0],
                        "assessment_id": r[1],
                        "indicator_name": ind_name,
                        "category": r[3],
                        "points_achieved": current_score,
                        "max_score": float(r[5]),
                        "target_score": plan["target"],
                        "notes": plan["notes"] if plan["notes"] else "",
                    }
                )
            async with self:
                self.indicator_scores = merged_scores
                self.is_loading = False

    async def _ensure_tables(self, session):
        await session.execute(
            text("""
            CREATE TABLE IF NOT EXISTS qs_stars_assessments (
                id SERIAL PRIMARY KEY,
                institution_id INTEGER NOT NULL,
                audit_start_date DATE,
                audit_delivery_date DATE,
                audit_validity_date DATE,
                methodology_version VARCHAR(50),
                overall_stars INTEGER DEFAULT 0,
                teaching_stars INTEGER DEFAULT 0,
                employability_stars INTEGER DEFAULT 0,
                academic_development_stars INTEGER DEFAULT 0,
                inclusiveness_stars INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(institution_id)
            );
        """)
        )
        await session.execute(
            text("""
            CREATE TABLE IF NOT EXISTS qs_indicator_scores (
                id SERIAL PRIMARY KEY,
                assessment_id INTEGER REFERENCES qs_stars_assessments(id),
                indicator_name VARCHAR(255),
                category VARCHAR(100),
                points_achieved DECIMAL(10, 2),
                max_score DECIMAL(10, 2),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(assessment_id, indicator_name)
            );
        """)
        )
        await session.execute(
            text("""
            CREATE TABLE IF NOT EXISTS qs_action_plans (
                id SERIAL PRIMARY KEY,
                assessment_id INTEGER REFERENCES qs_stars_assessments(id),
                indicator_name VARCHAR(255),
                current_score DECIMAL(10, 2),
                target_score DECIMAL(10, 2),
                notes TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(assessment_id, indicator_name)
            );
        """)
        )
        await session.commit()

    async def _seed_default_indicators(self, session, assessment_id):
        defaults = [
            ("Faculty-Student Ratio", "Teaching", 0, 40),
            ("Professors per 100 Students", "Teaching", 0, 20),
            ("Student Satisfaction", "Teaching", 0, 40),
            ("Graduate Employment Rate", "Employability", 0, 50),
            ("Employer Partnerships", "Employability", 0, 25),
            ("Career Services", "Employability", 0, 25),
            ("Publications per Faculty", "Academic Development", 0, 40),
            ("Research Income", "Academic Development", 0, 30),
            ("PhD Staff Ratio", "Academic Development", 0, 30),
            ("International Students Ratio", "Inclusiveness", 0, 20),
            ("International Faculty Ratio", "Inclusiveness", 0, 20),
            ("Scholarships Offered", "Inclusiveness", 0, 30),
            ("Facilities Access", "Inclusiveness", 0, 30),
        ]
        for ind_name, cat, score, max_s in defaults:
            await session.execute(
                text(
                    "INSERT INTO qs_indicator_scores (assessment_id, indicator_name, category, points_achieved, max_score) VALUES (:aid, :name, :cat, :score, :max) ON CONFLICT (assessment_id, indicator_name) DO NOTHING"
                ),
                {
                    "aid": assessment_id,
                    "name": ind_name,
                    "cat": cat,
                    "score": score,
                    "max": max_s,
                },
            )
        await session.commit()

    @rx.event(background=True)
    async def save_audit_metadata(self):
        """Save audit dates and version."""
        async with self:
            self.is_saving = True
        async with rx.asession() as session:
            await session.execute(
                text(
                    "UPDATE qs_stars_assessments SET audit_start_date = :start, audit_delivery_date = :del, audit_validity_date = :val, methodology_version = :ver WHERE id = :aid"
                ),
                {
                    "start": self.audit_start_date if self.audit_start_date else None,
                    "del": self.audit_delivery_date
                    if self.audit_delivery_date
                    else None,
                    "val": self.audit_validity_date
                    if self.audit_validity_date
                    else None,
                    "ver": self.methodology_version,
                    "aid": self.assessment_id,
                },
            )
            await session.commit()
        async with self:
            self.is_saving = False
            yield rx.toast("Audit metadata saved.")

    @rx.event(background=True)
    async def simulate_audit_update(self):
        """DEMO ONLY: Updates scores randomly to simulate a completed audit import."""
        import random

        async with self:
            self.is_loading = True
        async with rx.asession() as session:
            await session.execute(
                text(
                    "UPDATE qs_stars_assessments SET overall_stars = 4, teaching_stars = 5, employability_stars = 4, academic_development_stars = 3, inclusiveness_stars = 5 WHERE id = :aid"
                ),
                {"aid": self.assessment_id},
            )
            indicators_res = await session.execute(
                text(
                    "SELECT indicator_name, max_score FROM qs_indicator_scores WHERE assessment_id = :aid"
                ),
                {"aid": self.assessment_id},
            )
            rows = indicators_res.all()
            for name, max_score in rows:
                achieved = round(random.uniform(0.3, 0.95) * float(max_score), 2)
                await session.execute(
                    text(
                        "UPDATE qs_indicator_scores SET points_achieved = :score WHERE assessment_id = :aid AND indicator_name = :name"
                    ),
                    {"score": achieved, "aid": self.assessment_id, "name": name},
                )
            await session.commit()
        yield PostAssessmentState.on_load
        async with self:
            self.is_loading = False
            yield rx.toast("Audit data simulated successfully.")