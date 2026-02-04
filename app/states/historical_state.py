import reflex as rx
from typing import TypedDict, Any
import json
import logging
from sqlalchemy import text
from app.states.hei_state import HEIState
from app.states.auth_state import AuthState


class HistoricalScore(TypedDict):
    year: int
    indicator_code: str
    value: str
    evidence_files: list[str]


class HistoricalState(rx.State):
    """Manages historical ranking data entry and storage for past years (2020-2024)."""

    selected_year: str = "2024"
    available_years: list[str] = ["2020", "2021", "2022", "2023", "2024"]
    years_with_data: list[str] = []
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
    is_uploading: bool = False
    is_loading: bool = False
    is_saving: bool = False
    all_years_data: dict[str, dict[str, int]] = {}
    trend_data: list[dict[str, str | int | float]] = []
    year_completion_map: dict[str, int] = {
        "2020": 0,
        "2021": 0,
        "2022": 0,
        "2023": 0,
        "2024": 0,
    }
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
    def set_faculty_student_ratio(self, value: str):
        self.faculty_student_ratio = self._validate_and_clamp(
            "faculty_student_ratio", value
        )

    @rx.event
    def set_sustainability_metrics(self, value: str):
        self.sustainability_metrics = self._validate_and_clamp(
            "sustainability_metrics", value
        )

    @rx.var(cache=True)
    def overall_completion_pct(self) -> int:
        if not self.available_years:
            return 0
        total_pct = sum(self.year_completion_map.values())
        return int(total_pct / len(self.available_years))

    @rx.event(background=True)
    async def on_load(self):
        """Batch loading of all historical data to minimize round-trips and state updates."""
        async with self:
            self.is_loading = True
        yield HistoricalState.fetch_years_with_data
        yield HistoricalState.fetch_scores_for_year
        yield HistoricalState.fetch_all_historical_data
        async with self:
            self.is_loading = False

    @rx.var(cache=True)
    def best_performing_year(self) -> str:
        if not self.trend_data:
            return "N/A"
        best_year = ""
        max_score = -1
        for entry in self.trend_data:
            score = entry.get("Average", 0)
            if score > max_score:
                max_score = score
                best_year = str(entry["year"])
        return best_year

    @rx.var(cache=True)
    def years_count(self) -> int:
        return len(self.years_with_data)

    @rx.var(cache=True)
    def missing_years(self) -> list[str]:
        return [y for y in self.available_years if y not in self.years_with_data]

    @rx.var(cache=True)
    def historical_coverage_pct(self) -> int:
        if not self.available_years:
            return 0
        return int(len(self.years_with_data) / len(self.available_years) * 100)

    @rx.var(cache=True)
    def first_incomplete_year(self) -> str:
        for year in sorted(self.available_years):
            if year not in self.years_with_data:
                return year
        return ""

    @rx.var(cache=True)
    def overall_improvement(self) -> float:
        if len(self.trend_data) < 2:
            return 0.0
        first = self.trend_data[0].get("Average", 0)
        last = self.trend_data[-1].get("Average", 0)
        if first == 0:
            return 0.0
        return round((last - first) / first * 100, 1)

    @rx.event(background=True)
    async def fetch_all_historical_data(self):
        async with self:
            hei = await self.get_state(HEIState)
            if not hei.selected_hei:
                return
            inst_id = int(hei.selected_hei["id"])
        async with rx.asession() as session:
            result = await session.execute(
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
            rows = result.all()
            chart_data = []
            if rows:
                for year, ar, er, sm, ov in rows:
                    chart_data.append(
                        {
                            "year": str(year),
                            "academic_reputation": int(ar or 0),
                            "employer_reputation": int(er or 0),
                            "sustainability_metrics": int(sm or 0),
                            "Average": int(ov or 0),
                        }
                    )
            else:
                old_res = await session.execute(
                    text("""
                    SELECT ranking_year, indicator_code, value 
                    FROM historical_scores 
                    WHERE institution_id = :iid
                    ORDER BY ranking_year ASC
                    """),
                    {"iid": inst_id},
                )
                data_by_year = {}
                for year, code, val in old_res.all():
                    y_str = str(year)
                    if y_str not in data_by_year:
                        data_by_year[y_str] = {}
                    try:
                        data_by_year[y_str][code] = int(float(val))
                    except (ValueError, TypeError) as e:
                        logging.exception(f"Error parsing historical score: {e}")
                        data_by_year[y_str][code] = 0
                for year in sorted(data_by_year.keys()):
                    entry = {"year": year, **data_by_year[year]}
                    scores = list(data_by_year[year].values())
                    if scores:
                        entry["Average"] = int(sum(scores) / len(scores))
                    chart_data.append(entry)
            async with self:
                self.trend_data = chart_data

    async def _ensure_historical_table(self):
        async with rx.asession() as session:
            await session.execute(
                text("""
                CREATE TABLE IF NOT EXISTS historical_performance (
                    id SERIAL PRIMARY KEY,
                    institution_id INTEGER NOT NULL,
                    ranking_year INTEGER NOT NULL,

                    -- Research & Discovery (50%)
                    academic_reputation DECIMAL(10, 2) DEFAULT 0,
                    citations_per_faculty DECIMAL(10, 2) DEFAULT 0,
                    research_score DECIMAL(10, 2) DEFAULT 0,

                    -- Employability & Outcomes (20%)
                    employer_reputation DECIMAL(10, 2) DEFAULT 0,
                    employment_outcomes DECIMAL(10, 2) DEFAULT 0,
                    employability_score DECIMAL(10, 2) DEFAULT 0,

                    -- Global Engagement (15%)
                    international_research_network DECIMAL(10, 2) DEFAULT 0,
                    international_faculty_ratio DECIMAL(10, 2) DEFAULT 0,
                    international_student_ratio DECIMAL(10, 2) DEFAULT 0,
                    global_engagement_score DECIMAL(10, 2) DEFAULT 0,

                    -- Learning Experience (10%)
                    faculty_student_ratio DECIMAL(10, 2) DEFAULT 0,
                    learning_experience_score DECIMAL(10, 2) DEFAULT 0,

                    -- Sustainability (5%)
                    sustainability_metrics DECIMAL(10, 2) DEFAULT 0,
                    sustainability_score DECIMAL(10, 2) DEFAULT 0,

                    overall_score DECIMAL(10, 2) DEFAULT 0,

                    -- Metadata
                    evidence_files JSONB DEFAULT '[]',
                    notes TEXT,
                    data_source VARCHAR(50) DEFAULT 'Self-Assessment',
                    verified BOOLEAN DEFAULT FALSE,
                    user_id INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

                    UNIQUE(institution_id, ranking_year)
                )
            """)
            )
            await session.commit()
            count_check = await session.execute(
                text("SELECT COUNT(*) FROM historical_performance")
            )
            if count_check.scalar() == 0:
                old_table_check = await session.execute(
                    text("SELECT to_regclass('public.historical_scores')")
                )
                if old_table_check.scalar() is not None:
                    rows = await session.execute(
                        text(
                            "SELECT DISTINCT institution_id, ranking_year FROM historical_scores"
                        )
                    )
                    pairs = rows.all()
                    for inst_id, year in pairs:
                        scores_res = await session.execute(
                            text(
                                "SELECT indicator_code, value FROM historical_scores WHERE institution_id = :iid AND ranking_year = :yr"
                            ),
                            {"iid": inst_id, "yr": year},
                        )
                        scores_map = {
                            row[0]: float(row[1])
                            if row[1] and row[1].replace(".", "", 1).isdigit()
                            else 0.0
                            for row in scores_res.all()
                        }
                        acad_rep = scores_map.get("academic_reputation", 0)
                        cit_fac = scores_map.get("citations_per_faculty", 0)
                        research_score = acad_rep * 0.6 + cit_fac * 0.4
                        emp_rep = scores_map.get("employer_reputation", 0)
                        emp_out = scores_map.get("employment_outcomes", 0)
                        emp_score = emp_rep * 0.75 + emp_out * 0.25
                        irn = scores_map.get("international_research_network", 0)
                        ifr = scores_map.get("international_faculty_ratio", 0)
                        isr = scores_map.get("international_student_ratio", 0)
                        global_score = (irn + ifr + isr) / 3
                        fsr = scores_map.get("faculty_student_ratio", 0)
                        learn_score = fsr
                        sust = scores_map.get("sustainability_metrics", 0)
                        sust_score = sust
                        overall = (
                            research_score * 0.5
                            + emp_score * 0.2
                            + global_score * 0.15
                            + learn_score * 0.1
                            + sust_score * 0.05
                        )
                        await session.execute(
                            text("""
                            INSERT INTO historical_performance (
                                institution_id, ranking_year, 
                                academic_reputation, citations_per_faculty, research_score,
                                employer_reputation, employment_outcomes, employability_score,
                                international_research_network, international_faculty_ratio, international_student_ratio, global_engagement_score,
                                faculty_student_ratio, learning_experience_score,
                                sustainability_metrics, sustainability_score,
                                overall_score, data_source
                            ) VALUES (
                                :iid, :yr,
                                :ar, :cf, :rs,
                                :er, :eo, :es,
                                :irn, :ifr, :isr, :gs,
                                :fsr, :ls,
                                :sm, :ss,
                                :ov, 'Historical Import'
                            )
                            """),
                            {
                                "iid": inst_id,
                                "yr": year,
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
                            },
                        )
                    await session.commit()

    @rx.event(background=True)
    async def fetch_years_with_data(self):
        async with self:
            hei = await self.get_state(HEIState)
            if not hei.selected_hei:
                return
            inst_id = int(hei.selected_hei["id"])
        async with rx.asession() as session:
            result = await session.execute(
                text("""
                SELECT ranking_year, 
                       COUNT(*) filter (WHERE academic_reputation > 0) + 
                       COUNT(*) filter (WHERE citations_per_faculty > 0) + 
                       COUNT(*) filter (WHERE employer_reputation > 0) + 
                       COUNT(*) filter (WHERE employment_outcomes > 0) + 
                       COUNT(*) filter (WHERE international_research_network > 0) + 
                       COUNT(*) filter (WHERE international_faculty_ratio > 0) + 
                       COUNT(*) filter (WHERE international_student_ratio > 0) + 
                       COUNT(*) filter (WHERE faculty_student_ratio > 0) + 
                       COUNT(*) filter (WHERE sustainability_metrics > 0) as filled_count
                FROM historical_performance 
                WHERE institution_id = :iid
                GROUP BY ranking_year
            """),
                {"iid": inst_id},
            )
            rows = result.all()
            completion_map = {y: 0 for y in self.available_years}
            years = []
            for row in rows:
                year_str = str(row[0])
                years.append(year_str)
                completion_map[year_str] = int(row[1] / 9 * 100)
            async with self:
                self.years_with_data = years
                self.year_completion_map = completion_map
        async with rx.asession() as session:
            result = await session.execute(
                text("""
                SELECT DISTINCT ranking_year FROM historical_performance WHERE institution_id = :iid
                UNION 
                SELECT DISTINCT ranking_year FROM historical_scores WHERE institution_id = :iid
                ORDER BY ranking_year DESC
            """),
                {"iid": inst_id},
            )
            rows = result.all()
            async with self:
                self.years_with_data = [str(row[0]) for row in rows]

    @rx.event(background=True)
    async def select_year(self, year: str):
        """Handles year selection with clear loading state feedback."""
        async with self:
            if self.selected_year == year:
                return
            self.selected_year = year
            self.is_loading = True
        async with self:
            for k in self.validation_errors.keys():
                self.validation_errors[k] = ""
        yield HistoricalState.fetch_scores_for_year

    @rx.event(background=True)
    async def fetch_scores_for_year(self):
        async with self:
            self.is_loading = True
            hei = await self.get_state(HEIState)
            if not hei.selected_hei:
                self.is_loading = False
                return
            inst_id = int(hei.selected_hei["id"])
            year = int(self.selected_year)
        async with self:
            self.academic_reputation = 0
            self.citations_per_faculty = 0
            self.employer_reputation = 0
            self.employment_outcomes = 0
            self.international_research_network = 0
            self.international_faculty_ratio = 0
            self.international_student_ratio = 0
            self.faculty_student_ratio = 0
            self.sustainability_metrics = 0
            self.uploaded_files = []
            for k in self.validation_errors.keys():
                self.validation_errors[k] = ""
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
            async with self:
                if row:
                    self.academic_reputation = int(row[0] or 0)
                    self.citations_per_faculty = int(row[1] or 0)
                    self.employer_reputation = int(row[2] or 0)
                    self.employment_outcomes = int(row[3] or 0)
                    self.international_research_network = int(row[4] or 0)
                    self.international_faculty_ratio = int(row[5] or 0)
                    self.international_student_ratio = int(row[6] or 0)
                    self.faculty_student_ratio = int(row[7] or 0)
                    self.sustainability_metrics = int(row[8] or 0)
                    if row[9]:
                        self.uploaded_files = (
                            json.loads(row[9]) if isinstance(row[9], str) else row[9]
                        )
                else:
                    old_res = await session.execute(
                        text("""
                        SELECT indicator_code, value, evidence_files 
                        FROM historical_scores 
                        WHERE institution_id = :iid AND ranking_year = :year
                        """),
                        {"iid": inst_id, "year": year},
                    )
                    rows = old_res.all()
                    all_files = []
                    for r in rows:
                        code, val, files_json = r
                        try:
                            num_val = int(float(val))
                        except (ValueError, TypeError) as e:
                            logging.exception(f"Error parsing score value '{val}': {e}")
                            num_val = 0
                        if code == "academic_reputation":
                            self.academic_reputation = num_val
                        elif code == "citations_per_faculty":
                            self.citations_per_faculty = num_val
                        elif code == "employer_reputation":
                            self.employer_reputation = num_val
                        elif code == "employment_outcomes":
                            self.employment_outcomes = num_val
                        elif code == "international_research_network":
                            self.international_research_network = num_val
                        elif code == "international_faculty_ratio":
                            self.international_faculty_ratio = num_val
                        elif code == "international_student_ratio":
                            self.international_student_ratio = num_val
                        elif code == "faculty_student_ratio":
                            self.faculty_student_ratio = num_val
                        elif code == "sustainability_metrics":
                            self.sustainability_metrics = num_val
                        if files_json:
                            f_list = (
                                json.loads(files_json)
                                if isinstance(files_json, str)
                                else files_json
                            )
                            all_files.extend(f_list)
                    self.uploaded_files = list(set(all_files))
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
            global_score = (irn + ifr + isr) / 3
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
                    academic_reputation = EXCLUDED.academic_reputation, citations_per_faculty = EXCLUDED.citations_per_faculty, research_score = EXCLUDED.research_score,
                    employer_reputation = EXCLUDED.employer_reputation, employment_outcomes = EXCLUDED.employment_outcomes, employability_score = EXCLUDED.employability_score,
                    international_research_network = EXCLUDED.international_research_network, international_faculty_ratio = EXCLUDED.international_faculty_ratio, international_student_ratio = EXCLUDED.international_student_ratio, global_engagement_score = EXCLUDED.global_engagement_score,
                    faculty_student_ratio = EXCLUDED.faculty_student_ratio, learning_experience_score = EXCLUDED.learning_experience_score,
                    sustainability_metrics = EXCLUDED.sustainability_metrics, sustainability_score = EXCLUDED.sustainability_score,
                    overall_score = EXCLUDED.overall_score,
                    evidence_files = EXCLUDED.evidence_files, user_id = EXCLUDED.user_id, updated_at = CURRENT_TIMESTAMP
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