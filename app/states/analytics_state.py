import reflex as rx
from sqlalchemy import text
from app.states.hei_state import HEIState
import logging
import json
import re
import os
import asyncio
import time

AI_RECOMMENDATIONS_CACHE = {}
CACHE_TTL = 1800
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


class AnalyticsState(rx.State):
    """
    Calculates weighted performance scores based on HEI data entry.
    Triggers AI-driven strategic advice generation based on performance gaps.
    """

    research_score: int = 0
    employability_score: int = 0
    global_engagement_score: int = 0
    learning_experience_score: int = 0
    sustainability_score: int = 0
    overall_score: int = 0
    review_status: str = ""
    is_loading: bool = False
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
    historical_trend_data: list[dict[str, str | int | float]] = []
    year_over_year_changes: dict[str, float] = {}

    async def _calculate_ncr_averages(self) -> dict[str, float]:
        """Queries all scores for 2025 and calculates real NCR averages per indicator."""
        async with rx.asession() as session:
            result = await session.execute(
                text("""
                SELECT 
                    i.code, 
                    AVG(CAST(NULLIF(regexp_replace(s.value, '[^0-9.]', '', 'g'), '') AS DOUBLE PRECISION)) as average
                FROM institution_scores s
                JOIN ranking_indicators i ON s.indicator_id = i.id
                WHERE s.ranking_year = 2025
                GROUP BY i.code
                """)
            )
            rows = result.all()
            return {
                row[0]: round(row[1], 2) if row[1] is not None else 0.0 for row in rows
            }

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

    def _parse_float(self, value: str) -> float:
        try:
            clean = "".join((c for c in value if c.isdigit() or c == "."))
            return float(clean) if clean else 0.0
        except ValueError as e:
            logging.exception(f"Error parsing float: {e}")
            return 0.0

    async def _fetch_scores(self, inst_id: int):
        async with rx.asession() as session:
            result = await session.execute(
                text("""
                SELECT i.code, s.value, s.review_status
                FROM institution_scores s
                JOIN ranking_indicators i ON s.indicator_id = i.id
                WHERE s.institution_id = :inst_id AND s.ranking_year = 2025
                """),
                {"inst_id": inst_id},
            )
            return result.all()

    @rx.event(background=True)
    async def on_load(self):
        """Optimized: Uses asyncio.gather for parallel database operations and batched state updates."""
        async with self:
            self.is_loading = True
        try:
            async with self:
                hei_state = await self.get_state(HEIState)
                if not hei_state.selected_hei:
                    self.is_loading = False
                    return
                institution_id = int(hei_state.selected_hei["id"])
            scores_data, ncr_avgs = await asyncio.gather(
                self._fetch_scores(institution_id), self._calculate_ncr_averages()
            )
            score_map = {row[0]: self._parse_float(row[1]) for row in scores_data}
            review_status = scores_data[0][2] if scores_data else "Pending"
            academic_rep = score_map.get("academic_reputation", 0.0)
            citations = score_map.get("citations_per_faculty", 0.0)
            emp_rep = score_map.get("employer_reputation", 0.0)
            emp_outcomes = score_map.get("employment_outcomes", 0.0)
            int_research_net = score_map.get("international_research_network", 0.0)
            int_faculty_ratio = score_map.get("international_faculty_ratio", 0.0)
            int_student_ratio = score_map.get("international_student_ratio", 0.0)
            faculty_student_ratio = score_map.get("faculty_student_ratio", 0.0)
            sustainability = score_map.get("sustainability_metrics", 0.0)
            b_academic_rep = 100.0
            b_citations = 100.0
            b_emp_rep = 100.0
            b_emp_outcomes = 100.0
            b_int_research_net = 100.0
            b_int_faculty_ratio = 25.0
            b_int_student_ratio = 25.0
            b_faculty_student_ratio = 8.0
            b_sustainability = 100.0
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
            hist_result = await session.execute(
                text("""
<<<<<<< HEAD
                SELECT ranking_year, indicator_code, value
                FROM historical_scores
=======
                SELECT ranking_year, overall_score, academic_reputation
                FROM historical_performance
>>>>>>> version2
                WHERE institution_id = :iid
                ORDER BY ranking_year ASC
                """),
                {"iid": institution_id},
            )
            hist_rows = hist_result.all()
