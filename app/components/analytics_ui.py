import reflex as rx
from app.states.analytics_state import AnalyticsState
from app.components.design_system import DS

TOOLTIP_PROPS = {
    "content_style": {
        "background": "white",
        "borderColor": "#e2e8f0",
        "borderRadius": "1rem",
        "boxShadow": "0 10px 15px -3px rgb(0 0 0 / 0.1)",
        "padding": "0.75rem",
        "border": "1px solid #f1f5f9",
    },
    "item_style": {"color": "#1e293b", "fontSize": "0.875rem", "fontWeight": "600"},
    "separator": ": ",
}


@rx.memo
def performance_pie_card(title: str, score: int, color: str, icon: str) -> rx.Component:
    """
    Optimized: Memoized donut chart component to prevent unnecessary re-renders of the expensive Recharts engine.
    """
    chart_data = [
        {"name": "Score", "value": score, "fill": color},
        {"name": "Remaining", "value": 100 - score, "fill": "#f1f5f9"},
    ]
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name=f"h-5 w-5", style={"stroke": color}),
                rx.el.span(
                    title,
                    class_name="text-sm font-bold text-slate-800 ml-2 tracking-tight",
                ),
                class_name="flex items-center mb-4",
            ),
            rx.el.div(
                rx.recharts.pie_chart(
                    rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
                    rx.recharts.pie(
                        data=chart_data,
                        data_key="value",
                        name_key="name",
                        cx="50%",
                        cy="50%",
                        inner_radius="70%",
                        outer_radius="95%",
                        stroke="none",
                        stroke_width=0,
                        start_angle=90,
                        end_angle=-270,
                    ),
                    width="100%",
                    height=160,
                ),
                rx.el.div(
                    rx.el.span(
                        f"{score}%",
                        class_name="text-2xl font-black text-slate-900 tracking-tighter",
                    ),
                    class_name="absolute inset-0 flex items-center justify-center pt-2",
                ),
                class_name="relative",
            ),
            class_name="p-6",
        ),
        class_name=f"bg-white {DS.RADIUS} border border-{DS.BORDER} {DS.SHADOW} overflow-hidden hover:shadow-md transition-shadow duration-300",
    )


def chart_legend() -> rx.Component:
    """Custom HTML legend for charts."""
    return rx.el.div(
        rx.el.div(
            rx.el.span(class_name="w-3 h-3 rounded-full bg-blue-600 mr-2"),
            rx.el.span("Your Institution", class_name="text-xs text-gray-600"),
            class_name="flex items-center mr-4",
        ),
        rx.el.div(
            rx.el.span(class_name="w-3 h-3 rounded-full bg-slate-400 mr-2"),
            rx.el.span("NCR Average", class_name="text-xs text-gray-600"),
            class_name="flex items-center mr-4",
        ),
        rx.el.div(
            rx.el.span(class_name="w-3 h-3 rounded-full bg-emerald-500 mr-2"),
            rx.el.span("QS Stars 5★ Target", class_name="text-xs text-gray-600"),
            class_name="flex items-center",
        ),
        class_name="flex items-center justify-end mb-4",
    )


