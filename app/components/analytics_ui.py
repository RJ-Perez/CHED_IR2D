import reflex as rx
from app.states.analytics_state import AnalyticsState

TOOLTIP_PROPS = {
    "content_style": {
        "background": "white",
        "borderColor": "#e2e8f0",
        "borderRadius": "0.5rem",
        "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
        "padding": "0.5rem",
    },
    "item_style": {"color": "#475569", "fontSize": "0.875rem"},
    "separator": "",
}


def score_card(title: str, score: int, icon: str, color_class: str) -> rx.Component:
    """Displays a score metric in a card."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(title, class_name="text-sm font-medium text-gray-500"),
                rx.el.h3(
                    f"{score}/100", class_name="text-2xl font-bold text-gray-900 mt-1"
                ),
            ),
            rx.el.div(
                rx.icon(icon, class_name=f"h-8 w-8 {color_class}"),
                class_name="p-3 bg-gray-50 rounded-lg",
            ),
            class_name="flex justify-between items-start",
        ),
        rx.el.div(
            rx.el.div(
                class_name=f"h-2 rounded-full {color_class.replace('text-', 'bg-')}",
                style={"width": f"{score}%"},
            ),
            class_name="w-full bg-gray-100 rounded-full h-2 mt-4",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
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
            rx.el.span("Target Benchmark", class_name="text-xs text-gray-600"),
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
                name="Target",
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
                name="Target",
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
                name="Target",
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
                name="Target",
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
                name="Target",
            ),
            data=AnalyticsState.sustainability_comparison_data,
            width="100%",
            height=300,
            margin={"left": -20, "right": 0, "top": 0, "bottom": 0},
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def analytics_content_ui() -> rx.Component:
    """Main Analytics Dashboard View."""
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Performance Analytics", class_name="text-2xl font-bold text-gray-900"
            ),
            rx.el.p(
                "Real-time readiness assessment based on your data entries against regional and international benchmarks.",
                class_name="text-gray-600 mt-1",
            ),
            class_name="mb-8",
        ),
        rx.el.div(
            score_card(
                "Overall Readiness",
                AnalyticsState.overall_score,
                "bar-chart-2",
                "text-blue-600",
            ),
            score_card(
                "Research & Discovery (50%)",
                AnalyticsState.research_score,
                "microscope",
                "text-purple-600",
            ),
            score_card(
                "Employability (20%)",
                AnalyticsState.employability_score,
                "briefcase",
                "text-emerald-600",
            ),
            score_card(
                "Global Engagement (15%)",
                AnalyticsState.global_engagement_score,
                "globe",
                "text-blue-600",
            ),
            score_card(
                "Learning Experience (10%)",
                AnalyticsState.learning_experience_score,
                "graduation-cap",
                "text-indigo-600",
            ),
            score_card(
                "Sustainability (5%)",
                AnalyticsState.sustainability_score,
                "leaf",
                "text-green-600",
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
                    ),
                ),
                rx.cond(
                    AnalyticsState.ai_recommendations.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            AnalyticsState.ai_recommendations,
                            lambda rec: rx.el.div(
                                rx.icon(
                                    rec["icon"],
                                    class_name=f"h-6 w-6 {rec['color_class']} mr-4 flex-shrink-0",
                                ),
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.h5(
                                            rec["title"],
                                            class_name="font-semibold text-gray-900",
                                        ),
                                        rx.el.span(
                                            rec["priority"],
                                            class_name=f"ml-2 text-xs px-2 py-1 rounded-full {rec['bg_class']} {rec['color_class']} font-medium",
                                        ),
                                        class_name="flex items-center",
                                    ),
                                    rx.el.p(
                                        rec["description"],
                                        class_name="text-sm text-gray-600 mt-2",
                                    ),
                                    rx.el.span(
                                        rec["category"],
                                        class_name="text-xs text-gray-400 mt-2 block",
                                    ),
                                ),
                                class_name=f"flex items-start p-4 {rec['bg_class']} border rounded-xl",
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