<<<<<<< HEAD
            hist_data_map = {}
            for y, c, v in hist_rows:
                y_str = str(y)
                if y_str not in hist_data_map:
                    hist_data_map[y_str] = {}
                try:
                    hist_data_map[y_str][c] = int(float(v))
                except Exception as e:
                    logging.exception(f"Error parsing historical score: {e}")
                    hist_data_map[y_str][c] = 0
            trend_data = []
            for year in sorted(hist_data_map.keys()):
                scores = list(hist_data_map[year].values())
                avg = int(sum(scores) / len(scores)) if scores else 0
                trend_data.append(
                    {
                        "year": year,
                        "score": avg,
                        "research": hist_data_map[year].get("academic_reputation", 0),
=======
            trend_data = []
            for y, ov, ar in hist_rows:
                trend_data.append(
                    {
                        "year": str(y),
                        "score": int(ov) if ov else 0,
                        "research": int(ar) if ar else 0,
>>>>>>> version2
                    }
                )
            trend_data.append(
                {
                    "year": "2025",
                    "score": overall_score,
                    "research": int(s_academic_rep),
                }
            )
            yoy_changes = {}
            if len(trend_data) >= 2:
                last = trend_data[-1]
                prev = trend_data[-2]
                yoy_changes["overall"] = round(
                    (last["score"] - prev["score"])
                    / (prev["score"] if prev["score"] else 1)
                    * 100,
                    1,
                )
            async with self:
                self.historical_trend_data = trend_data
                self.year_over_year_changes = yoy_changes
                self.research_score = research_score
                self.employability_score = employability_score
                self.global_engagement_score = global_engagement_score
                self.learning_experience_score = learning_experience_score
                self.sustainability_score = sustainability_score
                self.overall_score = overall_score
                self.review_status = review_status
                self.research_comparison_data = [
                    {
                        "metric": "Academic Rep.",
                        "You": academic_rep,
                        "NCR Avg": ncr_avgs.get("academic_reputation", 0.0),
                        "Target": b_academic_rep,
                    },
                    {
                        "metric": "Citations/Faculty",
                        "You": citations,
                        "NCR Avg": ncr_avgs.get("citations_per_faculty", 0.0),
                        "Target": b_citations,
                    },
                ]
                self.employability_comparison_data = [
                    {
                        "metric": "Emp. Reputation",
                        "You": emp_rep,
                        "NCR Avg": ncr_avgs.get("employer_reputation", 0.0),
                        "Target": b_emp_rep,
                    },
                    {
                        "metric": "Emp. Outcomes",
                        "You": emp_outcomes,
                        "NCR Avg": ncr_avgs.get("employment_outcomes", 0.0),
                        "Target": b_emp_outcomes,
                    },
                ]
                self.global_engagement_comparison_data = [
                    {
                        "metric": "Research Network",
                        "You": int_research_net,
                        "NCR Avg": ncr_avgs.get("international_research_network", 0.0),
                        "Target": b_int_research_net,
                    },
                    {
                        "metric": "Int. Faculty %",
                        "You": int_faculty_ratio,
                        "NCR Avg": ncr_avgs.get("international_faculty_ratio", 0.0),
                        "Target": b_int_faculty_ratio,
                    },
                    {
                        "metric": "Int. Student %",
                        "You": int_student_ratio,
                        "NCR Avg": ncr_avgs.get("international_student_ratio", 0.0),
                        "Target": b_int_student_ratio,
                    },
                ]
                self.learning_experience_comparison_data = [
                    {
                        "metric": "Faculty:Student",
                        "You": faculty_student_ratio,
                        "NCR Avg": ncr_avgs.get("faculty_student_ratio", 0.0),
                        "Target": b_faculty_student_ratio,
                    }
                ]
                self.sustainability_comparison_data = [
                    {
                        "metric": "Sustainability",
                        "You": sustainability,
                        "NCR Avg": ncr_avgs.get("sustainability_metrics", 0.0),
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
        except Exception as e:
            logging.exception(f"Error in AnalyticsState.on_load: {e}")
        finally:
            async with self:
                self.is_loading = False
        yield AnalyticsState.generate_ai_recommendations(
            research_score=research_score,
            employability_score=employability_score,
            global_engagement_score=global_engagement_score,
            learning_experience_score=learning_experience_score,
            sustainability_score=sustainability_score,
            overall_score=overall_score,
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

    @rx.event
    def clear_ai_cache(self):
        """Manually clears the recommendations cache to force refresh with fixed logic."""
        global AI_RECOMMENDATIONS_CACHE
        AI_RECOMMENDATIONS_CACHE = {}

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
            hei_state = await self.get_state(HEIState)
            inst_id = (
                hei_state.selected_hei["id"] if hei_state.selected_hei else "unknown"
            )
        now = time.time()
        if inst_id in AI_RECOMMENDATIONS_CACHE:
            cache_entry = AI_RECOMMENDATIONS_CACHE[inst_id]
            is_expired = now - cache_entry["timestamp"] > CACHE_TTL
            is_invalid = (
                not cache_entry.get("recommendations")
                or len(cache_entry["recommendations"]) == 0
            )
            if not is_invalid:
                first_rec = cache_entry["recommendations"][0]
                desc = first_rec.get("description", "")
                if len(desc) > 40 and " " not in desc:
                    is_invalid = True
            if not is_expired and (not is_invalid):
                logging.info(f"Using valid cached AI recommendations for {inst_id}")
                async with self:
                    self.ai_recommendations = cache_entry["recommendations"]
                    self.is_generating_recommendations = False
                return
            else:
                logging.warning(
                    f"Cache for {inst_id} is {('expired' if is_expired else 'invalid')}. Refreshing..."
                )
        if not GOOGLE_AI_AVAILABLE:
            async with self:
                self.is_generating_recommendations = False
            return
        try:
            performance_summary = f"\nPerformance Summary:\n- Overall Readiness Score: {overall_score}/100\n- Research & Discovery: {research_score}/100\n- Employability & Outcomes: {employability_score}/100\n- Global Engagement: {global_engagement_score}/100\n- Learning Experience: {learning_experience_score}/100\n- Sustainability: {sustainability_score}/100\n"
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
            prompt = f"""You are an expert higher education consultant. \n\nAnalyze the following performance data for a Higher Education Institution and provide 3-4 strategic, actionable recommendations to improve their institutional readiness.\n\n{performance_summary}\n\nAreas needing improvement: {(", ".join(weak_areas) if weak_areas else "All areas are performing well")}\n\nProvide recommendations in JSON format with this structure:\n{{\n  "recommendations": [\n    {{\n      "title": "Short, actionable title (max 8 words)",\n      "description": "Detailed recommendation explaining specific actions to improve performance in this area.",\n      "category": "Research & Discovery|Employability|Global Engagement|Learning Experience|Sustainability|Overall",\n      "priority": "High|Medium|Low"\n    }}\n  ]\n}}\n\nReturn ONLY valid JSON, no additional text."""
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
                            f"Attempt {attempt + 1}: Google AI returned empty response or no text."
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
                                "Google AI quota exhausted after all retries. Falling back to rule-based recommendations."
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
                        continue
                    else:
                        logging.exception(
                            f"Error generating content from Google AI: {e}"
                        )
                        break
            if not response_text or not response_text.strip():
                logging.info(
                    "Google AI returned an empty response or failed. Falling back to rule-based recommendations."
                )
                async with self:
                    self.ai_recommendations = self._get_fallback_recommendations(
                        research_score,
                        employability_score,
                        global_engagement_score,
                        learning_experience_score,
                        sustainability_score,
                    )
                    self.is_generating_recommendations = False
                return
            response_text = self._clean_json_response(response_text)
            if not response_text:
                logging.info(
                    "Cleaned AI response is empty. Falling back to rule-based recommendations."
                )
                async with self:
                    self.ai_recommendations = self._get_fallback_recommendations(
                        research_score,
                        employability_score,
                        global_engagement_score,
                        learning_experience_score,
                        sustainability_score,
                    )
                    self.is_generating_recommendations = False
                return
            try:
                recommendations_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logging.exception(
                    f"Failed to parse AI JSON response: {e}. Cleaned response: {response_text[:200]}..."
                )
                async with self:
                    self.ai_recommendations = self._get_fallback_recommendations(
                        research_score,
                        employability_score,
                        global_engagement_score,
                        learning_experience_score,
                        sustainability_score,
                    )
                    self.is_generating_recommendations = False
                return
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
            AI_RECOMMENDATIONS_CACHE[inst_id] = {
                "timestamp": time.time(),
                "recommendations": recommendations,
            }
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
                    "title": "Boost Academic Reputation & Citations",
                    "description": f"Your Research & Discovery score is {research_score}/100. Focus on increasing 'Citations per Faculty' by encouraging publication in Scopus-indexed journals and improve 'Academic Reputation' by increasing visibility in global academic networks.",
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
                    "title": "Improve Employer Reputation",
                    "description": f"Your Employability score is {employability_score}/100. Strengthen 'Employer Reputation' by expanding industry partnerships and ensure robust tracking of 'Employment Outcomes' for recent graduates.",
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
                    "title": "Grow International Research Network",
                    "description": f"Your Global Engagement score is {global_engagement_score}/100. Focus on the 'International Research Network' (IRN) index by formalizing cross-border research collaborations and recruiting International Faculty.",
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
                    "title": "Optimize Faculty-Student Ratio",
                    "description": f"Your Learning Experience score is {learning_experience_score}/100. The 'Faculty Student Ratio' accounts for 10% of the QS score; consider strategic hiring to lower this ratio and improve teaching quality metrics.",
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
                    "title": "Advance Sustainability (ESG)",
                    "description": f"Your Sustainability score is {sustainability_score}/100. Align institutional policies with UN SDGs and ensure documentation of environmental and social governance initiatives for the QS Sustainability metric.",
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