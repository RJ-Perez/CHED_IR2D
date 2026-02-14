import reflex as rx
from typing import TypedDict
import datetime
import io
import csv
import json
import logging
import os
import re
import asyncio
import time
from sqlalchemy import text

REPORT_AI_CACHE = {}
REPORT_CACHE_TTL = 3600
try:
    from google import genai
    from google.genai import types

    GOOGLE_AI_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_AI_AVAILABLE = bool(GOOGLE_AI_API_KEY)
except ImportError as e:
    logging.exception(f"google-genai package not installed: {e}")
    GOOGLE_AI_AVAILABLE = False
except Exception as e:
    logging.exception(f"Error configuring Google AI: {e}")
    GOOGLE_AI_AVAILABLE = False


class ReportItem(TypedDict):
    id: str
    name: str
    overall_score: int
    research_score: int
    employability_score: int
    global_engagement_score: int
    learning_experience_score: int
    sustainability_score: int
    status: str
    last_generated: str
    evidence_files: list[str]


class ReportsState(rx.State):
    delete_confirm_id: str = ""
    delete_confirm_name: str = ""
    show_delete_modal: bool = False
    show_reset_modal: bool = False
    is_resetting: bool = False
    reports: list[ReportItem] = []
    search_query: str = ""
    selected_report_id: str = ""
    is_loading: bool = False
    selected_report_recommendations: list[dict[str, str]] = []
    is_generating_report_recommendations: bool = False
    show_review_modal: bool = False
    page_size: int = 10
    current_page: int = 1
    is_loading_page: bool = False
    selected_review_report: ReportItem = {
        "id": "",
        "name": "",
        "overall_score": 0,
        "research_score": 0,
        "employability_score": 0,
        "global_engagement_score": 0,
        "learning_experience_score": 0,
        "sustainability_score": 0,
        "status": "",
        "last_generated": "",
        "evidence_files": [],
    }
    review_comments: str = ""
    is_saving_review: bool = False

    def _clean_json_response(self, text: str) -> str:
        """Sanitizes AI response text to ensure it is valid parseable JSON.
        Handles markdown blocks, control characters in strings, and single-quoted keys.
        """
        if not text:
            return ""
        text = re.sub("[a-zA-Z]*\\n?", "", text)
        text = re.sub("", "", text)
        text = text.strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start : end + 1]
        text = re.sub(",(\\s*[}\\]])", "\\1", text)
        text = re.sub("'([^']+)'\\s*:", '"\\1":', text)

        @rx.event
        def escape_string_content(match):
            content = match.group(1)
            content = (
                content.replace(
                    """
""",
                    "\\n",
                )
                .replace("\r", "\\r")
                .replace("\t", "\\t")
            )
            return f'"{content}"'

        text = re.sub('"([^"\\\\]*(?:\\\\.[^"\\\\]*)*)"', escape_string_content, text)
        return text

    def _parse_float(self, value) -> float:
        """Parse a value to float, handling strings, ints, floats, and None."""
        try:
            if value is None:
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            value_str = str(value)
            clean = "".join((c for c in value_str if c.isdigit() or c == "."))
            return float(clean) if clean else 0.0
        except (ValueError, TypeError) as e:
            logging.exception(f"Error parsing float value '{value}': {e}")
            return 0.0

    @rx.event(background=True)
    async def on_load(self):
        """Optimized report fetching with 2-minute caching and simplified logic."""
        from app.utils.db_utils import get_cached_reports, set_cached_reports

        async with self:
            cached = get_cached_reports()
            if cached:
                self.reports = cached
                self.is_loading = False
                return
            self.is_loading = True
        try:
            async with rx.asession() as session:
                await session.execute(
                    text("""
                    CREATE TABLE IF NOT EXISTS institution_reviews (
                        id SERIAL PRIMARY KEY, institution_id INTEGER NOT NULL, 
                        status VARCHAR(50) NOT NULL, reviewer_name VARCHAR(255), comments TEXT
                    )
                """)
                )
                await session.commit()
                result = await session.execute(
                    text("""
                    SELECT 
                        i.id as inst_id, i.institution_name, MAX(s.updated_at) as last_update,
                        MAX(s.review_status) as status,
                        COALESCE(
                            json_object_agg(ri.code, s.value) FILTER (WHERE ri.code IS NOT NULL),
                            '{}'::json
                        ) as scores_map,
                        COALESCE(
                            json_agg(s.evidence_files) FILTER (WHERE s.evidence_files IS NOT NULL),
                            '[]'::json
                        ) as evidence_list
                    FROM institutions i
                    LEFT JOIN institution_scores s ON i.id = s.institution_id AND s.ranking_year = 2025
                    LEFT JOIN ranking_indicators ri ON s.indicator_id = ri.id
                    GROUP BY i.id, i.institution_name
                    ORDER BY i.institution_name ASC LIMIT 100
                """)
                )
                processed_reports = []
                for (
                    inst_id,
                    name,
                    last_update,
                    db_status,
                    scores,
                    evidence,
                ) in result.all():
                    scores = scores or {}
                    evidence_list = []
                    if evidence:
                        for ev in evidence:
                            if ev:
                                try:
                                    evidence_list.extend(json.loads(ev))
                                except:
                                    logging.exception("Unexpected error")
                    b_map = {
                        "academic_reputation": 90.0,
                        "citations_per_faculty": 20.0,
                        "employer_reputation": 90.0,
                        "employment_outcomes": 95.0,
                        "international_research_network": 80.0,
                        "international_faculty_ratio": 15.0,
                        "international_student_ratio": 10.0,
                        "faculty_student_ratio": 12.0,
                        "sustainability_metrics": 85.0,
                    }
                    c = {
                        k: min(100, self._parse_float(scores.get(k, 0)) / b * 100)
                        if b
                        else 0
                        for k, b in b_map.items()
                    }
                    res = int(
                        c["academic_reputation"] * 0.6
                        + c["citations_per_faculty"] * 0.4
                    )
                    emp = int(
                        c["employer_reputation"] * 0.75
                        + c["employment_outcomes"] * 0.25
                    )
                    gl_eng = int(
                        (
                            c["international_research_network"]
                            + c["international_faculty_ratio"]
                            + c["international_student_ratio"]
                        )
                        / 3
                    )
                    over = int(
                        res * 0.5
                        + emp * 0.2
                        + gl_eng * 0.15
                        + int(c["faculty_student_ratio"]) * 0.1
                        + int(c["sustainability_metrics"]) * 0.05
                    )
                    final_status = (
                        db_status
                        if db_status in ["Reviewed", "Declined", "For Review"]
                        else "Pending"
                    )
                    if final_status == "Pending" and over > 0:
                        final_status = (
                            "For Review" if len(scores) >= 9 else "In Progress"
                        )
                    processed_reports.append(
                        {
                            "id": str(inst_id),
                            "name": name,
                            "overall_score": over,
                            "research_score": res,
                            "employability_score": emp,
                            "global_engagement_score": gl_eng,
                            "learning_experience_score": int(
                                c["faculty_student_ratio"]
                            ),
                            "sustainability_score": int(c["sustainability_metrics"]),
                            "status": final_status,
                            "last_generated": last_update.strftime("%Y-%m-%d")
                            if last_update
                            else "-",
                            "evidence_files": list(set(evidence_list)),
                        }
                    )
                set_cached_reports(processed_reports)
                async with self:
                    self.reports = processed_reports
        except Exception as e:
            logging.exception(f"Error fetching reports: {e}")
        finally:
            async with self:
                self.is_loading = False

    @rx.var(cache=True)
    def filtered_reports(self) -> list[ReportItem]:
        if not self.search_query:
            return self.reports
        query = self.search_query.lower()
        return [r for r in self.reports if query in r["name"].lower()]

    @rx.var(cache=True)
    def total_pages(self) -> int:
        total = len(self.filtered_reports)
        if total == 0:
            return 1
        return (total + self.page_size - 1) // self.page_size

    @rx.var(cache=True)
    def paginated_reports(self) -> list[ReportItem]:
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        return self.filtered_reports[start:end]

    @rx.event
    def set_page_size(self, value: str):
        self.page_size = int(value)
        self.current_page = 1

    @rx.event(background=True)
    async def next_page(self):
        async with self:
            if self.current_page < self.total_pages:
                self.current_page += 1
                self.is_loading_page = True
        await asyncio.sleep(0.2)
        async with self:
            self.is_loading_page = False

    @rx.event(background=True)
    async def prev_page(self):
        async with self:
            if self.current_page > 1:
                self.current_page -= 1
                self.is_loading_page = True
        await asyncio.sleep(0.2)
        async with self:
            self.is_loading_page = False

    @rx.var(cache=True)
    def total_reports(self) -> int:
        return len(self.reports)

    @rx.var(cache=True)
    def for_review_count(self) -> int:
        return len([r for r in self.reports if r["status"] == "For Review"])

    @rx.var(cache=True)
    def reviewed_count(self) -> int:
        return len([r for r in self.reports if r["status"] == "Reviewed"])

    @rx.var(cache=True)
    def in_progress_count(self) -> int:
        """Returns count of reports that are In Progress (Not Reviewed, Declined, or Completed)."""
        return len([r for r in self.reports if r["status"] == "In Progress"])

    @rx.var(cache=True)
    def pending_count(self) -> int:
        """Returns count of reports that are Pending (No data entered or all zeros)."""
        return len([r for r in self.reports if r["status"] == "Pending"])

    @rx.var(cache=True)
    def status_distribution_data(self) -> list[dict[str, str | int]]:
        """Calculates data for the status distribution pie chart."""
        counts = {
            "For Review": self.for_review_count,
            "Reviewed": self.reviewed_count,
            "In Progress": self.in_progress_count,
            "Pending": self.pending_count,
        }
        colors = {
            "For Review": "#3b82f6",
            "Reviewed": "#10b981",
            "In Progress": "#f59e0b",
            "Pending": "#64748b",
        }
        return [
            {"name": status, "value": count, "fill": colors.get(status, "#cbd5e1")}
            for status, count in counts.items()
            if count > 0 or len(self.reports) == 0
        ]

    @rx.var(cache=True)
    def status_distribution_percentages(self) -> list[dict[str, str | int]]:
        """Returns status distribution data with pre-calculated rounded percentages for display."""
        total = self.total_reports
        counts = {
            "For Review": self.for_review_count,
            "Reviewed": self.reviewed_count,
            "In Progress": self.in_progress_count,
            "Pending": self.pending_count,
        }
        colors = {
            "For Review": "#3b82f6",
            "Reviewed": "#10b981",
            "In Progress": "#f59e0b",
            "Pending": "#64748b",
        }
        results = []
        for status, count in counts.items():
            if count > 0 or total == 0:
                percentage = "0"
                if total > 0:
                    percentage = str(int(round(count / total * 100)))
                results.append(
                    {
                        "name": status,
                        "value": count,
                        "percentage": f"{percentage}%",
                        "fill": colors.get(status, "#cbd5e1"),
                    }
                )
        return results

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query

    @rx.event
    def set_review_comments(self, value: str):
        self.review_comments = value

    @rx.event
    def open_review_modal(self, report_id: str):
        report = next((r for r in self.reports if r["id"] == report_id), None)
        if report:
            self.selected_review_report = report
            self.review_comments = ""
            self.show_review_modal = True

    @rx.event
    def close_review_modal(self):
        self.show_review_modal = False

    @rx.event(background=True)
    async def process_review(self, status: str):
        """Process Approve/Decline review using RAW SQL and migrate data to history table."""
        async with self:
            self.is_saving_review = True
            report_id = self.selected_review_report["id"]
            comments = self.review_comments
            from app.states.auth_state import AuthState

            auth_state = await self.get_state(AuthState)
            user_id = auth_state.authenticated_user_id
        async with rx.asession() as session:
            reviewer_name = "System Administrator"
            if user_id:
                user_res = await session.execute(
                    text("SELECT first_name, last_name FROM users WHERE id = :uid"),
                    {"uid": user_id},
                )
                user_row = user_res.first()
                if user_row:
                    reviewer_name = f"{user_row[0]} {user_row[1]}"
            await session.execute(
                text("""
                    UPDATE institution_scores 
                    SET review_status = :status, 
                        review_comments = :comments,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE institution_id = :inst_id AND ranking_year = 2025
                """),
                {"status": status, "comments": comments, "inst_id": int(report_id)},
            )
            await session.execute(
                text("""
                    INSERT INTO institution_reviews (
                        institution_id, 
                        status, 
                        reviewer_name, 
                        comments
                    ) VALUES (
                        :inst_id, 
                        :status, 
                        :reviewer_name, 
                        :comments
                    )
                """),
                {
                    "inst_id": int(report_id),
                    "status": status,
                    "reviewer_name": reviewer_name,
                    "comments": comments,
                },
            )
            await session.commit()
        async with self:
            self.is_saving_review = False
            self.show_review_modal = False
            yield ReportsState.on_load
            yield rx.toast(
                f"Institution assessment has been {status.lower()} and archived.",
                duration=3000,
            )

    @rx.event
    def download_report(self, report_id: str):
        """Generate and download CSV for a single report."""
        report = next((r for r in self.reports if r["id"] == report_id), None)
        if report:
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(
                [
                    "Institution",
                    "Overall Readiness Score",
                    "Research & Discovery (50%)",
                    "Employability & Outcomes (20%)",
                    "Global Engagement (15%)",
                    "Learning Experience (10%)",
                    "Sustainability (5%)",
                    "Status",
                    "Last Generated",
                ]
            )
            writer.writerow(
                [
                    report["name"],
                    report["overall_score"],
                    report["research_score"],
                    report["employability_score"],
                    report["global_engagement_score"],
                    report["learning_experience_score"],
                    report["sustainability_score"],
                    report["status"],
                    datetime.date.today().isoformat(),
                ]
            )
            return rx.download(
                data=output.getvalue(),
                filename=f"report_{report['id']}_{datetime.date.today()}.csv",
            )
        return rx.toast("Report not found", duration=3000)

    @rx.event(background=True)
    async def download_all_reports(self):
        """Generate and download CSV for all reports with historical context."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Institution",
                "2025 Overall Readiness",
                "Research & Discovery (50%)",
                "Employability & Outcomes (20%)",
                "Global Engagement (15%)",
                "Learning Experience (10%)",
                "Sustainability (5%)",
                "Historical Records Found",
                "Status",
                "Last Generated",
            ]
        )
        async with rx.asession() as session:
            hist_res = await session.execute(
                text(
                    "SELECT institution_id, COUNT(DISTINCT ranking_year) FROM historical_scores GROUP BY institution_id"
                )
            )
            hist_counts = {str(row[0]): row[1] for row in hist_res.all()}
        async with self:
            for report in self.reports:
                writer.writerow(
                    [
                        report["name"],
                        report["overall_score"],
                        report["research_score"],
                        report["employability_score"],
                        report["global_engagement_score"],
                        report["learning_experience_score"],
                        report["sustainability_score"],
                        hist_counts.get(report["id"], 0),
                        report["status"],
                        report["last_generated"],
                    ]
                )
        return rx.download(
            data=output.getvalue(),
            filename=f"all_institutions_report_{datetime.date.today()}.csv",
        )

    @rx.event
    def confirm_delete_report(self, report_id: str, report_name: str):
        """Open delete confirmation modal."""
        self.delete_confirm_id = report_id
        self.delete_confirm_name = report_name
        self.show_delete_modal = True

    @rx.event
    def cancel_delete_report(self):
        """Close delete confirmation modal."""
        self.show_delete_modal = False
        self.delete_confirm_id = ""
        self.delete_confirm_name = ""

    @rx.event
    def delete_report(self):
        """Delete report from reports list."""
        if not self.delete_confirm_id:
            return
        report_id = self.delete_confirm_id
        report_name = self.delete_confirm_name
        self.reports = [r for r in self.reports if r["id"] != report_id]
        self.show_delete_modal = False
        self.delete_confirm_id = ""
        self.delete_confirm_name = ""
        return rx.toast(
            f"Report for '{report_name}' has been deleted successfully.",
            duration=3000,
            position="top-center",
        )

    @rx.event
    def confirm_reset_assessment(self):
        self.show_reset_modal = True

    @rx.event
    def cancel_reset_assessment(self):
        self.show_reset_modal = False

    @rx.event(background=True)
    async def reset_all_assessments(self):
        """Wipes all numerical scores from DB and deletes all evidence files from disk."""
        async with self:
            self.is_resetting = True
        try:
            import shutil

            upload_dir = rx.get_upload_dir()
            if upload_dir.exists():
                for item in upload_dir.iterdir():
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
            async with rx.asession() as session:
                await session.execute(text("DELETE FROM institution_scores"))
                await session.commit()
            yield ReportsState.on_load
            async with self:
                self.show_reset_modal = False
                yield rx.toast(
                    "System Reset Complete: All scores and evidence files have been purged.",
                    duration=5000,
                    position="top-center",
                )
        except Exception as e:
            logging.exception(f"Error during system reset: {e}")
            yield rx.toast(
                "An error occurred during reset. Please check logs.", duration=5000
            )
        finally:
            async with self:
                self.is_resetting = False

    @rx.event(background=True)
    async def select_report_for_analysis(self, report_id: str):
        """Selects a report and triggers recommendation generation."""
        async with self:
            self.selected_report_id = report_id
            self.selected_report_recommendations = []
            if not report_id:
                return
        report = next((r for r in self.reports if r["id"] == report_id), None)
        if not report:
            return
        yield ReportsState.generate_report_recommendations(report)

    @rx.event(background=True)
    async def generate_report_recommendations(self, report: dict):
        """Generate AI recommendations for a specific report."""
        async with self:
            self.is_generating_report_recommendations = True
        report_id = report["id"]
        now = time.time()
        if report_id in REPORT_AI_CACHE:
            cache_entry = REPORT_AI_CACHE[report_id]
            if now - cache_entry["timestamp"] < REPORT_CACHE_TTL:
                logging.info(f"Using cached report AI analysis for {report_id}")
                async with self:
                    self.selected_report_recommendations = cache_entry[
                        "recommendations"
                    ]
                    self.is_generating_report_recommendations = False
                return
        research_score = report["research_score"]
        employability_score = report["employability_score"]
        global_engagement_score = report["global_engagement_score"]
        learning_experience_score = report["learning_experience_score"]
        sustainability_score = report["sustainability_score"]
        overall_score = report["overall_score"]
        institution_name = report["name"]
        if not GOOGLE_AI_AVAILABLE:
            async with self:
                self.selected_report_recommendations = (
                    self._get_fallback_recommendations(
                        research_score,
                        employability_score,
                        global_engagement_score,
                        learning_experience_score,
                        sustainability_score,
                    )
                )
                self.is_generating_report_recommendations = False
            return
        try:
            performance_summary = f"\nAnalysis for {institution_name}:\n- Overall Readiness Score: {overall_score}/100\n- Research & Discovery: {research_score}/100\n- Employability: {employability_score}/100\n- Global Engagement: {global_engagement_score}/100\n- Learning Experience: {learning_experience_score}/100\n- Sustainability: {sustainability_score}/100\n"
            weak_areas = []
            if research_score < 70:
                weak_areas.append("Research")
            if employability_score < 70:
                weak_areas.append("Employability")
            if global_engagement_score < 70:
                weak_areas.append("Global Engagement")
            if learning_experience_score < 70:
                weak_areas.append("Learning Experience")
            if sustainability_score < 70:
                weak_areas.append("Sustainability")
            prompt = f"""You are an expert higher education consultant. Analyze the following performance data for {institution_name} and provide 3 strategic, actionable recommendations to improve their overall readiness.\n\n{performance_summary}\n\nFocus areas: {(", ".join(weak_areas) if weak_areas else "General Excellence")}\n\nProvide recommendations in JSON format with this structure:\n{{\n  "recommendations": [\n    {{\n      "title": "Short, actionable title (max 8 words)",\n      "description": "Detailed recommendation explaining specific improvements for the institution.",\n      "category": "Research & Discovery|Employability|Global Engagement|Learning Experience|Sustainability|Overall",\n      "priority": "High|Medium|Low"\n    }}\n  ]\n}}\n\nReturn ONLY valid JSON."""
            client = genai.Client(api_key=GOOGLE_AI_API_KEY)
            max_retries = 5
            response_text = ""
            for attempt in range(max_retries):
                try:
                    response = await client.aio.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        ),
                    )
                    if response and response.text:
                        response_text = response.text
                        break
                    else:
                        logging.warning(
                            f"Attempt {attempt + 1}: Empty response from Google AI"
                        )
                except Exception as e:
                    error_str = str(e)
                    is_retriable = (
                        "429" in error_str
                        or "RESOURCE_EXHAUSTED" in error_str
                        or "503" in error_str
                        or ("UNAVAILABLE" in error_str)
                    )
                    if is_retriable:
                        if attempt == max_retries - 1:
                            logging.info(
                                "Google AI quota exhausted after all retries. Using report fallback logic."
                            )
                            break
                        wait_time = 2.0 * 2**attempt
                        retry_match = re.search("retry in (\\d+(\\.\\d+)?)s", error_str)
                        if retry_match:
                            wait_time = float(retry_match.group(1)) + 1.0
                        wait_time = min(wait_time, 60.0)
                        logging.warning(
                            f"Google AI error (Rate limit or Unavailable). Retrying in {wait_time:.2f}s (Attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logging.exception(f"Non-retriable AI error: {e}")
                        break
            if not response_text:
                raise Exception("Failed to generate AI content after retries")
            response_text = self._clean_json_response(response_text)
            if not response_text:
                raise Exception("Cleaned AI response is empty")
            try:
                recommendations_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logging.exception(
                    f"Failed to parse Report AI JSON: {e}. Cleaned text: {response_text[:200]}..."
                )
                raise e
            recommendations = []
            for rec in recommendations_data.get("recommendations", []):
                category = rec.get("category", "Overall")
                if "Research" in category:
                    icon = "microscope"
                    color_class = "text-purple-600"
                    bg_class = "bg-purple-50 border-purple-100"
                elif "Employability" in category:
                    icon = "briefcase"
                    color_class = "text-emerald-600"
                    bg_class = "bg-emerald-50 border-emerald-100"
                elif "Global" in category:
                    icon = "globe"
                    color_class = "text-blue-600"
                    bg_class = "bg-blue-50 border-blue-100"
                elif "Learning" in category:
                    icon = "graduation-cap"
                    color_class = "text-indigo-600"
                    bg_class = "bg-indigo-50 border-indigo-100"
                elif "Sustainability" in category:
                    icon = "leaf"
                    color_class = "text-green-600"
                    bg_class = "bg-green-50 border-green-100"
                else:
                    icon = "lightbulb"
                    color_class = "text-amber-600"
                    bg_class = "bg-amber-50 border-amber-100"
                recommendations.append(
                    {
                        "title": rec.get("title", "Strategic Insight"),
                        "description": rec.get("description", ""),
                        "category": category,
                        "priority": rec.get("priority", "Medium"),
                        "icon": icon,
                        "color_class": color_class,
                        "bg_class": bg_class,
                    }
                )
            REPORT_AI_CACHE[report_id] = {
                "timestamp": time.time(),
                "recommendations": recommendations,
            }
            async with self:
                self.selected_report_recommendations = recommendations
                self.is_generating_report_recommendations = False
        except Exception as e:
            logging.exception(f"Error generating report recommendations: {e}")
            async with self:
                self.selected_report_recommendations = (
                    self._get_fallback_recommendations(
                        research_score,
                        employability_score,
                        global_engagement_score,
                        learning_experience_score,
                        sustainability_score,
                    )
                )
                self.is_generating_report_recommendations = False

    def _get_fallback_recommendations(
        self,
        research_score: int,
        employability_score: int,
        global_engagement_score: int,
        learning_experience_score: int,
        sustainability_score: int,
    ) -> list[dict[str, str]]:
        """Generate fallback recommendations for reports."""
        recommendations = []
        if research_score < 75:
            recommendations.append(
                {
                    "title": "Increase Scopus Citations",
                    "description": "Research & Discovery accounts for 50% of the QS score. Prioritize publishing in Scopus-indexed journals to drive up 'Citations per Faculty' and enhance 'Academic Reputation'.",
                    "category": "Research & Discovery",
                    "priority": "High",
                    "icon": "microscope",
                    "color_class": "text-purple-600",
                    "bg_class": "bg-purple-50 border-purple-100",
                }
            )
        if employability_score < 75:
            recommendations.append(
                {
                    "title": "Boost Employer Reputation",
                    "description": "Expand industry partnerships to improve 'Employer Reputation' (15% weight) and systematically track alumni career progression for 'Employment Outcomes'.",
                    "category": "Employability",
                    "priority": "High",
                    "icon": "briefcase",
                    "color_class": "text-emerald-600",
                    "bg_class": "bg-emerald-50 border-emerald-100",
                }
            )
        if not recommendations:
            recommendations.append(
                {
                    "title": "Sustain QS Excellence",
                    "description": "Current performance is strong. Continue to monitor 'Faculty Student Ratio' and 'International Research Network' metrics to maintain your QS ranking competitiveness.",
                    "category": "Overall",
                    "priority": "Medium",
                    "icon": "bar-chart-2",
                    "color_class": "text-blue-600",
                    "bg_class": "bg-blue-50 border-blue-100",
                }
            )
        return recommendations