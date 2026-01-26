import reflex as rx
import asyncio
import json
import logging
from sqlalchemy import text
from app.states.hei_state import HEIState


class DashboardState(rx.State):
    """Manages data entry for the ranking readiness assessment.
    It tracks individual indicator scores and their associated evidence files.
    """

    academic_reputation: int = 0
    review_status: str = ""
    citations_per_faculty: int = 0
    employer_reputation: int = 0
    employment_outcomes: int = 0
    international_research_network: int = 0
    international_faculty_ratio: int = 0
    international_student_ratio: int = 0
    international_student_diversity: str = ""
    faculty_student_ratio: int = 0
    sustainability_metrics: int = 0
    uploaded_research_files: list[str] = []
    uploaded_employability_files: list[str] = []
    uploaded_global_engagement_files: list[str] = []
    uploaded_learning_experience_files: list[str] = []
    uploaded_sustainability_files: list[str] = []
    is_saving: bool = False
    is_uploading_research: bool = False
    is_uploading_employability: bool = False
    is_uploading_global_engagement: bool = False
    is_uploading_learning_experience: bool = False
    is_uploading_sustainability: bool = False
    upload_progress_research: int = 0
    upload_progress_employability: int = 0
    upload_progress_global_engagement: int = 0
    upload_progress_learning_experience: int = 0
    upload_progress_sustainability: int = 0
    upload_count_research: str = ""
    upload_count_employability: str = ""
    upload_count_global_engagement: str = ""
    upload_count_learning_experience: str = ""
    upload_count_sustainability: str = ""
    save_successful: bool = False
    validation_errors: dict[str, str] = {
        "academic_reputation": "",
        "citations_per_faculty": "",
        "employer_reputation": "",
        "employment_outcomes": "",
        "international_research_network": "",
        "international_faculty_ratio": "",
        "international_student_ratio": "",
        "faculty_student_ratio": "",
        "sustainability_metrics": "",
    }

    @rx.var(cache=True)
    def has_validation_errors(self) -> bool:
        """Checks if any field in validation_errors has a non-empty string."""
        for key in self.validation_errors.keys():
            if self.validation_errors[key]:
                return True
        return False

    @rx.var(cache=True)
    def academic_reputation_points(self) -> float:
        return round(float(self.academic_reputation) * 0.3, 1)

    @rx.var(cache=True)
    def citations_per_faculty_points(self) -> float:
        return round(float(self.citations_per_faculty) * 0.2, 1)

    @rx.var(cache=True)
    def research_section_total(self) -> float:
        return round(
            self.academic_reputation_points + self.citations_per_faculty_points, 1
        )

    @rx.var(cache=True)
    def employer_reputation_points(self) -> float:
        return round(float(self.employer_reputation) * 0.15, 1)

    @rx.var(cache=True)
    def employment_outcomes_points(self) -> float:
        return round(float(self.employment_outcomes) * 0.05, 1)

    @rx.var(cache=True)
    def employability_section_total(self) -> float:
        return round(
            self.employer_reputation_points + self.employment_outcomes_points, 1
        )

    @rx.var(cache=True)
    def international_research_network_points(self) -> float:
        return round(float(self.international_research_network) * 0.05, 1)

    @rx.var(cache=True)
    def international_faculty_ratio_points(self) -> float:
        return round(float(self.international_faculty_ratio) * 0.05, 1)

    @rx.var(cache=True)
    def international_student_ratio_points(self) -> float:
        return round(float(self.international_student_ratio) * 0.05, 1)

    @rx.var(cache=True)
    def global_engagement_section_total(self) -> float:
        return round(
            self.international_research_network_points
            + self.international_faculty_ratio_points
            + self.international_student_ratio_points,
            1,
        )

    @rx.var(cache=True)
    def faculty_student_ratio_points(self) -> float:
        return round(float(self.faculty_student_ratio) * 0.1, 1)

    @rx.var(cache=True)
    def learning_experience_section_total(self) -> float:
        return self.faculty_student_ratio_points

    @rx.var(cache=True)
    def sustainability_metrics_points(self) -> float:
        return round(float(self.sustainability_metrics) * 0.05, 1)

    @rx.var(cache=True)
    def sustainability_section_total(self) -> float:
        return self.sustainability_metrics_points

    @rx.var(cache=True)
    def progress(self) -> int:
        """Calculate completion progress based on filled fields."""
        metrics = [
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
        filled_count = len([m for m in metrics if m > 0])
        total_fields = 9
        return int(filled_count / total_fields * 100)

    def _validate_and_clamp(self, field_name: str, value: str) -> int:
        """Helper to convert string to int, clamp values, and set validation errors."""
        try:
            if not value:
                self.validation_errors[field_name] = ""
                return 0
            num_float = float(value)
            num = int(num_float)
            if num_float < 0 or num_float > 100:
                self.validation_errors[field_name] = "Value must be between 0 and 100"
            else:
                self.validation_errors[field_name] = ""
            return max(0, min(100, num))
        except (ValueError, TypeError) as e:
            logging.exception(f"Validation error for {field_name}: {e}")
            self.validation_errors[field_name] = "Please enter a valid number"
            return 0

    @rx.event
    def set_academic_reputation(self, value: str):
        self.academic_reputation = self._validate_and_clamp(
            "academic_reputation", value
        )

    @rx.event
    def set_citations_per_faculty(self, value: str):
        self.citations_per_faculty = self._validate_and_clamp(
            "citations_per_faculty", value
        )

    @rx.event
    def set_employer_reputation(self, value: str):
        self.employer_reputation = self._validate_and_clamp(
            "employer_reputation", value
        )

    @rx.event
    def set_employment_outcomes(self, value: str):
        self.employment_outcomes = self._validate_and_clamp(
            "employment_outcomes", value
        )

    @rx.event
    def set_international_research_network(self, value: str):
        self.international_research_network = self._validate_and_clamp(
            "international_research_network", value
        )

    @rx.event
    def set_international_faculty_ratio(self, value: str):
        self.international_faculty_ratio = self._validate_and_clamp(
            "international_faculty_ratio", value
        )

    @rx.event
    def set_international_student_ratio(self, value: str):
        self.international_student_ratio = self._validate_and_clamp(
            "international_student_ratio", value
        )

    @rx.event
    def set_international_student_diversity(self, value: str):
        self.international_student_diversity = value

    @rx.event
    def set_faculty_student_ratio(self, value: str):
        self.faculty_student_ratio = self._validate_and_clamp(
            "faculty_student_ratio", value
        )

    @rx.event
    def set_sustainability_metrics(self, value: str):
        self.sustainability_metrics = self._validate_and_clamp(
            "sustainability_metrics", value
        )

    async def _save_uploaded_file(
        self, file: rx.UploadFile, category: str
    ) -> str | None:
        """Helper to save files into institution-specific directories."""
        hei_state = await self.get_state(HEIState)
        if not hei_state.selected_hei:
            return None
        inst_id = hei_state.selected_hei["id"]
        relative_dir = f"institution_{inst_id}/{category}"
        upload_dir = rx.get_upload_dir() / relative_dir
        upload_dir.mkdir(parents=True, exist_ok=True)
        import random, string

        unique_name = (
            "".join(random.choices(string.ascii_letters + string.digits, k=6))
            + "_"
            + file.name
        )
        upload_data = await file.read()
        file_path = upload_dir / unique_name
        with file_path.open("wb") as f:
            f.write(upload_data)
        return f"{relative_dir}/{unique_name}"

    @rx.event
    async def handle_research_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for Research section with unique directory."""
        if not files:
            return
        self.is_uploading_research = True
        self.upload_progress_research = 0
        total = len(files)
        for i, file in enumerate(files):
            self.upload_count_research = f"{i + 1} of {total}"
            saved_path = await self._save_uploaded_file(file, "research")
            if saved_path:
                self.uploaded_research_files.append(saved_path)
            self.upload_progress_research = int((i + 1) / total * 100)
            yield
        self.is_uploading_research = False
        yield rx.clear_selected_files("upload_research")

    @rx.event
    async def handle_employability_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for Employability section with unique directory."""
        if not files:
            return
        self.is_uploading_employability = True
        self.upload_progress_employability = 0
        total = len(files)
        for i, file in enumerate(files):
            self.upload_count_employability = f"{i + 1} of {total}"
            saved_path = await self._save_uploaded_file(file, "employability")
            if saved_path:
                self.uploaded_employability_files.append(saved_path)
            self.upload_progress_employability = int((i + 1) / total * 100)
            yield
        self.is_uploading_employability = False
        yield rx.clear_selected_files("upload_employability")

    @rx.event
    async def handle_global_engagement_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for Global Engagement section with unique directory."""
        if not files:
            return
        self.is_uploading_global_engagement = True
        self.upload_progress_global_engagement = 0
        total = len(files)
        for i, file in enumerate(files):
            self.upload_count_global_engagement = f"{i + 1} of {total}"
            saved_path = await self._save_uploaded_file(file, "global_engagement")
            if saved_path:
                self.uploaded_global_engagement_files.append(saved_path)
            self.upload_progress_global_engagement = int((i + 1) / total * 100)
            yield
        self.is_uploading_global_engagement = False
        yield rx.clear_selected_files("upload_global_engagement")

    @rx.event
    async def handle_learning_experience_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for Learning Experience section with unique directory."""
        if not files:
            return
        self.is_uploading_learning_experience = True
        self.upload_progress_learning_experience = 0
        total = len(files)
        for i, file in enumerate(files):
            self.upload_count_learning_experience = f"{i + 1} of {total}"
            saved_path = await self._save_uploaded_file(file, "learning_experience")
            if saved_path:
                self.uploaded_learning_experience_files.append(saved_path)
            self.upload_progress_learning_experience = int((i + 1) / total * 100)
            yield
        self.is_uploading_learning_experience = False
        yield rx.clear_selected_files("upload_learning_experience")

    @rx.event
    async def handle_sustainability_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for Sustainability section with unique directory."""
        if not files:
            return
        self.is_uploading_sustainability = True
        self.upload_progress_sustainability = 0
        total = len(files)
        for i, file in enumerate(files):
            self.upload_count_sustainability = f"{i + 1} of {total}"
            saved_path = await self._save_uploaded_file(file, "sustainability")
            if saved_path:
                self.uploaded_sustainability_files.append(saved_path)
            self.upload_progress_sustainability = int((i + 1) / total * 100)
            yield
        self.is_uploading_sustainability = False
        yield rx.clear_selected_files("upload_sustainability")

    @rx.event
    def delete_research_file(self, filename: str):
        self.uploaded_research_files = [
            f for f in self.uploaded_research_files if f != filename
        ]

    @rx.event
    def delete_employability_file(self, filename: str):
        self.uploaded_employability_files = [
            f for f in self.uploaded_employability_files if f != filename
        ]

    @rx.event
    def delete_global_engagement_file(self, filename: str):
        self.uploaded_global_engagement_files = [
            f for f in self.uploaded_global_engagement_files if f != filename
        ]

    @rx.event
    def delete_learning_experience_file(self, filename: str):
        self.uploaded_learning_experience_files = [
            f for f in self.uploaded_learning_experience_files if f != filename
        ]

    @rx.event
    def delete_sustainability_file(self, filename: str):
        self.uploaded_sustainability_files = [
            f for f in self.uploaded_sustainability_files if f != filename
        ]

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
                    s.evidence_files,
                    s.review_status
                FROM institution_scores s
                JOIN ranking_indicators i ON s.indicator_id = i.id
                WHERE s.institution_id = :inst_id AND s.ranking_year = 2025
                """),
                {"inst_id": institution_id},
            )
            data = rows.all()
            async with self:
                for code, value, evidence, r_status in data:
                    if r_status:
                        self.review_status = r_status
                    if code == "academic_reputation":
                        try:
                            self.academic_reputation = int(float(value))
                        except (ValueError, TypeError) as e:
                            logging.exception(
                                f"Error loading academic reputation from DB: {e}"
                            )
                            self.academic_reputation = 0
                        self.uploaded_research_files = (
                            json.loads(evidence) if evidence else []
                        )
                    elif code == "citations_per_faculty":
                        try:
                            self.citations_per_faculty = int(float(value))
                        except (ValueError, TypeError) as e:
                            logging.exception(
                                f"Error loading citations per faculty from DB: {e}"
                            )
                            self.citations_per_faculty = 0
                    elif code == "employer_reputation":
                        try:
                            self.employer_reputation = int(float(value))
                        except (ValueError, TypeError) as e:
                            logging.exception(
                                f"Error loading employer reputation from DB: {e}"
                            )
                            self.employer_reputation = 0
                        self.uploaded_employability_files = (
                            json.loads(evidence) if evidence else []
                        )
                    elif code == "employment_outcomes":
                        try:
                            self.employment_outcomes = int(float(value))
                        except (ValueError, TypeError) as e:
                            logging.exception(
                                f"Error loading employment outcomes from DB: {e}"
                            )
                            self.employment_outcomes = 0
                    elif code == "international_research_network":
                        try:
                            self.international_research_network = int(float(value))
                        except (ValueError, TypeError) as e:
                            logging.exception(
                                f"Error loading international research network from DB: {e}"
                            )
                            self.international_research_network = 0
                        self.uploaded_global_engagement_files = (
                            json.loads(evidence) if evidence else []
                        )
                    elif code == "international_faculty_ratio":
                        try:
                            self.international_faculty_ratio = int(float(value))
                        except (ValueError, TypeError) as e:
                            logging.exception(
                                f"Error loading international faculty ratio from DB: {e}"
                            )
                            self.international_faculty_ratio = 0
                    elif code == "international_student_ratio":
                        try:
                            self.international_student_ratio = int(float(value))
                        except (ValueError, TypeError) as e:
                            logging.exception(
                                f"Error loading international student ratio from DB: {e}"
                            )
                            self.international_student_ratio = 0
                    elif code == "international_student_diversity":
                        self.international_student_diversity = value
                    elif code == "faculty_student_ratio":
                        try:
                            self.faculty_student_ratio = int(float(value))
                        except (ValueError, TypeError) as e:
                            logging.exception(
                                f"Error loading faculty student ratio from DB: {e}"
                            )
                            self.faculty_student_ratio = 0
                        self.uploaded_learning_experience_files = (
                            json.loads(evidence) if evidence else []
                        )
                    elif code == "sustainability_metrics":
                        try:
                            self.sustainability_metrics = int(float(value))
                        except (ValueError, TypeError) as e:
                            logging.exception(
                                f"Error loading sustainability metrics from DB: {e}"
                            )
                            self.sustainability_metrics = 0
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
            if self.has_validation_errors:
                yield rx.toast.error(
                    "Please correct the validation errors before saving."
                )
                return
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
            current_user_id = auth_state.authenticated_user_id
            institution_id = int(hei_state.selected_hei["id"])
            scores_map = {
                "academic_reputation": (
                    str(self.academic_reputation),
                    self.uploaded_research_files,
                ),
                "citations_per_faculty": (str(self.citations_per_faculty), []),
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
            self.save_successful = True
            yield rx.toast(
                "Assessment data saved successfully.",
                duration=3000,
                position="bottom-right",
                close_button=True,
            )