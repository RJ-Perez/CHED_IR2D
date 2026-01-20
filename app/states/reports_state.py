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
from sqlalchemy import text

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
    reports: list[ReportItem] = []
    search_query: str = ""
    selected_report_id: str = ""
    selected_report_recommendations: list[dict[str, str]] = []
    is_generating_report_recommendations: bool = False

    def _parse_float(self, value: str) -> float:
        try:
            clean = "".join((c for c in value if c.isdigit() or c == "."))
            return float(clean) if clean else 0.0
        except (ValueError, TypeError) as e:
            logging.exception(f"Error parsing float value '{value}': {e}")
            return 0.0

    @rx.event(background=True)
    async def on_load(self):
        """Fetches all institutions and calculates their scores from database records."""
        async with rx.asession() as session:
            inst_result = await session.execute(
                text(
                    "SELECT id, institution_name FROM institutions ORDER BY institution_name ASC"
                )
            )
            institutions = inst_result.all()
            scores_result = await session.execute(
                text("""
                SELECT 
                    s.institution_id, 
                    i.code, 
                    s.value, 
                    s.evidence_files, 
                    s.updated_at
                FROM institution_scores s
                JOIN ranking_indicators i ON s.indicator_id = i.id
                WHERE s.ranking_year = 2025
                """)
            )
            all_scores = scores_result.all()
            inst_data = {}
            for inst_id, code, val, evidence, updated in all_scores:
                if inst_id not in inst_data:
                    inst_data[inst_id] = {
                        "scores": {},
                        "files": [],
                        "last_update": updated,
                    }
                inst_data[inst_id]["scores"][code] = val
                if evidence:
                    try:
                        files = json.loads(evidence)
                        if isinstance(files, list):
                            inst_data[inst_id]["files"].extend(files)
                    except Exception as e:
                        logging.exception(
                            f"Error parsing evidence files JSON for institution {inst_id}: {e}"
                        )
                        pass
                if updated and (
                    not inst_data[inst_id]["last_update"]
                    or updated > inst_data[inst_id]["last_update"]
                ):
                    inst_data[inst_id]["last_update"] = updated
            processed_reports = []
            for i_id, i_name in institutions:
                data = inst_data.get(
                    i_id, {"scores": {}, "files": [], "last_update": None}
                )
                scores = data["scores"]
                b_academic_rep = 90.0
                b_citations = 20.0
                b_emp_rep = 90.0
                b_emp_outcomes = 95.0
                b_int_research_net = 80.0
                b_int_faculty_ratio = 15.0
                b_int_student_ratio = 10.0
                b_faculty_student_ratio = 12.0
                b_sustainability = 85.0
                academic_rep = self._parse_float(scores.get("academic_reputation", "0"))
                citations = self._parse_float(scores.get("citations_per_faculty", "0"))
                emp_rep = self._parse_float(scores.get("employer_reputation", "0"))
                emp_outcomes = self._parse_float(scores.get("employment_outcomes", "0"))
                int_research_net = self._parse_float(
                    scores.get("international_research_network", "0")
                )
                int_faculty_ratio = self._parse_float(
                    scores.get("international_faculty_ratio", "0")
                )
                int_student_ratio = self._parse_float(
                    scores.get("international_student_ratio", "0")
                )
                faculty_student_ratio = self._parse_float(
                    scores.get("faculty_student_ratio", "0")
                )
                sustainability = self._parse_float(
                    scores.get("sustainability_metrics", "0")
                )
                s_academic_rep = (
                    min(100, academic_rep / b_academic_rep * 100)
                    if b_academic_rep
                    else 0
                )
                s_citations = (
                    min(100, citations / b_citations * 100) if b_citations else 0
                )
                s_emp_rep = min(100, emp_rep / b_emp_rep * 100) if b_emp_rep else 0
                s_emp_outcomes = (
                    min(100, emp_outcomes / b_emp_outcomes * 100)
                    if b_emp_outcomes
                    else 0
                )
                s_int_research_net = (
                    min(100, int_research_net / b_int_research_net * 100)
                    if b_int_research_net
                    else 0
                )
                s_int_faculty_ratio = (
                    min(100, int_faculty_ratio / b_int_faculty_ratio * 100)
                    if b_int_faculty_ratio
                    else 0
                )
                s_int_student_ratio = (
                    min(100, int_student_ratio / b_int_student_ratio * 100)
                    if b_int_student_ratio
                    else 0
                )
                s_faculty_student = min(100, faculty_student_ratio)
                s_sustainability = (
                    min(100, sustainability / b_sustainability * 100)
                    if b_sustainability
                    else 0
                )
                research_score = int(s_academic_rep * 0.6 + s_citations * 0.4)
                employability_score = int(s_emp_rep * 0.75 + s_emp_outcomes * 0.25)
                global_engagement_score = int(
                    (s_int_research_net + s_int_faculty_ratio + s_int_student_ratio) / 3
                )
                learning_experience_score = int(s_faculty_student)
                sustainability_score = int(s_sustainability)
                overall_score = int(
                    research_score * 0.5
                    + employability_score * 0.2
                    + global_engagement_score * 0.15
                    + learning_experience_score * 0.1
                    + sustainability_score * 0.05
                )
                indicators_count = len(scores.keys())
                status = "Pending"
                is_any_score_na = (
                    research_score == 0
                    or employability_score == 0
                    or global_engagement_score == 0
                    or (learning_experience_score == 0)
                    or (sustainability_score == 0)
                )
                if indicators_count >= 9:
                    status = "Completed"
                elif indicators_count > 0:
                    status = "In Progress"
                if is_any_score_na and indicators_count > 0:
                    status = "Incomplete"
                last_gen = (
                    data["last_update"].strftime("%Y-%m-%d")
                    if data["last_update"]
                    else "-"
                )
                processed_reports.append(
                    {
                        "id": str(i_id),
                        "name": i_name,
                        "overall_score": overall_score,
                        "research_score": research_score,
                        "employability_score": employability_score,
                        "global_engagement_score": global_engagement_score,
                        "learning_experience_score": learning_experience_score,
                        "sustainability_score": sustainability_score,
                        "status": status,
                        "last_generated": last_gen,
                        "evidence_files": list(set(data["files"])),
                    }
                )
            async with self:
                self.reports = processed_reports

    @rx.var(cache=True)
    def filtered_reports(self) -> list[ReportItem]:
        if not self.search_query:
            return self.reports
        query = self.search_query.lower()
        return [r for r in self.reports if query in r["name"].lower()]

    @rx.var(cache=True)
    def total_reports(self) -> int:
        return len(self.reports)

    @rx.var(cache=True)
    def completed_count(self) -> int:
        return len([r for r in self.reports if r["status"] == "Completed"])

    @rx.var(cache=True)
    def pending_count(self) -> int:
        return len([r for r in self.reports if r["status"] != "Completed"])

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query

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

    @rx.event
    def download_all_reports(self):
        """Generate and download CSV for all reports."""
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
            prompt = f"""You are an expert higher education consultant. Analyze the following performance data for {institution_name} in the Philippines and provide 3 strategic, actionable recommendations to improve their international ranking readiness.\n\n{performance_summary}\n\nFocus areas: {(", ".join(weak_areas) if weak_areas else "General Excellence")}\n\nProvide recommendations in JSON format with this structure:\n{{\n  "recommendations": [\n    {{\n      "title": "Short, actionable title (max 8 words)",\n      "description": "Detailed recommendation (2 sentences) explaining strategies specific to the metric",\n      "category": "Research & Discovery|Employability|Global Engagement|Learning Experience|Sustainability|Overall",\n      "priority": "High|Medium|Low"\n    }}\n  ]\n}}\n\nReturn ONLY valid JSON."""
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
                    is_rate_limit = (
                        "429" in error_str or "RESOURCE_EXHAUSTED" in error_str
                    )
                    if is_rate_limit:
                        if attempt == max_retries - 1:
                            logging.error(
                                "Google AI quota exhausted after all retries."
                            )
                            break
                        wait_time = 2.0 * 2**attempt
                        retry_match = re.search("retry in (\\d+(\\.\\d+)?)s", error_str)
                        if retry_match:
                            wait_time = float(retry_match.group(1)) + 1.0
                        wait_time = min(wait_time, 60.0)
                        logging.warning(
                            f"Rate limit hit. Retrying in {wait_time:.2f}s (Attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logging.exception(f"Non-retriable AI error: {e}")
                        break
            if not response_text:
                raise Exception("Failed to generate AI content after retries")
            json_match = re.search("\\{.*\\}", response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            recommendations_data = json.loads(response_text)
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
                    "title": "Boost Research Output",
                    "description": "Focus on increasing faculty publication rates in indexed journals to improve academic reputation and citations.",
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
                    "title": "Strengthen Industry Ties",
                    "description": "Expand partnership programs with key industry players to improve graduate employability and employer reputation scores.",
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
                    "title": "Maintain Performance",
                    "description": "Current metrics are strong. Focus on sustainability and long-term strategic planning to maintain leadership.",
                    "category": "Overall",
                    "priority": "Medium",
                    "icon": "bar-chart-2",
                    "color_class": "text-blue-600",
                    "bg_class": "bg-blue-50 border-blue-100",
                }
            )
        return recommendations