import reflex as rx
from app.states.historical_analytics_state import HistoricalAnalyticsState
from app.states.historical_state import HistoricalState
from app.components.design_system import DS, ds_card, ds_stat_card


def analytics_summary_cards() -> rx.Component:
    has_data = HistoricalAnalyticsState.has_meaningful_data
    return rx.el.div(
        ds_stat_card(
            title="Peak Performance Year",
            value=rx.cond(
                has_data, HistoricalAnalyticsState.stats_summary["best_year"], "No Data"
            ),
            icon="award",
            color_variant=rx.cond(has_data, "success", "neutral"),
        ),
        ds_stat_card(
            title="Average Aggregate Score",
            value=rx.cond(
                has_data,
                f"{HistoricalAnalyticsState.stats_summary['avg_score']}%",
                "0%",
            ),
            icon="target",
            color_variant=rx.cond(has_data, "primary", "neutral"),
        ),
        ds_stat_card(
            title="Cycle Consistency",
            value=rx.cond(
                has_data,
                f"{HistoricalAnalyticsState.stats_summary['consistency']}%",
                "0%",
            ),
            icon="activity",
            color_variant=rx.cond(has_data, "warning", "neutral"),
        ),
        ds_stat_card(
            title="Overall Growth Delta",
            value=rx.cond(
                has_data, f"{HistoricalAnalyticsState.stats_summary['growth']}%", "0.0%"
            ),
            icon=rx.cond(
                HistoricalAnalyticsState.stats_summary["growth"].to(float) >= 0,
                "trending-up",
                "trending-down",
            ),
            color_variant=rx.cond(
                HistoricalAnalyticsState.stats_summary["growth"].to(float) >= 0,
                "success",
                "error",
            ),
        ),
        class_name="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8",
    )


def radar_category_chart() -> rx.Component:
    has_data = HistoricalAnalyticsState.has_meaningful_data
    return rx.el.div(
        rx.el.h3(
            "Core Competency Profile",
            class_name="text-lg font-bold text-slate-800 mb-6",
        ),
        rx.cond(
            has_data,
            rx.recharts.radar_chart(
                rx.recharts.polar_grid(),
                rx.recharts.polar_angle_axis(
                    data_key="subject", custom_attrs={"fontSize": "10px"}
                ),
                rx.recharts.polar_radius_axis(angle=30, domain=[0, 100]),
                rx.recharts.radar(
                    name="Avg Performance",
                    data_key="A",
                    stroke="#2563eb",
                    fill="#3b82f6",
                    fill_opacity=0.5,
                ),
                data=HistoricalAnalyticsState.category_radar_data,
                width="100%",
                height=350,
            ),
            rx.el.div(
                rx.el.p(
                    "Insufficient category data for radar visualization.",
                    class_name="text-slate-400 italic text-sm",
                ),
                class_name="flex items-center justify-center h-[350px] border-2 border-dashed border-slate-100 rounded-3xl",
            ),
        ),
        class_name="bg-white p-8 rounded-[2.5rem] border border-blue-100 shadow-sm",
    )


def growth_rate_chart() -> rx.Component:
    has_data = HistoricalAnalyticsState.performance_growth_data.length() > 0
    return rx.el.div(
        rx.el.h3(
            "Year-over-Year Growth Rate",
            class_name="text-lg font-bold text-slate-800 mb-6",
        ),
        rx.cond(
            has_data,
            rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                rx.recharts.graphing_tooltip(),
                rx.recharts.x_axis(data_key="year"),
                rx.recharts.y_axis(),
                rx.recharts.bar(
                    data_key="rate",
                    fill="#2563eb",
                    radius=[4, 4, 0, 0],
                    name="Growth %",
                ),
                data=HistoricalAnalyticsState.performance_growth_data,
                width="100%",
                height=350,
            ),
            rx.el.div(
                rx.el.p(
                    "Multiple years of data required for growth analysis.",
                    class_name="text-slate-400 italic text-sm",
                ),
                class_name="flex items-center justify-center h-[350px] border-2 border-dashed border-slate-100 rounded-3xl",
            ),
        ),
        class_name="bg-white p-8 rounded-[2.5rem] border border-blue-100 shadow-sm",
    )


def ai_insights_section() -> rx.Component:
    has_data = HistoricalAnalyticsState.has_meaningful_data
    return rx.el.div(
        rx.el.div(
            rx.icon("sparkles", class_name="h-6 w-6 text-blue-600 mr-3"),
            rx.el.h3(
                "AI Historical Trend Analysis",
                class_name="text-xl font-black text-blue-900",
            ),
            class_name="flex items-center mb-6",
        ),
        rx.cond(
            HistoricalAnalyticsState.is_generating_ai,
            rx.el.div(
                rx.el.div(
                    class_name="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"
                ),
                rx.el.p(
                    "Analyzing historical data patterns...",
                    class_name="text-blue-700 font-bold mt-4",
                ),
                class_name="text-center p-12 bg-blue-50 rounded-3xl border border-dashed border-blue-200",
            ),
            rx.cond(
                has_data,
                rx.el.div(
                    rx.foreach(
                        HistoricalAnalyticsState.ai_insights,
                        lambda insight: rx.el.div(
                            rx.el.h4(
                                insight["title"],
                                class_name="font-black text-blue-900 mb-2",
                            ),
                            rx.el.p(
                                insight["description"],
                                class_name="text-sm text-blue-800 leading-relaxed",
                            ),
                            class_name="p-6 bg-white border border-blue-100 rounded-3xl shadow-sm",
                        ),
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-3 gap-6",
                ),
                rx.el.div(
                    rx.el.p(
                        "Historical data analysis is unavailable. Please commit records in the Data Entry tab.",
                        class_name="text-blue-600/60 font-medium",
                    ),
                    class_name="text-center p-12 bg-blue-50 rounded-3xl border border-blue-100",
                ),
            ),
        ),
        class_name="mt-12",
    )


def historical_analytics_view() -> rx.Component:
    has_data = HistoricalAnalyticsState.has_meaningful_data
    return rx.el.div(
        rx.cond(
            has_data,
            rx.el.div(
                analytics_summary_cards(),
                rx.el.div(
                    rx.el.div(
                        radar_category_chart(), class_name="col-span-1 md:col-span-1"
                    ),
                    rx.el.div(
                        growth_rate_chart(), class_name="col-span-1 md:col-span-1"
                    ),
                    class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12",
                ),
                ai_insights_section(),
                class_name="animate-in fade-in duration-700",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("database-zap", class_name="h-12 w-12 text-blue-200 mb-4"),
                    rx.el.h2(
                        "No Historical Records Found",
                        class_name="text-2xl font-black text-blue-900 mb-2",
                    ),
                    rx.el.p(
                        "The archive is currently empty for this institution. Please populate historical scores in the Data Entry tab first to generate multi-year analytics.",
                        class_name="text-blue-700/70 max-w-md mx-auto mb-8 text-sm leading-relaxed",
                    ),
                    rx.el.button(
                        "Switch to Data Entry",
                        on_click=lambda: HistoricalAnalyticsState.set_active_view(
                            "entry"
                        ),
                        class_name="px-8 py-3 bg-blue-600 text-white rounded-full font-black shadow-lg shadow-blue-100 hover:bg-blue-700 transition-all active:scale-95",
                    ),
                    class_name="text-center py-24 px-8 bg-blue-50 rounded-[3rem] border border-dashed border-blue-200 max-w-4xl mx-auto",
                ),
                class_name="py-12 animate-in fade-in slide-in-from-bottom-4 duration-500",
            ),
        )
    )