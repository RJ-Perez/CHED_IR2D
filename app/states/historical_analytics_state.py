import reflex as rx
from typing import TypedDict, Any
import json
import logging
import asyncio
import os
from sqlalchemy import text
from app.states.hei_state import HEIState
from app.states.historical_state import HistoricalState

try:
    from google import genai
    from google.genai import types

    GOOGLE_AI_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_AI_AVAILABLE = bool(GOOGLE_AI_API_KEY)
except ImportError as e:
    logging.exception(f"Google AI SDK not found: {e}")
    GOOGLE_AI_AVAILABLE = False


class HistoricalAnalyticsState(rx.State):
    """State for deep analytics of historical ranking data."""

    is_loading: bool = False
    is_generating_ai: bool = False
    category_radar_data: list[dict[str, str | int]] = []
    performance_growth_data: list[dict[str, str | float]] = []
    heatmap_data: list[dict[str, str | int | float | bool]] = []
    ai_insights: list[dict[str, str]] = []
    active_view: str = "entry"

    @rx.var(cache=True)
    async def stats_summary(self) -> dict[str, str | int | float]:
        hist = await self.get_state(HistoricalState)
        data = hist.trend_data
        if not data:
            return {"best_year": "N/A", "avg_score": 0, "growth": 0.0, "consistency": 0}
        scores = [d.get("Average", 0) for d in data]
        best_idx = scores.index(max(scores))
        best_year = str(data[best_idx].get("year", "N/A"))
        avg_score = sum(scores) / len(scores)
        growth = 0.0
        if len(scores) > 1:
            growth = (
                (scores[-1] - scores[0]) / scores[0] * 100 if scores[0] > 0 else 0.0
            )
        consistency = 100
        if len(scores) > 1 and avg_score > 0:
            variance = sum(((s - avg_score) ** 2 for s in scores)) / len(scores)
            std_dev = variance**0.5
            consistency = max(0, min(100, 100 * (1 - std_dev / avg_score)))
        return {
            "best_year": best_year,
            "avg_score": int(avg_score),
            "growth": round(growth, 1),
            "consistency": int(consistency),
        }

    @rx.event
    def set_active_view(self, view: str):
        self.active_view = view
        if view == "analytics":
            return HistoricalAnalyticsState.refresh_analytics

    @rx.event(background=True)
    async def refresh_analytics(self):
        async with self:
            self.is_loading = True
            hist = await self.get_state(HistoricalState)
            data = hist.trend_data
            if not data:
                self.is_loading = False
                return
        radar = []
        cats = [
            ("Research", "academic_reputation"),
            ("Citations", "citations_per_faculty"),
            ("Employer", "employer_reputation"),
            ("Employment", "employment_outcomes"),
            ("Network", "international_research_network"),
            ("Faculty %", "international_faculty_ratio"),
            ("Student %", "international_student_ratio"),
            ("Teaching", "faculty_student_ratio"),
            ("Sustainability", "sustainability_metrics"),
        ]
        for label, key in cats:
            vals = [d.get(key, 0) for d in data if key in d]
            avg = sum(vals) / len(vals) if vals else 0
            radar.append({"subject": label, "A": int(avg), "fullMark": 100})
        growth = []
        for i in range(1, len(data)):
            prev = data[i - 1].get("Average", 0)
            curr = data[i].get("Average", 0)
            delta = (curr - prev) / prev * 100 if prev > 0 else 0
            growth.append(
                {
                    "year": f"{data[i - 1]['year']}→{data[i]['year']}",
                    "rate": round(delta, 1),
                }
            )
        async with self:
            self.category_radar_data = radar
            self.performance_growth_data = growth
            self.is_loading = False
        yield HistoricalAnalyticsState.generate_ai_insights

    @rx.event(background=True)
    async def generate_ai_insights(self):
        if not GOOGLE_AI_AVAILABLE:
            return
        async with self:
            self.is_generating_ai = True
            hist = await self.get_state(HistoricalState)
            data = hist.trend_data
            hei = await self.get_state(HEIState)
            hei_name = (
                hei.selected_hei["name"] if hei.selected_hei else "the institution"
            )
        try:
            prompt = f"Analyze the historical performance of {hei_name} based on this data: {json.dumps(data)}. Provide 3 strategic insights regarding their improvement trends, volatility, and areas of consistent strength in a valid JSON list of objects with 'title' and 'description' keys. Return ONLY JSON."
            client = genai.Client(api_key=GOOGLE_AI_API_KEY)
            response = await client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            if response and response.text:
                insights = json.loads(response.text)
                async with self:
                    self.ai_insights = insights
        except Exception as e:
            logging.exception(f"AI Error: {e}")
        finally:
            async with self:
                self.is_generating_ai = False