from cmd import PROMPT
import reflex as rx
from app.states.dashboard_state import DashboardState
import random
import logging
import json

try:
    import google.generativeai as genai

    GOOGLE_AI_API_KEY = "AIzaSyB4N7w-PVlY8ZkVxYkEkQyL9qgBTsLfIr8"
    genai.configure(api_key=GOOGLE_AI_API_KEY)
    PROMPT = """
    You are an expert higher education consultant specializing in international university rankings (QS and THE). 

Analyze the following performance data for a Higher Education Institution in the Philippines and provide 3-4 strategic, actionable recommendations to improve their international ranking readiness.

{performance_summary}

Areas needing improvement: {', '.join(weak_areas) if weak_areas else 'All areas are performing well'}
Provide Readiness Score for each category and overall score.
"""
    GOOGLE_AI_AVAILABLE = True
except ImportError as e:
    logging.exception(f"google-generativeai package not installed: {e}")
    GOOGLE_AI_AVAILABLE = False
except Exception as e:
    logging.exception(f"Error configuring Google AI: {e}")
    GOOGLE_AI_AVAILABLE = False


class AnalyticsState(rx.State):
    research_score: int = 0
    employability_score: int = 0
    global_engagement_score: int = 0
    learning_experience_score: int = 0
    sustainability_score: int = 0
    overall_score: int = 0
    research_comparison_data: list[dict[str, str | int | float]] = []
    employability_comparison_data: list[dict[str, str | int | float]] = []
    global_engagement_comparison_data: list[dict[str, str | int | float]] = []
    learning_experience_comparison_data: list[dict[str, str | int | float]] = []
    sustainability_comparison_data: list[dict[str, str | int | float]] = []
    ai_recommendations: list[dict[str, str]] = []
    is_generating_recommendations: bool = False
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

        academic_rep = parse_float(dashboard_state.academic_reputation)
        citations = parse_float(dashboard_state.citations_per_faculty)
        emp_rep = parse_float(dashboard_state.employer_reputation)
        emp_outcomes = parse_float(dashboard_state.employment_outcomes)
        int_research_net = parse_float(dashboard_state.international_research_network)
        int_faculty_ratio = parse_float(dashboard_state.international_faculty_ratio)
        int_student_ratio = parse_float(dashboard_state.international_student_ratio)
        faculty_student_ratio = parse_float(dashboard_state.faculty_student_ratio)
        sustainability = parse_float(dashboard_state.sustainability_metrics)
        b_academic_rep = 90.0
        b_citations = 20.0
        b_emp_rep = 90.0
        b_emp_outcomes = 95.0
        b_int_research_net = 80.0
        b_int_faculty_ratio = 15.0
        b_int_student_ratio = 10.0
        b_faculty_student_ratio = 12.0
        b_sustainability = 85.0
        s_academic_rep = (
            min(100, academic_rep / b_academic_rep * 100) if b_academic_rep else 0
        )
        s_citations = min(100, citations / b_citations * 100) if b_citations else 0
        s_emp_rep = min(100, emp_rep / b_emp_rep * 100) if b_emp_rep else 0
        s_emp_outcomes = (
            min(100, emp_outcomes / b_emp_outcomes * 100) if b_emp_outcomes else 0
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
        s_faculty_student = (
            min(100, b_faculty_student_ratio / faculty_student_ratio * 100)
            if faculty_student_ratio > 0
            else 0
        )
        s_sustainability = (
            min(100, sustainability / b_sustainability * 100) if b_sustainability else 0
        )
        self.research_score = int(s_academic_rep * 0.6 + s_citations * 0.4)
        self.employability_score = int(s_emp_rep * 0.75 + s_emp_outcomes * 0.25)
        self.global_engagement_score = int(
            (s_int_research_net + s_int_faculty_ratio + s_int_student_ratio) / 3
        )
        self.learning_experience_score = int(s_faculty_student)
        self.sustainability_score = int(s_sustainability)
        self.overall_score = int(
            self.research_score * 0.5
            + self.employability_score * 0.2
            + self.global_engagement_score * 0.15
            + self.learning_experience_score * 0.1
            + self.sustainability_score * 0.05
        )
        self.research_comparison_data = [
            {
                "metric": "Academic Rep.",
                "You": academic_rep,
                "NCR Avg": 65.0,
                "Target": b_academic_rep,
            },
            {
                "metric": "Citations/Faculty",
                "You": citations,
                "NCR Avg": 8.5,
                "Target": b_citations,
            },
        ]
        self.employability_comparison_data = [
            {
                "metric": "Emp. Reputation",
                "You": emp_rep,
                "NCR Avg": 65.0,
                "Target": b_emp_rep,
            },
            {
                "metric": "Emp. Outcomes",
                "You": emp_outcomes,
                "NCR Avg": 82.0,
                "Target": b_emp_outcomes,
            },
        ]
        self.global_engagement_comparison_data = [
            {
                "metric": "Research Network",
                "You": int_research_net,
                "NCR Avg": 55.0,
                "Target": b_int_research_net,
            },
            {
                "metric": "Int. Faculty %",
                "You": int_faculty_ratio,
                "NCR Avg": 8.0,
                "Target": b_int_faculty_ratio,
            },
            {
                "metric": "Int. Student %",
                "You": int_student_ratio,
                "NCR Avg": 5.5,
                "Target": b_int_student_ratio,
            },
        ]
        self.learning_experience_comparison_data = [
            {
                "metric": "Faculty:Student",
                "You": faculty_student_ratio,
                "NCR Avg": 18.0,
                "Target": b_faculty_student_ratio,
            }
        ]
        self.sustainability_comparison_data = [
            {
                "metric": "Sustainability",
                "You": sustainability,
                "NCR Avg": 60.0,
                "Target": b_sustainability,
            }
        ]
        self.ai_recommendations = self._get_fallback_recommendations(
            research_score=self.research_score,
            employability_score=self.employability_score,
            global_engagement_score=self.global_engagement_score,
            learning_experience_score=self.learning_experience_score,
            sustainability_score=self.sustainability_score,
        )
        self.generate_ai_recommendations(
            research_score=self.research_score,
            employability_score=self.employability_score,
            global_engagement_score=self.global_engagement_score,
            learning_experience_score=self.learning_experience_score,
            sustainability_score=self.sustainability_score,
            overall_score=self.overall_score,
            academic_rep=academic_rep,
            citations=citations,
            emp_rep=emp_rep,
            emp_outcomes=emp_outcomes,
            int_research_net=int_research_net,
            int_faculty_ratio=int_faculty_ratio,
            int_student_ratio=int_student_ratio,
            faculty_student_ratio=faculty_student_ratio,
            sustainability=sustainability,
        )

    @rx.event(background=True)
    async def generate_ai_recommendations(
        self,
        research_score: int,
        employability_score: int,
        global_engagement_score: int,
        learning_experience_score: int,
        sustainability_score: int,
        overall_score: int,
        academic_rep: float,
        citations: float,
        emp_rep: float,
        emp_outcomes: float,
        int_research_net: float,
        int_faculty_ratio: float,
        int_student_ratio: float,
        faculty_student_ratio: float,
        sustainability: float,
    ):
        """Generate AI-powered strategic recommendations using Google AI."""
        async with self:
            self.is_generating_recommendations = True
        if not GOOGLE_AI_AVAILABLE:
            async with self:
                self.is_generating_recommendations = False
            return
        try:
            performance_summary = f"\nPerformance Summary:\n- Overall Readiness Score: {overall_score}/100\n- Research & Discovery: {research_score}/100 (50% weight)\n  * Academic Reputation: {academic_rep}/100\n  * Citations per Faculty: {citations}\n- Employability & Outcomes: {employability_score}/100 (20% weight)\n  * Employer Reputation: {emp_rep}/100\n  * Employment Outcomes: {emp_outcomes}%\n- Global Engagement: {global_engagement_score}/100 (15% weight)\n  * International Research Network: {int_research_net}/100\n  * International Faculty Ratio: {int_faculty_ratio}%\n  * International Student Ratio: {int_student_ratio}%\n- Learning Experience: {learning_experience_score}/100 (10% weight)\n  * Faculty-Student Ratio: 1:{faculty_student_ratio}\n- Sustainability: {sustainability_score}/100 (5% weight)\n  * Sustainability Metrics: {sustainability}/100\n"
            weak_areas = []
            if research_score < 70:
                weak_areas.append("Research & Discovery")
            if employability_score < 70:
                weak_areas.append("Employability & Outcomes")
            if global_engagement_score < 70:
                weak_areas.append("Global Engagement")
            if learning_experience_score < 70:
                weak_areas.append("Learning Experience")
            if sustainability_score < 70:
                weak_areas.append("Sustainability")
            prompt = f"""You are an expert higher education consultant specializing in international university rankings (QS and THE). \n\nAnalyze the following performance data for a Higher Education Institution in the Philippines and provide 3-4 strategic, actionable recommendations to improve their international ranking readiness.\n\n{performance_summary}\n\nAreas needing improvement: {(", ".join(weak_areas) if weak_areas else "All areas are performing well")}\n\nProvide recommendations in JSON format with this structure:\n{{\n  "recommendations": [\n    {{\n      "title": "Short, actionable title (max 8 words)",\n      "description": "Detailed recommendation (2-3 sentences) explaining what to do and why",\n      "category": "Research & Discovery|Employability|Global Engagement|Learning Experience|Sustainability|Overall",\n      "priority": "High|Medium|Low"\n    }}\n  ]\n}}\n\nFocus on:\n1. Specific, actionable steps the institution can take\n2. Evidence-based strategies used by top-ranked universities\n3. Realistic improvements given the Philippine higher education context\n4. Prioritize recommendations that will have the most impact on overall score\n\nReturn ONLY valid JSON, no additional text."""
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith(""):
                response_text = response_text[7:]
            if response_text.startswith(""):
                response_text = response_text[3:]
            if response_text.endswith(""):
                response_text = response_text[:-3]
            response_text = response_text.strip()
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
                        "title": rec.get("title", "Strategic Recommendation"),
                        "description": rec.get("description", ""),
                        "category": category,
                        "priority": rec.get("priority", "Medium"),
                        "icon": icon,
                        "color_class": color_class,
                        "bg_class": bg_class,
                    }
                )
            async with self:
                self.ai_recommendations = recommendations
                self.is_generating_recommendations = False
        except Exception as e:
            logging.exception(f"Error generating AI recommendations: {e}")
            async with self:
                self.ai_recommendations = self._get_fallback_recommendations(
                    research_score,
                    employability_score,
                    global_engagement_score,
                    learning_experience_score,
                    sustainability_score,
                )
                self.is_generating_recommendations = False

    def _get_fallback_recommendations(
        self,
        research_score: int,
        employability_score: int,
        global_engagement_score: int,
        learning_experience_score: int,
        sustainability_score: int,
    ) -> list[dict[str, str]]:
        """Generate fallback recommendations based on scores."""
        recommendations = []
        total_score = (
            research_score
            + employability_score
            + global_engagement_score
            + learning_experience_score
            + sustainability_score
        )
        if total_score == 0:
            recommendations.append(
                {
                    "title": "Enter Assessment Data",
                    "description": "Please fill in the data entry forms on the Dashboard page to receive personalized recommendations based on your institution's performance metrics.",
                    "category": "Overall",
                    "priority": "High",
                    "icon": "clipboard",
                    "color_class": "text-blue-600",
                    "bg_class": "bg-blue-50 border-blue-100",
                }
            )
            recommendations.append(
                {
                    "title": "Complete All Categories",
                    "description": "Ensure all assessment categories (Research, Employability, Global Engagement, Learning Experience, and Sustainability) are completed for accurate analysis.",
                    "category": "Overall",
                    "priority": "Medium",
                    "icon": "check-circle",
                    "color_class": "text-amber-600",
                    "bg_class": "bg-amber-50 border-amber-100",
                }
            )
            return recommendations
        if research_score < 80:
            recommendations.append(
                {
                    "title": "Enhance Research Excellence",
                    "description": f"Your research score is {research_score}/100. Focus on increasing high-impact publications, improving citation rates, and strengthening academic reputation through international collaborations and research grants.",
                    "category": "Research & Discovery",
                    "priority": "High" if research_score < 60 else "Medium",
                    "icon": "microscope",
                    "color_class": "text-purple-600",
                    "bg_class": "bg-purple-50 border-purple-100",
                }
            )
        if employability_score < 80:
            recommendations.append(
                {
                    "title": "Strengthen Employer Partnerships",
                    "description": f"Your employability score is {employability_score}/100. Build stronger industry partnerships, improve graduate employment tracking, and enhance employer reputation through alumni engagement and career services.",
                    "category": "Employability",
                    "priority": "High" if employability_score < 60 else "Medium",
                    "icon": "briefcase",
                    "color_class": "text-emerald-600",
                    "bg_class": "bg-emerald-50 border-emerald-100",
                }
            )
        if global_engagement_score < 80:
            recommendations.append(
                {
                    "title": "Expand International Presence",
                    "description": f"Your global engagement score is {global_engagement_score}/100. Increase international faculty and student ratios, establish more international research networks, and promote student exchange programs.",
                    "category": "Global Engagement",
                    "priority": "Medium",
                    "icon": "globe",
                    "color_class": "text-blue-600",
                    "bg_class": "bg-blue-50 border-blue-100",
                }
            )
        if learning_experience_score < 80:
            recommendations.append(
                {
                    "title": "Improve Faculty-Student Ratio",
                    "description": f"Your learning experience score is {learning_experience_score}/100. Consider hiring additional faculty members to improve the faculty-student ratio, which enhances teaching quality and student support.",
                    "category": "Learning Experience",
                    "priority": "Medium",
                    "icon": "graduation-cap",
                    "color_class": "text-indigo-600",
                    "bg_class": "bg-indigo-50 border-indigo-100",
                }
            )
        if sustainability_score < 80:
            recommendations.append(
                {
                    "title": "Enhance Sustainability Initiatives",
                    "description": f"Your sustainability score is {sustainability_score}/100. Develop comprehensive ESG policies, implement environmental programs, and integrate sustainability into curriculum and campus operations.",
                    "category": "Sustainability",
                    "priority": "Low",
                    "icon": "leaf",
                    "color_class": "text-green-600",
                    "bg_class": "bg-green-50 border-green-100",
                }
            )
        if not recommendations:
            recommendations.append(
                {
                    "title": "Maintain Excellence Standards",
                    "description": "Your institution is performing well across all categories. Continue monitoring metrics, maintain current standards, and explore opportunities for incremental improvements to stay competitive.",
                    "category": "Overall",
                    "priority": "Low",
                    "icon": "lightbulb",
                    "color_class": "text-amber-600",
                    "bg_class": "bg-amber-50 border-amber-100",
                }
            )
            recommendations.append(
                {
                    "title": "Benchmark Against Top Institutions",
                    "description": "Compare your metrics with top-ranked universities globally to identify areas for strategic enhancement and maintain your competitive position.",
                    "category": "Overall",
                    "priority": "Medium",
                    "icon": "bar-chart-2",
                    "color_class": "text-blue-600",
                    "bg_class": "bg-blue-50 border-blue-100",
                }
            )
        return recommendations