def research_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h4(
            "Research Performance vs Benchmarks",
            class_name="text-base font-semibold text-gray-800 mb-4",
        ),
        chart_legend(),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(
                horizontal=True, vertical=False, class_name="opacity-25"
            ),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.x_axis(
                data_key="metric",
                axis_line=False,
                tick_line=False,
                custom_attrs={"fontSize": "12px", "fontWeight": "600"},
                tick_margin=10,
            ),
            rx.recharts.y_axis(
                axis_line=False, tick_line=False, custom_attrs={"fontSize": "12px"}
            ),
            rx.recharts.bar(
                data_key="You",
                fill=AnalyticsState.your_color,
                radius=[4, 4, 0, 0],
                bar_size=40,
                name="Your Institution",
            ),
            rx.recharts.bar(
                data_key="NCR Avg",
                fill=AnalyticsState.ncr_average_color,
                radius=[4, 4, 0, 0],
                bar_size=40,
                name="NCR Average",
            ),
            rx.recharts.bar(
                data_key="Target",
                fill=AnalyticsState.target_color,
                radius=[4, 4, 0, 0],
                bar_size=40,
                name="QS Stars 5★ Target",
            ),
            data=AnalyticsState.research_comparison_data,
            width="100%",
            height=300,
            margin={"left": -20, "right": 0, "top": 0, "bottom": 0},
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def employability_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h4(
            "Employability Outcomes Comparison",
            class_name="text-base font-semibold text-gray-800 mb-4",
        ),
        chart_legend(),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(
                horizontal=True, vertical=False, class_name="opacity-25"
            ),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.x_axis(
                data_key="metric",
                axis_line=False,
                tick_line=False,
                custom_attrs={"fontSize": "12px", "fontWeight": "600"},
                tick_margin=10,
            ),
            rx.recharts.y_axis(
                axis_line=False, tick_line=False, custom_attrs={"fontSize": "12px"}
            ),
            rx.recharts.bar(
                data_key="You",
                fill=AnalyticsState.your_color,
                radius=[4, 4, 0, 0],
                bar_size=40,
                name="Your Institution",
            ),
            rx.recharts.bar(
                data_key="NCR Avg",
                fill=AnalyticsState.ncr_average_color,
                radius=[4, 4, 0, 0],
                bar_size=40,
                name="NCR Average",
            ),
            rx.recharts.bar(
                data_key="Target",
                fill=AnalyticsState.target_color,
                radius=[4, 4, 0, 0],
                bar_size=40,
                name="QS Stars 5★ Target",
            ),
            data=AnalyticsState.employability_comparison_data,
            width="100%",
            height=300,
            margin={"left": -20, "right": 0, "top": 0, "bottom": 0},
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def global_engagement_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h4(
            "Global Engagement Comparison",
            class_name="text-base font-semibold text-gray-800 mb-4",
        ),
        chart_legend(),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(
                horizontal=True, vertical=False, class_name="opacity-25"
            ),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.x_axis(
                data_key="metric",
                axis_line=False,
                tick_line=False,
                custom_attrs={"fontSize": "12px", "fontWeight": "600"},
                tick_margin=10,
            ),
            rx.recharts.y_axis(
                axis_line=False, tick_line=False, custom_attrs={"fontSize": "12px"}
            ),
            rx.recharts.bar(
                data_key="You",
                fill=AnalyticsState.your_color,
                radius=[4, 4, 0, 0],
                bar_size=40,
                name="Your Institution",
            ),
            rx.recharts.bar(
                data_key="NCR Avg",
                fill=AnalyticsState.ncr_average_color,
                radius=[4, 4, 0, 0],
                bar_size=40,
                name="NCR Average",
            ),
            rx.recharts.bar(
                data_key="Target",
                fill=AnalyticsState.target_color,
                radius=[4, 4, 0, 0],
                bar_size=40,
                name="QS Stars 5★ Target",
            ),
            data=AnalyticsState.global_engagement_comparison_data,
            width="100%",
            height=300,
            margin={"left": -20, "right": 0, "top": 0, "bottom": 0},
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def learning_experience_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h4(
            "Learning Experience Comparison",
            class_name="text-base font-semibold text-gray-800 mb-4",
        ),
        chart_legend(),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(
                horizontal=True, vertical=False, class_name="opacity-25"
            ),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.x_axis(
                data_key="metric",
                axis_line=False,
                tick_line=False,
                custom_attrs={"fontSize": "12px", "fontWeight": "600"},
                tick_margin=10,
            ),
            rx.recharts.y_axis(
                axis_line=False, tick_line=False, custom_attrs={"fontSize": "12px"}
            ),
            rx.recharts.bar(
                data_key="You",
                fill=AnalyticsState.your_color,
                radius=[4, 4, 0, 0],
                bar_size=40,
                name="Your Institution",
            ),
            rx.recharts.bar(
                data_key="NCR Avg",
                fill=AnalyticsState.ncr_average_color,
                radius=[4, 4, 0, 0],
                bar_size=40,
                name="NCR Average",
            ),
            rx.recharts.bar(
                data_key="Target",
                fill=AnalyticsState.target_color,
                radius=[4, 4, 0, 0],
                bar_size=40,
                name="QS Stars 5★ Target",
            ),
            data=AnalyticsState.learning_experience_comparison_data,
            width="100%",
            height=300,
            margin={"left": -20, "right": 0, "top": 0, "bottom": 0},
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def sustainability_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h4(
            "Sustainability Comparison",
            class_name="text-base font-semibold text-gray-800 mb-4",
        ),
        chart_legend(),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(
                horizontal=True, vertical=False, class_name="opacity-25"
            ),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.x_axis(
                data_key="metric",
                axis_line=False,
                tick_line=False,
                custom_attrs={"fontSize": "12px", "fontWeight": "600"},
                tick_margin=10,
            ),
            rx.recharts.y_axis(
                axis_line=False, tick_line=False, custom_attrs={"fontSize": "12px"}
            ),
            rx.recharts.bar(
                data_key="You",
                fill=AnalyticsState.your_color,
                radius=[4, 4, 0, 0],
                bar_size=40,
                name="Your Institution",
            ),
            rx.recharts.bar(
                data_key="NCR Avg",
                fill=AnalyticsState.ncr_average_color,
                radius=[4, 4, 0, 0],
                bar_size=40,
                name="NCR Average",
            ),
            rx.recharts.bar(
                data_key="Target",
                fill=AnalyticsState.target_color,
                radius=[4, 4, 0, 0],
                bar_size=40,
                name="QS Stars 5★ Target",
            ),
            data=AnalyticsState.sustainability_comparison_data,
            width="100%",
            height=300,
            margin={"left": -20, "right": 0, "top": 0, "bottom": 0},
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def loading_overlay(text: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.image(
                    src="https://chedcar.com/wp-content/uploads/2020/09/Commission_on_Higher_Education_CHEd.svg_.png",
                    class_name="h-16 w-16 mx-auto mb-6 animate-pulse",
                ),
                rx.el.div(
                    class_name="h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"
                ),
                rx.el.h3(text, class_name="text-xl font-bold text-gray-900 mb-2"),
                rx.el.p(
                    "Synthesizing performance metrics...",
                    class_name="text-gray-500 animate-pulse",
                ),
                class_name="bg-white p-12 rounded-[2.5rem] shadow-2xl text-center max-w-sm w-full border border-gray-100",
            ),
            class_name="fixed inset-0 z-[500] flex items-center justify-center bg-gray-50/80 backdrop-blur-md",
        ),
        class_name="relative",
    )


