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
    status: str
    last_generated: str


class ReportsState(rx.State):
    reports: list[ReportItem] = [
        {
            "id": "1",
            "name": "Ateneo de Manila University",
            "overall_score": 85,
            "research_score": 82,
            "employability_score": 88,
            "status": "Completed",
            "last_generated": "2023-10-15",
        },
        {
            "id": "2",
            "name": "University of the Philippines Diliman",
            "overall_score": 88,
            "research_score": 90,
            "employability_score": 86,
            "status": "Completed",
            "last_generated": "2023-10-14",
        },
        {
            "id": "3",
            "name": "De La Salle University",
            "overall_score": 82,
            "research_score": 78,
            "employability_score": 86,
            "status": "Completed",
            "last_generated": "2023-10-16",
        },
        {
            "id": "4",
            "name": "University of Santo Tomas",
            "overall_score": 79,
            "research_score": 75,
            "employability_score": 83,
            "status": "In Progress",
            "last_generated": "-",
        },
        {
            "id": "5",
            "name": "Polytechnic University of the Philippines",
            "overall_score": 75,
            "research_score": 70,
            "employability_score": 80,
            "status": "In Progress",
            "last_generated": "-",
        },
        {
            "id": "6",
            "name": "Adamson University",
            "overall_score": 65,
            "research_score": 60,
            "employability_score": 70,
            "status": "Pending",
            "last_generated": "-",
        },
        {
            "id": "7",
            "name": "Mapúa University",
            "overall_score": 72,
            "research_score": 68,
            "employability_score": 76,
            "status": "In Progress",
            "last_generated": "-",
        },
        {
            "id": "8",
            "name": "Far Eastern University",
            "overall_score": 0,
            "research_score": 0,
            "employability_score": 0,
            "status": "Pending",
            "last_generated": "-",
        },
        {
            "id": "9",
            "name": "Asia Pacific College",
            "overall_score": 92,
            "research_score": 88,
            "employability_score": 96,
            "status": "Completed",
            "last_generated": "2023-10-18",
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
                    "Overall Score",
                    "Research Score",
                    "Employability Score",
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
                "Overall Score",
                "Research Score",
                "Employability Score",
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
                    report["status"],
                    report["last_generated"],
                ]
            )
        return rx.download(
            data=output.getvalue(),
            filename=f"all_institutions_report_{datetime.date.today()}.csv",
        )