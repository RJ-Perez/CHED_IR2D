import reflex as rx
from typing import TypedDict, Any
import json
import logging
from sqlalchemy import text
from app.states.hei_state import HEIState
from app.states.auth_state import AuthState


class HistoricalState(rx.State):
    """Manages historical ranking data entry and analysis."""

    available_years: list[str] = [str(y) for y in range(2020, 2025)]
    selected_year: str = "2024"
    years_with_data: list[str] = []
    year_completion_map: dict[str, int] = {str(y): 0 for y in range(2020, 2025)}
    trend_data: list[dict[str, str | int]] = []
    academic_reputation: int = 0
    citations_per_faculty: int = 0
    employer_reputation: int = 0
    employment_outcomes: int = 0
    international_research_network: int = 0
    international_faculty_ratio: int = 0
    international_student_ratio: int = 0
    faculty_student_ratio: int = 0
    sustainability_metrics: int = 0
    uploaded_files: list[str] = []
    is_loading: bool = False
    is_saving: bool = False
    is_uploading: bool = False
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
        return any((v != "" for v in self.validation_errors.values()))

    @rx.event(background=True)
    async def on_load(self):
        """Optimized batch loading of all historical data with strict numeric initialization."""
        async with self:
            self.is_loading = True
            self.year_completion_map = {y: 0 for y in self.available_years}
            hei = await self.get_state(HEIState)
            if not hei.selected_hei:
                self.is_loading = False
                return
            inst_id = int(hei.selected_hei["id"])
            year = int(self.selected_year)
        async with rx.asession() as session:
            years_res = await session.execute(
                text("""
                SELECT ranking_year, 
                       (CASE WHEN academic_reputation > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN citations_per_faculty > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN employer_reputation > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN employment_outcomes > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN international_research_network > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN international_faculty_ratio > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN international_student_ratio > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN faculty_student_ratio > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN sustainability_metrics > 0 THEN 1 ELSE 0 END) as filled_count
                FROM historical_performance 
                WHERE institution_id = :iid
                """),
                {"iid": inst_id},
            )
            completion_rows = years_res.all()
            scores_res = await session.execute(
                text("""
                SELECT 
                    academic_reputation, citations_per_faculty, 
                    employer_reputation, employment_outcomes,
                    international_research_network, international_faculty_ratio, international_student_ratio,
                    faculty_student_ratio, sustainability_metrics,
                    evidence_files
                FROM historical_performance 
                WHERE institution_id = :iid AND ranking_year = :year
                """),
                {"iid": inst_id, "year": year},
            )
            all_hist_res = await session.execute(
                text("""
                SELECT 
                    ranking_year, 
                    academic_reputation, employer_reputation, 
                    sustainability_metrics, overall_score
                FROM historical_performance 
                WHERE institution_id = :iid
                ORDER BY ranking_year ASC
                """),
                {"iid": inst_id},
            )
            temp_completion_map = {y: 0 for y in self.available_years}
            temp_years_with_data = []
            for row in completion_rows:
                y_str = str(row[0])
                if y_str in temp_completion_map:
                    temp_completion_map[y_str] = int(row[1] / 9.0 * 100)
                    if row[1] > 0:
                        temp_years_with_data.append(y_str)
            score_row = scores_res.first()
            year_scores = {
                "academic_reputation": 0,
                "citations_per_faculty": 0,
                "employer_reputation": 0,
                "employment_outcomes": 0,
                "international_research_network": 0,
                "international_faculty_ratio": 0,
                "international_student_ratio": 0,
                "faculty_student_ratio": 0,
                "sustainability_metrics": 0,
                "uploaded_files": [],
            }
            if score_row:
                year_scores.update(
                    {
                        "academic_reputation": int(score_row[0] or 0),
                        "citations_per_faculty": int(score_row[1] or 0),
                        "employer_reputation": int(score_row[2] or 0),
                        "employment_outcomes": int(score_row[3] or 0),
                        "international_research_network": int(score_row[4] or 0),
                        "international_faculty_ratio": int(score_row[5] or 0),
                        "international_student_ratio": int(score_row[6] or 0),
                        "faculty_student_ratio": int(score_row[7] or 0),
                        "sustainability_metrics": int(score_row[8] or 0),
                        "uploaded_files": (
                            json.loads(score_row[9])
                            if isinstance(score_row[9], str)
                            else score_row[9]
                        )
                        or [],
                    }
                )
            chart_data = []
            for yr, ar, er, sm, ov in all_hist_res.all():
                chart_data.append(
                    {
                        "year": str(yr),
                        "academic_reputation": int(ar or 0),
                        "employer_reputation": int(er or 0),
                        "sustainability_metrics": int(sm or 0),
                        "Average": int(ov or 0),
                    }
                )
            async with self:
                self.years_with_data = temp_years_with_data
                self.year_completion_map = temp_completion_map
                self.academic_reputation = year_scores["academic_reputation"]
                self.citations_per_faculty = year_scores["citations_per_faculty"]
                self.employer_reputation = year_scores["employer_reputation"]
                self.employment_outcomes = year_scores["employment_outcomes"]
                self.international_research_network = year_scores[
                    "international_research_network"
                ]
                self.international_faculty_ratio = year_scores[
                    "international_faculty_ratio"
                ]
                self.international_student_ratio = year_scores[
                    "international_student_ratio"
                ]
                self.faculty_student_ratio = year_scores["faculty_student_ratio"]
                self.sustainability_metrics = year_scores["sustainability_metrics"]
                self.uploaded_files = year_scores["uploaded_files"]
                self.trend_data = chart_data
                self.is_loading = False

    @rx.var(cache=True)
    def years_count(self) -> int:
        return len(self.years_with_data)

    @rx.var(cache=True)
    def historical_coverage_pct(self) -> int:
        if not self.available_years:
            return 0
        return int(len(self.years_with_data) / len(self.available_years) * 100)

    @rx.var(cache=True)
    def selected_year_overall_score(self) -> int:
        for entry in self.trend_data:
            if str(entry.get("year")) == self.selected_year:
                return int(entry.get("Average", 0))
        return 0

    @rx.event(background=True)
    async def fetch_years_with_data(self):
        """Updates the completion map and years list from DB."""
        async with self:
            hei = await self.get_state(HEIState)
            if not hei.selected_hei:
                return
            inst_id = int(hei.selected_hei["id"])
        async with rx.asession() as session:
            result = await session.execute(
                text("""
                SELECT ranking_year, 
                       (CASE WHEN academic_reputation > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN citations_per_faculty > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN employer_reputation > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN employment_outcomes > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN international_research_network > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN international_faculty_ratio > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN international_student_ratio > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN faculty_student_ratio > 0 THEN 1 ELSE 0 END + 
                        CASE WHEN sustainability_metrics > 0 THEN 1 ELSE 0 END) as filled_count
                FROM historical_performance 
                WHERE institution_id = :iid
                """),
                {"iid": inst_id},
            )
            rows = result.all()
            completion_map = {y: 0 for y in self.available_years}
            years = []
            for row in rows:
                year_str = str(row[0])
                if year_str in completion_map:
                    pct = int(row[1] / 9.0 * 100)
                    completion_map[year_str] = pct
                    if row[1] > 0:
                        years.append(year_str)
            async with self:
                self.years_with_data = years
                self.year_completion_map = completion_map

    @rx.event(background=True)
    async def select_year(self, year: str):
        """Handles year selection with loading state."""
        async with self:
            if self.selected_year == year:
                return
            self.selected_year = year
            self.is_loading = True
            self.validation_errors = {k: "" for k in self.validation_errors.keys()}
        yield HistoricalState.fetch_scores_for_year

    @rx.event(background=True)
    async def fetch_scores_for_year(self):
        """Fetches score details for the current selected year."""
        async with self:
            hei = await self.get_state(HEIState)
            if not hei.selected_hei:
                self.is_loading = False
                return
            inst_id = int(hei.selected_hei["id"])
            year = int(self.selected_year)
        async with rx.asession() as session:
            result = await session.execute(
                text("""
                SELECT 
                    academic_reputation, citations_per_faculty, 
                    employer_reputation, employment_outcomes,
                    international_research_network, international_faculty_ratio, international_student_ratio,
                    faculty_student_ratio, sustainability_metrics,
                    evidence_files
                FROM historical_performance 
                WHERE institution_id = :iid AND ranking_year = :year
                """),
                {"iid": inst_id, "year": year},
            )
            row = result.first()
            scores_update = {
                "academic_reputation": 0,
                "citations_per_faculty": 0,
                "employer_reputation": 0,
                "employment_outcomes": 0,
                "international_research_network": 0,
                "international_faculty_ratio": 0,
                "international_student_ratio": 0,
                "faculty_student_ratio": 0,
                "sustainability_metrics": 0,
                "uploaded_files": [],
            }
            if row:
                scores_update.update(
                    {
                        "academic_reputation": int(row[0] or 0),
                        "citations_per_faculty": int(row[1] or 0),
                        "employer_reputation": int(row[2] or 0),
                        "employment_outcomes": int(row[3] or 0),
                        "international_research_network": int(row[4] or 0),
                        "international_faculty_ratio": int(row[5] or 0),
                        "international_student_ratio": int(row[6] or 0),
                        "faculty_student_ratio": int(row[7] or 0),
                        "sustainability_metrics": int(row[8] or 0),
                        "uploaded_files": (
                            json.loads(row[9]) if isinstance(row[9], str) else row[9]
                        )
                        or [],
                    }
                )
            async with self:
                self.academic_reputation = scores_update["academic_reputation"]
                self.citations_per_faculty = scores_update["citations_per_faculty"]
                self.employer_reputation = scores_update["employer_reputation"]
                self.employment_outcomes = scores_update["employment_outcomes"]
                self.international_research_network = scores_update[
                    "international_research_network"
                ]
                self.international_faculty_ratio = scores_update[
                    "international_faculty_ratio"
                ]
                self.international_student_ratio = scores_update[
                    "international_student_ratio"
                ]
                self.faculty_student_ratio = scores_update["faculty_student_ratio"]
                self.sustainability_metrics = scores_update["sustainability_metrics"]
                self.uploaded_files = scores_update["uploaded_files"]
                self.is_loading = False

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        self.is_uploading = True
        hei = await self.get_state(HEIState)
        inst_id = hei.selected_hei["id"] if hei.selected_hei else "unknown"
        year = self.selected_year
        upload_paths = []
        for file in files:
            relative_dir = f"historical_{inst_id}/{year}"
            upload_dir = rx.get_upload_dir() / relative_dir
            upload_dir.mkdir(parents=True, exist_ok=True)
            import random, string

            unique_name = f"{''.join(random.choices(string.ascii_letters + string.digits, k=6))}_{file.name}"
            data = await file.read()
            path = upload_dir / unique_name
            with path.open("wb") as f:
                f.write(data)
            upload_paths.append(f"{relative_dir}/{unique_name}")
        self.uploaded_files.extend(upload_paths)
        self.is_uploading = False
        yield rx.clear_selected_files("historical_upload")

    @rx.event
    def delete_file(self, filename: str):
        self.uploaded_files = [f for f in self.uploaded_files if f != filename]

    @rx.event(background=True)
    async def save_historical_scores(self):
        """Persist historical scores to DB and refresh metadata."""
        async with self:
            if self.has_validation_errors:
                yield rx.toast.error(
                    "Please correct the validation errors before saving."
                )
                return
            self.is_saving = True
            hei = await self.get_state(HEIState)
            auth = await self.get_state(AuthState)
            if not hei.selected_hei:
                self.is_saving = False
                return
            inst_id = int(hei.selected_hei["id"])
            user_id = auth.authenticated_user_id
            year = int(self.selected_year)
            acad_rep = float(self.academic_reputation)
            cit_fac = float(self.citations_per_faculty)
            research_score = acad_rep * 0.6 + cit_fac * 0.4
            emp_rep = float(self.employer_reputation)
            emp_out = float(self.employment_outcomes)
            emp_score = emp_rep * 0.75 + emp_out * 0.25
            irn = float(self.international_research_network)
            ifr = float(self.international_faculty_ratio)
            isr = float(self.international_student_ratio)
            global_score = (irn + ifr + isr) / 3.0
            fsr = float(self.faculty_student_ratio)
            learn_score = fsr
            sust = float(self.sustainability_metrics)
            sust_score = sust
            overall = (
                research_score * 0.5
                + emp_score * 0.2
                + global_score * 0.15
                + learn_score * 0.1
                + sust_score * 0.05
            )
            files_json = json.dumps(self.uploaded_files)
        async with rx.asession() as session:
            await session.execute(
                text("""
                INSERT INTO historical_performance (
                    institution_id, ranking_year, 
                    academic_reputation, citations_per_faculty, research_score,
                    employer_reputation, employment_outcomes, employability_score,
                    international_research_network, international_faculty_ratio, international_student_ratio, global_engagement_score,
                    faculty_student_ratio, learning_experience_score,
                    sustainability_metrics, sustainability_score,
                    overall_score,
                    evidence_files, user_id, updated_at, data_source
                ) VALUES (
                    :iid, :year,
                    :ar, :cf, :rs,
                    :er, :eo, :es,
                    :irn, :ifr, :isr, :gs,
                    :fsr, :ls,
                    :sm, :ss,
                    :ov,
                    :files, :uid, CURRENT_TIMESTAMP, 'Self-Assessment'
                )
                ON CONFLICT (institution_id, ranking_year)
                DO UPDATE SET 
                    academic_reputation = EXCLUDED.academic_reputation, 
                    citations_per_faculty = EXCLUDED.citations_per_faculty, 
                    research_score = EXCLUDED.research_score,
                    employer_reputation = EXCLUDED.employer_reputation, 
                    employment_outcomes = EXCLUDED.employment_outcomes, 
                    employability_score = EXCLUDED.employability_score,
                    international_research_network = EXCLUDED.international_research_network, 
                    international_faculty_ratio = EXCLUDED.international_faculty_ratio, 
                    international_student_ratio = EXCLUDED.international_student_ratio, 
                    global_engagement_score = EXCLUDED.global_engagement_score,
                    faculty_student_ratio = EXCLUDED.faculty_student_ratio, 
                    learning_experience_score = EXCLUDED.learning_experience_score,
                    sustainability_metrics = EXCLUDED.sustainability_metrics, 
                    sustainability_score = EXCLUDED.sustainability_score,
                    overall_score = EXCLUDED.overall_score,
                    evidence_files = EXCLUDED.evidence_files, 
                    user_id = EXCLUDED.user_id, 
                    updated_at = CURRENT_TIMESTAMP
                """),
                {
                    "iid": inst_id,
                    "year": year,
                    "ar": acad_rep,
                    "cf": cit_fac,
                    "rs": research_score,
                    "er": emp_rep,
                    "eo": emp_out,
                    "es": emp_score,
                    "irn": irn,
                    "ifr": ifr,
                    "isr": isr,
                    "gs": global_score,
                    "fsr": fsr,
                    "ls": learn_score,
                    "sm": sust,
                    "ss": sust_score,
                    "ov": overall,
                    "files": files_json,
                    "uid": user_id,
                },
            )
            await session.commit()
        async with self:
            self.is_saving = False
            yield rx.toast(f"Historical scores for {year} saved successfully!")
            yield HistoricalState.fetch_years_with_data

    @rx.event
    def set_academic_reputation(self, value: str):
        try:
            self.academic_reputation = int(float(value)) if value else 0
            self.validation_errors["academic_reputation"] = ""
        except:
            logging.exception("Unexpected error")
            self.validation_errors["academic_reputation"] = "Numeric required"

    @rx.event
    def set_citations_per_faculty(self, value: str):
        try:
            self.citations_per_faculty = int(float(value)) if value else 0
            self.validation_errors["citations_per_faculty"] = ""
        except:
            logging.exception("Unexpected error")
            self.validation_errors["citations_per_faculty"] = "Numeric required"

    @rx.event
    def set_employer_reputation(self, value: str):
        try:
            self.employer_reputation = int(float(value)) if value else 0
            self.validation_errors["employer_reputation"] = ""
        except:
            logging.exception("Unexpected error")
            self.validation_errors["employer_reputation"] = "Numeric required"

    @rx.event
    def set_employment_outcomes(self, value: str):
        try:
            self.employment_outcomes = int(float(value)) if value else 0
            self.validation_errors["employment_outcomes"] = ""
        except:
            logging.exception("Unexpected error")
            self.validation_errors["employment_outcomes"] = "Numeric required"

    @rx.event
    def set_international_research_network(self, value: str):
        try:
            self.international_research_network = int(float(value)) if value else 0
            self.validation_errors["international_research_network"] = ""
        except:
            logging.exception("Unexpected error")
            self.validation_errors["international_research_network"] = (
                "Numeric required"
            )

    @rx.event
    def set_international_faculty_ratio(self, value: str):
        try:
            self.international_faculty_ratio = int(float(value)) if value else 0
            self.validation_errors["international_faculty_ratio"] = ""
        except:
            logging.exception("Unexpected error")
            self.validation_errors["international_faculty_ratio"] = "Numeric required"

    @rx.event
    def set_international_student_ratio(self, value: str):
        try:
            self.international_student_ratio = int(float(value)) if value else 0
            self.validation_errors["international_student_ratio"] = ""
        except:
            logging.exception("Unexpected error")
            self.validation_errors["international_student_ratio"] = "Numeric required"

    @rx.event
    def set_faculty_student_ratio(self, value: str):
        try:
            self.faculty_student_ratio = int(float(value)) if value else 0
            self.validation_errors["faculty_student_ratio"] = ""
        except:
            logging.exception("Unexpected error")
            self.validation_errors["faculty_student_ratio"] = "Numeric required"

    @rx.event
    def set_sustainability_metrics(self, value: str):
        try:
            self.sustainability_metrics = int(float(value)) if value else 0
            self.validation_errors["sustainability_metrics"] = ""
        except:
            logging.exception("Unexpected error")
            self.validation_errors["sustainability_metrics"] = "Numeric required"