def analytics_content_ui() -> rx.Component:
    """The main visualization layout for institution performance.
    Combines score cards, comparison charts, and AI-powered advice.
    """
    return rx.el.div(
        rx.cond(
            AnalyticsState.is_loading,
            rx.el.div(
                rx.el.div(
                    class_name="h-full w-full bg-gradient-to-r from-blue-600 via-indigo-500 to-blue-600 animate-slide-progress"
                ),
                class_name="absolute top-0 left-0 w-full h-1 overflow-hidden z-[60]",
            ),
        ),
        rx.cond(
            AnalyticsState.is_loading,
            loading_overlay("Loading Analytics..."),
            rx.fragment(),
        ),
        rx.cond(
            AnalyticsState.review_status == "For Review",
            rx.el.div(
                rx.el.div(
                    rx.icon("info", class_name="h-5 w-5 text-blue-600 mr-3"),
                    rx.el.p(
                        "This assessment is currently under formal verification and audit by CHED. Analytics reflect provisional data.",
                        class_name="text-sm font-semibold text-blue-800",
                    ),
                    class_name="flex items-center",
                ),
                class_name="bg-blue-50 border border-blue-100 px-6 py-3 rounded-xl mb-6 animate-in fade-in duration-500",
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "Performance Analytics",
                        class_name="text-2xl font-bold text-slate-900 tracking-tight",
                    ),
                    rx.el.p(
                        "Real-time readiness assessment based on your data entries against regional and international benchmarks.",
                        class_name="text-sm text-slate-500 mt-1 font-medium",
                    ),
                    class_name="flex-1",
                ),
                rx.el.div(
                    rx.match(
                        AnalyticsState.review_status,
                        (
                            "For Review",
                            rx.el.div(
                                rx.el.div(
                                    class_name="h-2 w-2 rounded-full bg-blue-400 animate-pulse mr-2"
                                ),
                                rx.el.span(
                                    "Under Review",
                                    class_name="text-xs font-bold text-blue-700 uppercase",
                                ),
                                class_name="flex items-center bg-blue-50 px-3 py-1.5 rounded-full border border-blue-200",
                            ),
                        ),
                        (
                            "Reviewed",
                            rx.el.div(
                                rx.icon(
                                    "circle_pause",
                                    class_name="h-3.5 w-3.5 text-emerald-600 mr-2",
                                ),
                                rx.el.span(
                                    "Approved",
                                    class_name="text-xs font-bold text-emerald-700 uppercase",
                                ),
                                class_name="flex items-center bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-200",
                            ),
                        ),
                        (
                            "Declined",
                            rx.el.div(
                                rx.icon(
                                    "gpu", class_name="h-3.5 w-3.5 text-rose-600 mr-2"
                                ),
                                rx.el.span(
                                    "Declined",
                                    class_name="text-xs font-bold text-rose-700 uppercase",
                                ),
                                class_name="flex items-center bg-rose-50 px-3 py-1.5 rounded-full border border-rose-200",
                            ),
                        ),
                        (
                            "In Progress",
                            rx.el.div(
                                rx.el.div(
                                    class_name="h-2 w-2 rounded-full bg-amber-400 animate-pulse mr-2"
                                ),
                                rx.el.span(
                                    "In Progress",
                                    class_name="text-xs font-bold text-amber-700 uppercase",
                                ),
                                class_name="flex items-center bg-amber-50 px-3 py-1.5 rounded-full border border-amber-200",
                            ),
                        ),
                        rx.el.div(
                            rx.el.span(
                                "Pending",
                                class_name="text-xs font-bold text-slate-500 uppercase",
                            ),
                            class_name="flex items-center bg-slate-100 px-3 py-1.5 rounded-full border border-slate-200",
                        ),
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex items-start justify-between",
            ),
            class_name="mb-8",
        ),
        rx.el.div(
            performance_pie_card(
                title="Overall Readiness",
                score=AnalyticsState.overall_score,
                color="#1d4ed8",
                icon="bar-chart-2",
            ),
            performance_pie_card(
                title="Research & Discovery (50%)",
                score=AnalyticsState.research_score,
                color="#7c3aed",
                icon="microscope",
            ),
            performance_pie_card(
                title="Employability (20%)",
                score=AnalyticsState.employability_score,
                color="#059669",
                icon="briefcase",
            ),
            performance_pie_card(
                title="Global Engagement (15%)",
                score=AnalyticsState.global_engagement_score,
                color="#0284c7",
                icon="globe",
            ),
            performance_pie_card(
                title="Learning Experience (10%)",
                score=AnalyticsState.learning_experience_score,
                color="#4f46e5",
                icon="graduation-cap",
            ),
            performance_pie_card(
                title="Sustainability (5%)",
                score=AnalyticsState.sustainability_score,
                color="#16a34a",
                icon="leaf",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8",
        ),
        rx.el.div(
            rx.el.div(research_chart(), class_name="w-full"),
            rx.el.div(employability_chart(), class_name="w-full"),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6",
        ),
        rx.el.div(
            rx.el.div(global_engagement_chart(), class_name="w-full"),
            rx.el.div(learning_experience_chart(), class_name="w-full"),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6",
        ),
        rx.el.div(
            rx.el.div(sustainability_chart(), class_name="w-full lg:w-1/2"),
            class_name="grid grid-cols-1 gap-6 mb-8",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "AI-Powered Strategic Recommendations",
                    class_name="text-lg font-bold text-gray-900",
                ),
                rx.el.p(
                    "Personalized recommendations generated using Google AI based on your institution's performance data.",
                    class_name="text-sm text-gray-500 mt-1",
                ),
                class_name="mb-4",
            ),
            rx.cond(
                AnalyticsState.is_generating_recommendations,
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            class_name="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"
                        ),
                        rx.el.p(
                            "Generating AI recommendations...",
                            class_name="text-sm text-gray-600 mt-3 text-center",
                        ),
                        class_name="flex flex-col items-center justify-center p-12 bg-white rounded-xl border border-gray-200",
                    )
                ),
                rx.cond(
                    AnalyticsState.ai_recommendations.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            AnalyticsState.ai_recommendations,
                            lambda rec: rx.el.div(
                                rx.icon(
                                    rec["icon"],
                                    class_name=f"h-6 w-6 {rec['color_class']} shrink-0 mt-1",
                                ),
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.h5(
                                            rec["title"],
                                            class_name="font-bold text-gray-900 text-sm leading-tight whitespace-normal break-words flex-1",
                                            style={"wordSpacing": "normal"},
                                        ),
                                        rx.el.span(
                                            rec["priority"],
                                            class_name=f"shrink-0 text-[10px] px-2 py-0.5 rounded-full {rec['bg_class']} {rec['color_class']} font-bold border border-current",
                                        ),
                                        class_name="flex items-start justify-between gap-3 mb-2",
                                    ),
                                    rx.el.p(
                                        rec["description"],
                                        class_name="text-sm text-gray-600 leading-relaxed whitespace-normal break-words",
                                        style={"wordSpacing": "normal"},
                                    ),
                                    rx.el.div(
                                        rx.el.span(
                                            rec["category"],
                                            class_name="text-[10px] font-bold text-gray-400 uppercase tracking-wider",
                                        ),
                                        class_name="mt-4 pt-3 border-t border-gray-100/50",
                                    ),
                                    class_name="flex-1 min-w-0",
                                ),
                                class_name=f"flex flex-row items-start gap-4 p-5 {rec['bg_class']} border rounded-2xl min-h-[160px] shadow-sm",
                            ),
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "No recommendations available. Please ensure all data fields are filled.",
                            class_name="text-sm text-gray-500 text-center p-8",
                        ),
                        class_name="bg-white rounded-xl border border-gray-200",
                    ),
                ),
            ),
        ),
        class_name="max-w-6xl mx-auto",
    )