import reflex as rx
from app.states.historical_analytics_state import HistoricalAnalyticsState
from app.states.historical_state import HistoricalState
from app.components.design_system import DS, ds_card, ds_stat_card


def analytics_summary_cards() -> rx.Component:
    return rx.el.div(
        ds_stat_card(
            title="Peak Performance Year",
            value=HistoricalAnalyticsState.stats_summary["best_year"],
            icon="award",
            color_variant="success",
        ),
        ds_stat_card(
            title="Average Aggregate Score",
            value=f"{HistoricalAnalyticsState.stats_summary['avg_score']}%",
            icon="target",
            color_variant="primary",
        ),
        ds_stat_card(
            title="Cycle Consistency",
            value=f"{HistoricalAnalyticsState.stats_summary['consistency']}%",
            icon="activity",
            color_variant="warning",
        ),
        ds_stat_card(
            title="Overall Growth Delta",
            value=f"{HistoricalAnalyticsState.stats_summary['growth']}%",
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
    return rx.el.div(
        rx.el.h3(
            "Core Competency Profile",
            class_name="text-lg font-bold text-slate-800 mb-6",
        ),
        rx.recharts.radar_chart(
            rx.recharts.polar_grid(),
            rx.recharts.polar_angle_axis(
                data_key="subject", custom_attrs={"fontSize": "10px"}
            ),
            rx.recharts.polar_radius_axis(angle=30, domain=[0, 100]),
            rx.recharts.radar(
                name="Avg Performance",
                data_key="A",
                stroke="#059669",
                fill="#10b981",
                fill_opacity=0.5,
            ),
            data=HistoricalAnalyticsState.category_radar_data,
            width="100%",
            height=350,
        ),
        class_name="bg-white p-8 rounded-[2.5rem] border border-emerald-100 shadow-sm",
    )


def growth_rate_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Year-over-Year Growth Rate",
            class_name="text-lg font-bold text-slate-800 mb-6",
        ),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
            rx.recharts.graphing_tooltip(),
            rx.recharts.x_axis(data_key="year"),
            rx.recharts.y_axis(),
            rx.recharts.bar(
                data_key="rate", fill="#059669", radius=[4, 4, 0, 0], name="Growth %"
            ),
            data=HistoricalAnalyticsState.performance_growth_data,
            width="100%",
            height=350,
        ),
        class_name="bg-white p-8 rounded-[2.5rem] border border-emerald-100 shadow-sm",
    )


def ai_insights_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("sparkles", class_name="h-6 w-6 text-emerald-600 mr-3"),
            rx.el.h3(
                "AI Historical Trend Analysis",
                class_name="text-xl font-black text-emerald-900",
            ),
            class_name="flex items-center mb-6",
        ),
        rx.cond(
            HistoricalAnalyticsState.is_generating_ai,
            rx.el.div(
                rx.el.div(
                    class_name="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mx-auto"
                ),
                rx.el.p(
                    "Analyzing historical data patterns...",
                    class_name="text-emerald-700 font-bold mt-4",
                ),
                class_name="text-center p-12 bg-emerald-50/50 rounded-3xl border border-dashed border-emerald-200",
            ),
            rx.el.div(
                rx.foreach(
                    HistoricalAnalyticsState.ai_insights,
                    lambda insight: rx.el.div(
                        rx.el.h4(
                            insight["title"],
                            class_name="font-black text-emerald-900 mb-2",
                        ),
                        rx.el.p(
                            insight["description"],
                            class_name="text-sm text-emerald-800 leading-relaxed",
                        ),
                        class_name="p-6 bg-white border border-emerald-100 rounded-3xl shadow-sm",
                    ),
                ),
                class_name="grid grid-cols-1 md:grid-cols-3 gap-6",
            ),
        ),
        class_name="mt-12",
    )


def historical_analytics_view() -> rx.Component:
    return rx.el.div(
        analytics_summary_cards(),
        rx.el.div(
            rx.el.div(radar_category_chart(), class_name="col-span-1 md:col-span-1"),
            rx.el.div(growth_rate_chart(), class_name="col-span-1 md:col-span-1"),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12",
        ),
        ai_insights_section(),
        class_name="animate-in fade-in duration-700",
    )