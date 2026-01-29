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
    methodology_version: str = "5.2"
    overall_stars: int = 0
    teaching_stars: int = 0
    employability_stars: int = 0
    academic_development_stars: int = 0
    inclusiveness_stars: int = 0
    indicator_scores: list[IndicatorScore] = []
    is_loading: bool = False
    is_saving: bool = False
    is_syncing_analytics: bool = False
    last_sync_time: str = ""
    analytics_research_score: int = 0
    analytics_employability_score: int = 0
    analytics_global_engagement_score: int = 0
    analytics_learning_experience_score: int = 0
    analytics_sustainability_score: int = 0
    analytics_overall_score: int = 0
    analytics_recommendations: list[dict[str, str]] = []

    @rx.var
    def weak_indicators_count(self) -> int:
        """Count indicators with score < 50% of max."""
        count = 0
        for ind in self.indicator_scores:
            if ind["max_score"] > 0 and ind["points_achieved"] / ind["max_score"] < 0.5:
                count += 1
        return count

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
                    "SELECT id, methodology_version, overall_stars, teaching_stars, employability_stars, academic_development_stars, inclusiveness_stars FROM qs_stars_assessments WHERE institution_id = :iid"
                ),
                {"iid": inst_id},
            )
            row = result.first()
            if row:
                assessment_id = row[0]
                async with self:
                    self.assessment_id = row[0]
                    self.methodology_version = row[1]
                    self.overall_stars = row[2]
                    self.teaching_stars = row[3]
                    self.employability_stars = row[4]
                    self.academic_development_stars = row[5]
                    self.inclusiveness_stars = row[6]
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
        yield PostAssessmentState.load_institution_scores_for_insights
        async with self:
            self.is_loading = False

    async def _ensure_tables(self, session):
        await session.execute(
            text("""
            CREATE TABLE IF NOT EXISTS qs_stars_assessments (
                id SERIAL PRIMARY KEY,
                institution_id INTEGER NOT NULL,
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
        """Save audit methodology version."""
        async with self:
            self.is_saving = True
        async with rx.asession() as session:
            await session.execute(
                text(
                    "UPDATE qs_stars_assessments SET methodology_version = :ver WHERE id = :aid"
                ),
                {"ver": self.methodology_version, "aid": self.assessment_id},
            )
            await session.commit()
        async with self:
            self.is_saving = False
            yield rx.toast("Audit metadata saved.")

    @rx.event(background=True)
    async def load_institution_scores_for_insights(self):
        """Synchronize Insight Scores and recommendations directly from AnalyticsState."""
        async with self:
            self.is_syncing_analytics = True
            from app.states.analytics_state import AnalyticsState

            analytics = await self.get_state(AnalyticsState)
        async with self:
            self.analytics_research_score = analytics.research_score
            self.analytics_employability_score = analytics.employability_score
            self.analytics_global_engagement_score = analytics.global_engagement_score
            self.analytics_learning_experience_score = (
                analytics.learning_experience_score
            )
            self.analytics_sustainability_score = analytics.sustainability_score
            self.analytics_overall_score = analytics.overall_score
            self.analytics_recommendations = analytics.ai_recommendations
            self.last_sync_time = datetime.datetime.now().strftime("%H:%M:%S")
            if self.analytics_overall_score == 0:
                yield rx.toast(
                    "No analytics data found. Please ensure assessment data is entered and visit the Analytics page.",
                    duration=4000,
                )
            self.is_syncing_analytics = False
        async with rx.asession() as session:
            result = await session.execute(
                text("""
                SELECT i.code, s.value 
                FROM institution_scores s 
                JOIN ranking_indicators i ON s.indicator_id = i.id 
                WHERE s.institution_id = :iid AND s.ranking_year = 2025
                """),
                {"iid": inst_id},
            )
            rows = result.all()
            scores = {row[0]: float(row[1]) if row[1] else 0.0 for row in rows}
            s_academic = min(100, scores.get("academic_reputation", 0) / 90.0 * 100)
            s_citations = min(100, scores.get("citations_per_faculty", 0) / 20.0 * 100)
            research = int(s_academic * 0.6 + s_citations * 0.4)
            s_emp_rep = min(100, scores.get("employer_reputation", 0) / 90.0 * 100)
            s_emp_out = min(100, scores.get("employment_outcomes", 0) / 95.0 * 100)
            employability = int(s_emp_rep * 0.75 + s_emp_out * 0.25)
            s_irn = min(
                100, scores.get("international_research_network", 0) / 80.0 * 100
            )
            s_ifac = min(100, scores.get("international_faculty_ratio", 0) / 15.0 * 100)
            s_istud = min(
                100, scores.get("international_student_ratio", 0) / 10.0 * 100
            )
            global_eng = int((s_irn + s_ifac + s_istud) / 3)
            fs_ratio = scores.get("faculty_student_ratio", 0)
            s_learning = int(
                max(0, min(100, 12.0 / fs_ratio * 100 if fs_ratio > 0 else 0))
            )
            s_sus = min(100, scores.get("sustainability_metrics", 0) / 85.0 * 100)
            sustainability = int(s_sus)
            overall = int(
                research * 0.5
                + employability * 0.2
                + global_eng * 0.15
                + s_learning * 0.1
                + sustainability * 0.05
            )
            async with self:
                self.analytics_research_score = research
                self.analytics_employability_score = employability
                self.analytics_global_engagement_score = global_eng
                self.analytics_learning_experience_score = s_learning
                self.analytics_sustainability_score = sustainability
                self.analytics_overall_score = overall
                try:
                    from app.states.analytics_state import AnalyticsState

                    analytics = await self.get_state(AnalyticsState)
                    self.analytics_recommendations = analytics.ai_recommendations
                except Exception as e:
                    logging.exception(f"Error loading analytics recommendations: {e}")