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
    has_synced_analytics: bool = False

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

    def _calculate_stars(self, score: int) -> int:
        """Convert 0-100 score to 0-5 stars based on 20-point increments."""
        if score >= 80:
            return 5
        if score >= 60:
            return 4
        if score >= 40:
            return 3
        if score >= 20:
            return 2
        if score > 0:
            return 1
        return 0

    @rx.event(background=True)
    async def on_load(self):
        """Initialize tables and verify institution context."""
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
                text("SELECT id FROM qs_stars_assessments WHERE institution_id = :iid"),
                {"iid": inst_id},
            )
            row = result.first()
            if not row:
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
            async with self:
                self.assessment_id = row[0]
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
        """This method is now a no-op as we pull directly from lens configuration."""
        pass

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
        """Synchronize Insight Scores and load real indicator gap data from database."""
        async with self:
            self.is_syncing_analytics = True
            from app.states.analytics_state import AnalyticsState

            analytics = await self.get_state(AnalyticsState)
            hei_state = await self.get_state(HEIState)
            self.analytics_research_score = analytics.research_score
            self.analytics_employability_score = analytics.employability_score
            self.analytics_global_engagement_score = analytics.global_engagement_score
            self.analytics_learning_experience_score = (
                analytics.learning_experience_score
            )
            self.analytics_sustainability_score = analytics.sustainability_score
            self.analytics_overall_score = analytics.overall_score
            self.analytics_recommendations = analytics.ai_recommendations
            self.overall_stars = self._calculate_stars(self.analytics_overall_score)
            self.teaching_stars = self._calculate_stars(
                self.analytics_learning_experience_score
            )
            self.employability_stars = self._calculate_stars(
                self.analytics_employability_score
            )
            self.academic_development_stars = self._calculate_stars(
                self.analytics_research_score
            )
            self.inclusiveness_stars = self._calculate_stars(
                self.analytics_global_engagement_score
            )
            self.last_sync_time = datetime.datetime.now().strftime("%H:%M:%S")
            if self.analytics_overall_score == 0:
                self.is_syncing_analytics = False
                yield rx.toast(
                    "No analytics data found. Please ensure assessment data is entered."
                )
                return
            inst_id = int(hei_state.selected_hei["id"])
            assessment_id = self.assessment_id
        async with rx.asession() as session:
            result = await session.execute(
                text("""
                SELECT 
                    i.indicator_name, 
                    l.lens_name as category, 
                    COALESCE(CAST(s.value AS DECIMAL), 0) as achieved,
                    i.indicator_weight_pct as max_s
                FROM ranking_indicators i
                JOIN ranking_lenses l ON i.lens_id = l.id
                LEFT JOIN institution_scores s ON i.id = s.indicator_id 
                    AND s.institution_id = :inst_id 
                    AND s.ranking_year = 2025
                ORDER BY l.lens_name, i.indicator_name
                """),
                {"inst_id": inst_id},
            )
            db_rows = result.all()
            plan_res = await session.execute(
                text(
                    "SELECT indicator_name, target_score, notes FROM qs_action_plans WHERE assessment_id = :aid"
                ),
                {"aid": assessment_id},
            )
            plans_map = {
                r[0]: {"target": float(r[1]), "notes": r[2]} for r in plan_res.all()
            }
            cat_map = {
                "Learning Experience": "Teaching",
                "Employability & Outcomes": "Employability",
                "Research & Discovery": "Academic Development",
                "Global Engagement": "Inclusiveness",
            }
            merged = []
            for i_name, i_cat, achieved, max_s in db_rows:
                target_cat = cat_map.get(i_cat, "Other")
                if target_cat == "Other":
                    continue
                plan = plans_map.get(i_name, {"target": float(achieved), "notes": ""})
                merged.append(
                    {
                        "id": 0,
                        "assessment_id": assessment_id,
                        "indicator_name": i_name,
                        "category": target_cat,
                        "points_achieved": float(achieved),
                        "max_score": float(max_s) if float(max_s) > 0 else 100.0,
                        "target_score": plan["target"],
                        "notes": plan["notes"] if plan["notes"] else "",
                    }
                )
            async with self:
                self.indicator_scores = merged
                self.has_synced_analytics = True
                self.is_syncing_analytics = False