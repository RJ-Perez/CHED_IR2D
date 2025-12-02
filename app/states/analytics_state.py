import reflex as rx
from app.states.dashboard_state import DashboardState
import random
import logging


class AnalyticsState(rx.State):
    research_score: int = 0
    employability_score: int = 0
    overall_score: int = 0
    research_comparison_data: list[dict[str, str | int | float]] = []
    employability_comparison_data: list[dict[str, str | int | float]] = []
    ncr_average_color: str = "#94a3b8"
    target_color: str = "#10b981"
    your_color: str = "#2563eb"

    @rx.event
    async def on_load(self):
        """Calculate scores and prepare chart data based on DashboardState inputs."""
        dashboard_state = await self.get_state(DashboardState)

        @rx.event
        def parse_float(value: str) -> float:
            try:
                clean = "".join((c for c in value if c.isdigit() or c == "."))
                return float(clean) if clean else 0.0
            except ValueError as e:
                logging.exception(f"Error parsing float: {e}")
                return 0.0

        r_output = parse_float(dashboard_state.research_output)
        citations = parse_float(dashboard_state.citations)
        grants = parse_float(dashboard_state.grants)
        emp_rate = parse_float(dashboard_state.employment_rate)
        emp_rep = parse_float(dashboard_state.employer_reputation)
        b_r_output = 1500.0
        b_citations = 20.0
        b_emp_rate = 95.0
        b_emp_rep = 90.0
        s_r_output = min(100, r_output / b_r_output * 100) if b_r_output else 0
        s_citations = min(100, citations / b_citations * 100) if b_citations else 0
        s_emp_rate = min(100, emp_rate / b_emp_rate * 100) if b_emp_rate else 0
        s_emp_rep = min(100, emp_rep / b_emp_rep * 100) if b_emp_rep else 0
        self.research_score = int(s_r_output * 0.6 + s_citations * 0.4)
        self.employability_score = int(s_emp_rate * 0.5 + s_emp_rep * 0.5)
        self.overall_score = int((self.research_score + self.employability_score) / 2)
        self.research_comparison_data = [
            {
                "metric": "Publications",
                "You": r_output,
                "NCR Avg": 450,
                "Target": b_r_output,
            },
            {
                "metric": "Citations",
                "You": citations,
                "NCR Avg": 4.5,
                "Target": b_citations,
            },
        ]
        self.employability_comparison_data = [
            {
                "metric": "Emp. Rate (%)",
                "You": emp_rate,
                "NCR Avg": 82.0,
                "Target": b_emp_rate,
            },
            {
                "metric": "Reputation",
                "You": emp_rep,
                "NCR Avg": 45.0,
                "Target": b_emp_rep,
            },
        ]