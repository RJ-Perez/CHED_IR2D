import reflex as rx
from typing import TypedDict
import datetime
import io
import csv
import json
import logging
from sqlalchemy import text


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

    @rx.var
    def filtered_reports(self) -> list[ReportItem]:
        if not self.search_query:
            return self.reports
        query = self.search_query.lower()
        return [r for r in self.reports if query in r["name"].lower()]

    @rx.var
    def total_reports(self) -> int:
        return len(self.reports)

    @rx.var
    def completed_count(self) -> int:
        return len([r for r in self.reports if r["status"] == "Completed"])

    @rx.var
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