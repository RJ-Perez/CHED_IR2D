import reflex as rx
import asyncio
import json
from sqlalchemy import text
from app.states.hei_state import HEIState


class DashboardState(rx.State):
    """Manages data entry for the ranking readiness assessment.
    It tracks individual indicator scores and their associated evidence files.
    """

    academic_reputation: str = ""
    citations_per_faculty: str = ""
    employer_reputation: str = ""
    employment_outcomes: str = ""
    international_research_network: str = ""
    international_faculty_ratio: str = ""
    international_student_ratio: str = ""
    international_student_diversity: str = ""
    faculty_student_ratio: str = ""
    sustainability_metrics: str = ""
    uploaded_research_files: list[str] = []
    uploaded_employability_files: list[str] = []
    uploaded_global_engagement_files: list[str] = []
    uploaded_learning_experience_files: list[str] = []
    uploaded_sustainability_files: list[str] = []
    is_saving: bool = False

    @rx.var
    def progress(self) -> int:
        """Calculate completion progress based on filled fields."""
        fields = [
            self.academic_reputation,
            self.citations_per_faculty,
            self.employer_reputation,
            self.employment_outcomes,
            self.international_research_network,
            self.international_faculty_ratio,
            self.international_student_ratio,
            self.faculty_student_ratio,
            self.sustainability_metrics,
        ]
        filled_count = len([f for f in fields if f.strip() != ""])
        total_fields = 9
        return int(filled_count / total_fields * 100)

    @rx.event
    def set_academic_reputation(self, value: str):
        self.academic_reputation = value

    @rx.event
    def set_citations_per_faculty(self, value: str):
        self.citations_per_faculty = value

    @rx.event
    def set_employer_reputation(self, value: str):
        self.employer_reputation = value

    @rx.event
    def set_employment_outcomes(self, value: str):
        self.employment_outcomes = value

    @rx.event
    def set_international_research_network(self, value: str):
        self.international_research_network = value

    @rx.event
    def set_international_faculty_ratio(self, value: str):
        self.international_faculty_ratio = value

    @rx.event
    def set_international_student_ratio(self, value: str):
        self.international_student_ratio = value

    @rx.event
    def set_international_student_diversity(self, value: str):
        self.international_student_diversity = value

    @rx.event
    def set_faculty_student_ratio(self, value: str):
        self.faculty_student_ratio = value

    @rx.event
    def set_sustainability_metrics(self, value: str):
        self.sustainability_metrics = value

    @rx.event
    async def handle_research_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for Research section."""
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.name
            with outfile.open("wb") as file_object:
                file_object.write(upload_data)
            self.uploaded_research_files.append(file.name)

    @rx.event
    async def handle_employability_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for Employability section."""
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.name
            with outfile.open("wb") as file_object:
                file_object.write(upload_data)
            self.uploaded_employability_files.append(file.name)

    @rx.event
    async def handle_global_engagement_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for Global Engagement section."""
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.name
            with outfile.open("wb") as file_object:
                file_object.write(upload_data)
            self.uploaded_global_engagement_files.append(file.name)

    @rx.event
    async def handle_learning_experience_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for Learning Experience section."""
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.name
            with outfile.open("wb") as file_object:
                file_object.write(upload_data)
            self.uploaded_learning_experience_files.append(file.name)

    @rx.event
    async def handle_sustainability_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for Sustainability section."""
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.name
            with outfile.open("wb") as file_object:
                file_object.write(upload_data)
            self.uploaded_sustainability_files.append(file.name)

    @rx.event(background=True)
    async def on_load(self):
        """Load existing data for the selected institution."""
        async with rx.asession() as session:
            await self._ensure_static_data(session)
            async with self:
                hei_state = await self.get_state(HEIState)
            if not hei_state.selected_hei:
                return
            institution_id = int(hei_state.selected_hei["id"])
            rows = await session.execute(
                text("""
                SELECT 
                    i.code, 
                    s.value, 
                    s.evidence_files
                FROM institution_scores s
                JOIN ranking_indicators i ON s.indicator_id = i.id
                WHERE s.institution_id = :inst_id AND s.ranking_year = 2025
                """),
                {"inst_id": institution_id},
            )
            data = rows.all()
            async with self:
                for code, value, evidence in data:
                    if code == "academic_reputation":
                        self.academic_reputation = value
                        self.uploaded_research_files = (
                            json.loads(evidence) if evidence else []
                        )
                    elif code == "citations_per_faculty":
                        self.citations_per_faculty = value
                    elif code == "employer_reputation":
                        self.employer_reputation = value
                        self.uploaded_employability_files = (
                            json.loads(evidence) if evidence else []
                        )
                    elif code == "employment_outcomes":
                        self.employment_outcomes = value
                    elif code == "international_research_network":
                        self.international_research_network = value
                        self.uploaded_global_engagement_files = (
                            json.loads(evidence) if evidence else []
                        )
                    elif code == "international_faculty_ratio":
                        self.international_faculty_ratio = value
                    elif code == "international_student_ratio":
                        self.international_student_ratio = value
                    elif code == "international_student_diversity":
                        self.international_student_diversity = value
                    elif code == "faculty_student_ratio":
                        self.faculty_student_ratio = value
                        self.uploaded_learning_experience_files = (
                            json.loads(evidence) if evidence else []
                        )
                    elif code == "sustainability_metrics":
                        self.sustainability_metrics = value
                        self.uploaded_sustainability_files = (
                            json.loads(evidence) if evidence else []
                        )

    async def _ensure_static_data(self, session):
        """Helper to populate static ranking framework data if missing."""
        result = await session.execute(text("SELECT COUNT(*) FROM ranking_lenses"))
        if result.scalar() > 0:
            return
        lenses = [
            ("Research & Discovery", 50.0),
            ("Employability & Outcomes", 20.0),
            ("Global Engagement", 15.0),
            ("Learning Experience", 10.0),
            ("Sustainability", 5.0),
        ]
        lens_ids = {}
        for name, weight in lenses:
            res = await session.execute(
                text(
                    "INSERT INTO ranking_lenses (lens_name, total_weight_pct) VALUES (:name, :weight) RETURNING id"
                ),
                {"name": name, "weight": weight},
            )
            lens_ids[name] = res.scalar()
        indicators = [
            (
                lens_ids["Research & Discovery"],
                "Academic Reputation",
                "academic_reputation",
                30.0,
            ),
            (
                lens_ids["Research & Discovery"],
                "Citations per Faculty",
                "citations_per_faculty",
                20.0,
            ),
            (
                lens_ids["Employability & Outcomes"],
                "Employer Reputation",
                "employer_reputation",
                15.0,
            ),
            (
                lens_ids["Employability & Outcomes"],
                "Employment Outcomes",
                "employment_outcomes",
                5.0,
            ),
            (
                lens_ids["Global Engagement"],
                "International Research Network",
                "international_research_network",
                5.0,
            ),
            (
                lens_ids["Global Engagement"],
                "International Faculty Ratio",
                "international_faculty_ratio",
                5.0,
            ),
            (
                lens_ids["Global Engagement"],
                "International Student Ratio",
                "international_student_ratio",
                5.0,
            ),
            (
                lens_ids["Global Engagement"],
                "International Student Diversity",
                "international_student_diversity",
                0.0,
            ),
            (
                lens_ids["Learning Experience"],
                "Faculty-Student Ratio",
                "faculty_student_ratio",
                10.0,
            ),
            (
                lens_ids["Sustainability"],
                "Sustainability Metrics",
                "sustainability_metrics",
                5.0,
            ),
        ]
        for lens_id, name, code, weight in indicators:
            await session.execute(
                text(
                    "INSERT INTO ranking_indicators (lens_id, indicator_name, code, indicator_weight_pct) VALUES (:lid, :name, :code, :weight)"
                ),
                {"lid": lens_id, "name": name, "code": code, "weight": weight},
            )
        await session.commit()

    @rx.event(background=True)
    async def save_progress(self):
        """Save current dashboard state to the database, tracking the submitting user."""
        async with self:
            self.is_saving = True
        async with rx.asession() as session:
            async with self:
                from app.states.auth_state import AuthState

                hei_state = await self.get_state(HEIState)
                auth_state = await self.get_state(AuthState)
            if not hei_state.selected_hei:
                async with self:
                    self.is_saving = False
                    yield rx.toast("No institution selected.")
                return
            user_result = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": auth_state.email},
            )
            user_row = user_result.first()
            current_user_id = user_row[0] if user_row else None
            institution_id = int(hei_state.selected_hei["id"])
            scores_map = {
                "academic_reputation": (
                    self.academic_reputation,
                    self.uploaded_research_files,
                ),
                "citations_per_faculty": (self.citations_per_faculty, []),
                "employer_reputation": (
                    self.employer_reputation,
                    self.uploaded_employability_files,
                ),
                "employment_outcomes": (self.employment_outcomes, []),
                "international_research_network": (
                    self.international_research_network,
                    self.uploaded_global_engagement_files,
                ),
                "international_faculty_ratio": (self.international_faculty_ratio, []),
                "international_student_ratio": (self.international_student_ratio, []),
                "international_student_diversity": (
                    self.international_student_diversity,
                    [],
                ),
                "faculty_student_ratio": (
                    self.faculty_student_ratio,
                    self.uploaded_learning_experience_files,
                ),
                "sustainability_metrics": (
                    self.sustainability_metrics,
                    self.uploaded_sustainability_files,
                ),
            }
            ind_rows = await session.execute(
                text("SELECT code, id FROM ranking_indicators")
            )
            code_to_id = {row[0]: row[1] for row in ind_rows.all()}
            for code, (value, files) in scores_map.items():
                if code not in code_to_id:
                    continue
                indicator_id = code_to_id[code]
                files_json = json.dumps(files)
                await session.execute(
                    text("""
                        INSERT INTO institution_scores (institution_id, indicator_id, user_id, value, evidence_files, ranking_year)
                        VALUES (:inst_id, :ind_id, :user_id, :val, :files, 2025)
                        ON CONFLICT (institution_id, indicator_id, ranking_year)
                        DO UPDATE SET 
                            value = EXCLUDED.value, 
                            evidence_files = EXCLUDED.evidence_files, 
                            user_id = EXCLUDED.user_id,
                            updated_at = CURRENT_TIMESTAMP
                    """),
                    {
                        "inst_id": institution_id,
                        "ind_id": indicator_id,
                        "user_id": current_user_id,
                        "val": value,
                        "files": files_json,
                    },
                )
            await session.commit()
        async with self:
            self.is_saving = False
            yield rx.toast(
                "Assessment data saved successfully.",
                duration=3000,
                position="bottom-right",
                close_button=True,
            )