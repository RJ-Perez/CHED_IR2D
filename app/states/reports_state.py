import reflex as rx
from typing import TypedDict
import datetime
import io
import csv


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
    reports: list[ReportItem] = [
        {
            "id": "1",
            "name": "Ateneo de Manila University",
            "overall_score": 85,
            "research_score": 82,
            "employability_score": 88,
            "global_engagement_score": 85,
            "learning_experience_score": 80,
            "sustainability_score": 90,
            "status": "Completed",
            "last_generated": "2023-10-15",
            "evidence_files": [
                "institution_1/research/annual_report_2023.pdf",
                "institution_1/employability/employer_survey.pdf",
                "institution_1/sustainability/esg_compliance.pdf",
            ],
        },
        {
            "id": "2",
            "name": "University of the Philippines Diliman",
            "overall_score": 88,
            "research_score": 90,
            "employability_score": 86,
            "global_engagement_score": 88,
            "learning_experience_score": 85,
            "sustainability_score": 85,
            "status": "Completed",
            "last_generated": "2023-10-14",
            "evidence_files": [
                "institution_2/research/research_portfolio.pdf",
                "institution_2/global_engagement/moa_international.pdf",
            ],
        },
        {
            "id": "3",
            "name": "De La Salle University",
            "overall_score": 82,
            "research_score": 78,
            "employability_score": 86,
            "global_engagement_score": 80,
            "learning_experience_score": 82,
            "sustainability_score": 85,
            "status": "Completed",
            "last_generated": "2023-10-16",
            "evidence_files": [],
        },
        {
            "id": "4",
            "name": "University of Santo Tomas",
            "overall_score": 79,
            "research_score": 75,
            "employability_score": 83,
            "global_engagement_score": 75,
            "learning_experience_score": 78,
            "sustainability_score": 80,
            "status": "In Progress",
            "last_generated": "-",
            "evidence_files": [],
        },
        {
            "id": "5",
            "name": "Polytechnic University of the Philippines",
            "overall_score": 75,
            "research_score": 70,
            "employability_score": 80,
            "global_engagement_score": 72,
            "learning_experience_score": 75,
            "sustainability_score": 78,
            "status": "In Progress",
            "last_generated": "-",
            "evidence_files": [],
        },
        {
            "id": "6",
            "name": "Adamson University",
            "overall_score": 65,
            "research_score": 60,
            "employability_score": 70,
            "global_engagement_score": 65,
            "learning_experience_score": 65,
            "sustainability_score": 70,
            "status": "Pending",
            "last_generated": "-",
            "evidence_files": [],
        },
        {
            "id": "7",
            "name": "Mapúa University",
            "overall_score": 72,
            "research_score": 68,
            "employability_score": 76,
            "global_engagement_score": 70,
            "learning_experience_score": 72,
            "sustainability_score": 75,
            "status": "In Progress",
            "last_generated": "-",
            "evidence_files": [],
        },
        {
            "id": "8",
            "name": "Far Eastern University",
            "overall_score": 0,
            "research_score": 0,
            "employability_score": 0,
            "global_engagement_score": 0,
            "learning_experience_score": 0,
            "sustainability_score": 0,
            "status": "Pending",
            "last_generated": "-",
            "evidence_files": [],
        },
        {
            "id": "9",
            "name": "Asia Pacific College",
            "overall_score": 92,
            "research_score": 88,
            "employability_score": 96,
            "global_engagement_score": 92,
            "learning_experience_score": 90,
            "sustainability_score": 95,
            "status": "Completed",
            "last_generated": "2023-10-18",
            "evidence_files": [],
        },
    ]
    search_query: str = ""

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