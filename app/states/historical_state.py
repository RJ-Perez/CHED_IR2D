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

    @rx.event(background=True)
    async def on_load(self):
        async with self:
            self.is_loading = True
        await self._ensure_historical_table()
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
                SELECT ranking_year, indicator_code, value 
                FROM historical_scores 
                WHERE institution_id = :iid
                ORDER BY ranking_year ASC
                """),
                {"iid": inst_id},
            )
            rows = result.all()
            data_by_year = {}
            for year, code, val in rows:
                y_str = str(year)
                if y_str not in data_by_year:
                    data_by_year[y_str] = {}
                try:
                    data_by_year[y_str][code] = int(float(val))
                except (ValueError, TypeError) as e:
                    logging.exception(f"Error parsing historical value: {e}")
                    data_by_year[y_str][code] = 0
            chart_data = []
            for year in sorted(data_by_year.keys()):
                entry = {"year": year, **data_by_year[year]}
                scores = list(data_by_year[year].values())
                if scores:
                    entry["Average"] = int(sum(scores) / len(scores))
                chart_data.append(entry)
            async with self:
                self.all_years_data = data_by_year
                self.trend_data = chart_data

    async def _ensure_historical_table(self):
        async with rx.asession() as session:
            result = await session.execute(
                text("SELECT to_regclass('public.historical_scores')")
            )
            if result.scalar() is None:
                await session.execute(
                    text("""
                    CREATE TABLE historical_scores (
                        id SERIAL PRIMARY KEY,
                        institution_id INTEGER NOT NULL,
                        ranking_year INTEGER NOT NULL,
                        indicator_code VARCHAR(100) NOT NULL,
                        value VARCHAR(255),
                        evidence_files JSONB DEFAULT '[]',
                        user_id INTEGER,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(institution_id, ranking_year, indicator_code)
                    )
                """)
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
                SELECT DISTINCT ranking_year FROM historical_scores 
                WHERE institution_id = :iid ORDER BY ranking_year DESC
            """),
                {"iid": inst_id},
            )
            rows = result.all()
            async with self:
                self.years_with_data = [str(row[0]) for row in rows]

    @rx.event(background=True)
    async def set_selected_year(self, year: str):
        async with self:
            self.selected_year = year
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
        async with rx.asession() as session:
            result = await session.execute(
                text("""
                SELECT indicator_code, value, evidence_files 
                FROM historical_scores 
                WHERE institution_id = :iid AND ranking_year = :year
            """),
                {"iid": inst_id, "year": year},
            )
            rows = result.all()
            async with self:
                all_files = []
                for row in rows:
                    code, val, files_json = row
                    try:
                        num_val = int(float(val))
                    except (ValueError, TypeError) as e:
                        logging.exception(f"Error parsing value {val}: {e}")
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
            self.is_saving = True
            hei = await self.get_state(HEIState)
            auth = await self.get_state(AuthState)
            if not hei.selected_hei:
                self.is_saving = False
                return
            inst_id = int(hei.selected_hei["id"])
            user_id = auth.authenticated_user_id
            year = int(self.selected_year)
            scores_map = {
                "academic_reputation": self.academic_reputation,
                "citations_per_faculty": self.citations_per_faculty,
                "employer_reputation": self.employer_reputation,
                "employment_outcomes": self.employment_outcomes,
                "international_research_network": self.international_research_network,
                "international_faculty_ratio": self.international_faculty_ratio,
                "international_student_ratio": self.international_student_ratio,
                "faculty_student_ratio": self.faculty_student_ratio,
                "sustainability_metrics": self.sustainability_metrics,
            }
            files_json = json.dumps(self.uploaded_files)
        async with rx.asession() as session:
            for code, val in scores_map.items():
                await session.execute(
                    text("""
                    INSERT INTO historical_scores (institution_id, ranking_year, indicator_code, value, evidence_files, user_id)
                    VALUES (:iid, :year, :code, :val, :files, :uid)
                    ON CONFLICT (institution_id, ranking_year, indicator_code)
                    DO UPDATE SET value = EXCLUDED.value, evidence_files = EXCLUDED.evidence_files, updated_at = CURRENT_TIMESTAMP
                """),
                    {
                        "iid": inst_id,
                        "year": year,
                        "code": code,
                        "val": str(val),
                        "files": files_json,
                        "uid": user_id,
                    },
                )
            await session.commit()
        async with self:
            self.is_saving = False
            yield rx.toast(f"Historical scores for {year} saved successfully!")
            yield HistoricalState.fetch_years_with_data