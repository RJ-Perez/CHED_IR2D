import reflex as rx
from app.states.post_assessment_state import PostAssessmentState, IndicatorScore
from app.components.design_system import DS, ds_card, ds_button, ds_input


def star_rating_display(stars: int, label: str, size: str = "md") -> rx.Component:
    """Displays a row of stars with enhanced styling."""
    star_size = rx.cond(size == "md", "h-6 w-6", "h-10 w-10")
    return rx.el.div(
        rx.el.p(
            label,
            class_name="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2",
        ),
        rx.el.div(
            rx.foreach(
                rx.Var.range(5),
                lambda i: rx.icon(
                    "star",
                    class_name=rx.cond(
                        i < stars,
                        f"{star_size} text-yellow-400 fill-yellow-400 mr-1 drop-shadow-sm transition-all duration-300 transform hover:scale-110",
                        f"{star_size} text-gray-200 mr-1 transition-all duration-300",
                    ),
                ),
            ),
            class_name="flex items-center",
        ),
        class_name="flex flex-col",
    )


def audit_clock_card() -> rx.Component:
    """Displays audit validity and status with enhanced visuals."""
    return ds_card(
        rx.el.div(
            rx.el.div(
                rx.icon("timer", class_name="h-6 w-6 text-blue-600 mr-2"),
                rx.el.h3("Audit Validity", class_name=DS.H3),
                class_name="flex items-center mb-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p("Status", class_name=DS.LABEL),
                    rx.el.div(
                        rx.el.span(
                            PostAssessmentState.audit_status,
                            class_name=f"px-3 py-1 rounded-full text-xs font-bold bg-{PostAssessmentState.audit_status_color}-100 text-{PostAssessmentState.audit_status_color}-700 border border-{PostAssessmentState.audit_status_color}-200",
                        ),
                        class_name="mt-1",
                    ),
                ),
                rx.el.div(
                    rx.el.p("Days Remaining", class_name=DS.LABEL),
                    rx.el.h4(
                        f"{PostAssessmentState.days_until_expiry} Days",
                        class_name="text-xl font-bold text-gray-900 mt-1",
                    ),
                ),
                class_name="flex justify-between items-end mb-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        style={
                            "width": f"{PostAssessmentState.audit_time_elapsed_percent}%"
                        },
                        class_name="h-full bg-blue-600 rounded-full transition-all duration-1000",
                    ),
                    class_name="h-2 w-full bg-gray-100 rounded-full overflow-hidden",
                ),
                rx.el.div(
                    rx.el.span("Start", class_name="text-[10px] text-gray-400"),
                    rx.el.span("Expiry", class_name="text-[10px] text-gray-400"),
                    class_name="flex justify-between mt-1 mb-6",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.label("Start Date", class_name=DS.LABEL),
                    rx.el.input(
                        type="date",
                        on_change=PostAssessmentState.set_audit_start_date,
                        class_name="w-full text-xs border-b border-gray-200 focus:border-blue-500 outline-none py-1 bg-transparent text-gray-700",
                        default_value=PostAssessmentState.audit_start_date,
                    ),
                    class_name="mb-2",
                ),
                rx.el.div(
                    rx.el.label("Validity Date", class_name=DS.LABEL),
                    rx.el.input(
                        type="date",
                        on_change=PostAssessmentState.set_audit_validity_date,
                        class_name="w-full text-xs border-b border-gray-200 focus:border-blue-500 outline-none py-1 bg-transparent text-gray-700",
                        default_value=PostAssessmentState.audit_validity_date,
                    ),
                    class_name="mb-2",
                ),
                rx.el.div(
                    rx.el.label("Methodology Version", class_name=DS.LABEL),
                    rx.el.input(
                        on_change=PostAssessmentState.set_methodology_version,
                        class_name="w-full text-xs border-b border-gray-200 focus:border-blue-500 outline-none py-1 bg-transparent text-gray-700 font-medium",
                        default_value=PostAssessmentState.methodology_version,
                        placeholder="e.g. 5.2",
                    ),
                ),
                class_name="space-y-3 bg-gray-50 p-4 rounded-xl border border-gray-100",
            ),
            ds_button(
                "Update Metadata",
                variant="secondary",
                size="sm",
                on_click=PostAssessmentState.save_audit_metadata,
                loading=PostAssessmentState.is_saving,
                class_name="w-full mt-4",
            ),
            class_name="h-full flex flex-col justify-between",
        )
    )


def overall_rating_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                "Overall Star Rating",
                class_name="text-sm font-bold text-white uppercase tracking-widest opacity-80 mb-4",
            ),
            rx.el.div(
                rx.el.h1(
                    PostAssessmentState.overall_stars,
                    class_name="text-8xl font-black text-white mr-6 tracking-tighter",
                ),
                rx.el.div(
                    rx.icon(
                        "star",
                        class_name="h-20 w-20 text-yellow-400 fill-yellow-400 drop-shadow-md",
                    ),
                    class_name="animate-pulse",
                ),
                class_name="flex items-center justify-center",
            ),
            rx.el.p(
                "Based on QS Stars Methodology",
                class_name="text-xs text-blue-200 mt-4 font-medium",
            ),
            class_name="flex flex-col items-center justify-center h-full py-8",
        ),
        class_name="bg-gradient-to-br from-blue-900 to-indigo-800 rounded-2xl p-6 shadow-xl text-center h-full flex flex-col justify-center border border-blue-700 relative overflow-hidden",
    )


def category_stars_section() -> rx.Component:
    return rx.el.div(
        ds_card(
            star_rating_display(PostAssessmentState.teaching_stars, "Teaching", "lg"),
            class_name="flex items-center justify-center p-8 hover:shadow-md transition-shadow",
        ),
        ds_card(
            star_rating_display(
                PostAssessmentState.employability_stars, "Employability", "lg"
            ),
            class_name="flex items-center justify-center p-8 hover:shadow-md transition-shadow",
        ),
        ds_card(
            star_rating_display(
                PostAssessmentState.academic_development_stars, "Academic Dev.", "lg"
            ),
            class_name="flex items-center justify-center p-8 hover:shadow-md transition-shadow",
        ),
        ds_card(
            star_rating_display(
                PostAssessmentState.inclusiveness_stars, "Inclusiveness", "lg"
            ),
            class_name="flex items-center justify-center p-8 hover:shadow-md transition-shadow",
        ),
        class_name="grid grid-cols-2 md:grid-cols-4 gap-6",
    )


def indicator_row(ind: IndicatorScore) -> rx.Component:
    percentage = ind["points_achieved"] / ind["max_score"] * 100
    is_weakness = percentage < 50
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        ind["indicator_name"],
                        class_name="font-bold text-gray-900 text-base",
                    ),
                    rx.cond(
                        is_weakness,
                        rx.el.span(
                            "Attention Required",
                            class_name="text-[10px] font-bold bg-red-100 text-red-600 px-2.5 py-1 rounded-full ml-3 border border-red-200",
                        ),
                        rx.fragment(),
                    ),
                    class_name="flex items-center mb-3",
                ),
                rx.el.div(
                    rx.el.div(
                        class_name=f"h-2.5 rounded-full {rx.cond(is_weakness, 'bg-red-500', 'bg-blue-600')} transition-all duration-500",
                        style={"width": f"{percentage}%"},
                    ),
                    class_name="w-full bg-gray-100 rounded-full h-2.5 mb-2",
                ),
                rx.el.div(
                    rx.el.span(
                        f"{ind['points_achieved']} / {ind['max_score']} pts",
                        class_name="text-xs font-bold text-gray-700",
                    ),
                    rx.el.span(
                        f"({percentage:.1f}%)",
                        class_name="text-xs font-medium text-gray-500 ml-1",
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex-1 mr-8 min-w-[300px]",
            ),
            rx.el.div(class_name="w-px bg-gray-100 h-24 hidden md:block mx-4"),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Target Score",
                            class_name="text-[10px] font-bold text-gray-400 uppercase mb-1.5 block",
                        ),
                        rx.el.div(
                            rx.el.input(
                                type="number",
                                placeholder="Target",
                                default_value=ind["target_score"],
                                on_change=lambda val: PostAssessmentState.set_indicator_target(
                                    ind["indicator_name"], val
                                ),
                                class_name="w-24 text-sm font-bold border border-gray-200 rounded-lg p-2.5 text-center focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition-all",
                            ),
                            rx.el.span(
                                "pts",
                                class_name="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 font-medium",
                            ),
                            class_name="relative",
                        ),
                        class_name="flex flex-col mr-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Action Plan Notes",
                            class_name="text-[10px] font-bold text-gray-400 uppercase mb-1.5 block",
                        ),
                        rx.el.textarea(
                            placeholder="Strategies to improve score...",
                            default_value=ind["notes"],
                            on_change=lambda val: PostAssessmentState.set_indicator_notes(
                                ind["indicator_name"], val
                            ),
                            class_name="w-full md:w-64 h-[42px] min-h-[42px] text-sm border border-gray-200 rounded-lg p-2 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none resize-none transition-all",
                        ),
                        class_name="flex flex-col flex-1",
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.icon("save", class_name="h-4 w-4"),
                            on_click=lambda: PostAssessmentState.save_indicator_plan(
                                ind["indicator_name"]
                            ),
                            class_name="p-2.5 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors mt-auto mb-px",
                            title="Save Plan",
                        ),
                        class_name="flex flex-col justify-end ml-2",
                    ),
                    class_name="flex items-start w-full md:w-auto",
                ),
                class_name="flex-1",
            ),
            class_name="flex flex-col md:flex-row items-start md:items-center justify-between p-6 hover:bg-slate-50 transition-colors gap-6",
        ),
        class_name="border-b border-gray-100 last:border-0",
    )


def category_gap_analysis(category: str) -> rx.Component:
    """Collapsible category section using HTML details/summary for simplicity and accessibility."""
    return rx.el.div(
        rx.el.details(
            rx.el.summary(
                rx.el.span(category, class_name="text-lg font-bold text-gray-800"),
                class_name="cursor-pointer p-6 bg-white hover:bg-gray-50 rounded-xl list-none flex items-center justify-between outline-none border border-gray-200 shadow-sm transition-all marker:content-none",
            ),
            rx.el.div(
                rx.foreach(
                    PostAssessmentState.indicator_scores,
                    lambda ind: rx.cond(
                        ind["category"] == category, indicator_row(ind), rx.fragment()
                    ),
                ),
                class_name="bg-white border-x border-b border-gray-200 rounded-b-xl -mt-2 pt-2",
            ),
            open=True,
            class_name="group",
        ),
        class_name="mb-6",
    )


def weakness_summary_banner() -> rx.Component:
    return rx.cond(
        PostAssessmentState.weak_indicators_count > 0,
        rx.el.div(
            rx.el.div(
                rx.icon(
                    "triangle-alert",
                    class_name="h-6 w-6 text-amber-600 mr-3 flex-shrink-0 mt-0.5",
                ),
                rx.el.div(
                    rx.el.h4(
                        f"{PostAssessmentState.weak_indicators_count} Indicators Require Attention",
                        class_name="text-base font-bold text-amber-900",
                    ),
                    rx.el.p(
                        "These indicators are currently performing below the 50% threshold. Review the gap analysis below to plan corrective actions for the next audit cycle.",
                        class_name="text-sm text-amber-800 mt-1 leading-relaxed",
                    ),
                ),
                class_name="flex items-start",
            ),
            class_name="bg-amber-50 border border-amber-200 rounded-xl p-5 mb-8 animate-in fade-in slide-in-from-top-2 shadow-sm",
        ),
    )


def analytics_score_item(label: str, score: int, icon: str, color: str) -> rx.Component:
    """Helper for displaying analytics scores in the insights card."""
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"h-4 w-4 {color} mr-2"),
            rx.el.span(label, class_name="text-sm font-medium text-gray-700"),
            class_name="flex items-center",
        ),
        rx.el.div(
            rx.el.span(score, class_name="text-sm font-bold text-gray-900 mr-1"),
            rx.el.span("/ 100", class_name="text-xs text-gray-400"),
            rx.cond(
                score < 50,
                rx.icon("trending-down", class_name="h-3 w-3 text-red-500 ml-2 inline"),
                rx.icon(
                    "trending-up", class_name="h-3 w-3 text-emerald-500 ml-2 inline"
                ),
            ),
            class_name="flex items-center",
        ),
        class_name="flex items-center justify-between py-2 border-b border-gray-50 last:border-0",
    )


def analytics_insights_card() -> rx.Component:
    """New card displaying fetched analytics data and AI recommendations."""
    return rx.cond(
        PostAssessmentState.last_analytics_sync != "",
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("line-chart", class_name="h-5 w-5 text-indigo-600 mr-2"),
                    rx.el.h3(
                        "Analytics-Driven Insights",
                        class_name="text-lg font-bold text-gray-900",
                    ),
                    class_name="flex items-center mb-4",
                ),
                rx.el.div(
                    analytics_score_item(
                        "Research & Discovery",
                        PostAssessmentState.analytics_research_score,
                        "microscope",
                        "text-purple-600",
                    ),
                    analytics_score_item(
                        "Employability",
                        PostAssessmentState.analytics_employability_score,
                        "briefcase",
                        "text-emerald-600",
                    ),
                    analytics_score_item(
                        "Global Engagement",
                        PostAssessmentState.analytics_global_engagement_score,
                        "globe",
                        "text-blue-600",
                    ),
                    analytics_score_item(
                        "Learning Experience",
                        PostAssessmentState.analytics_learning_experience_score,
                        "graduation-cap",
                        "text-indigo-600",
                    ),
                    class_name="bg-gray-50 rounded-xl p-4 mb-6",
                ),
                rx.el.h4(
                    "Strategic Recommendations",
                    class_name="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3",
                ),
                rx.el.div(
                    rx.foreach(
                        PostAssessmentState.analytics_recommendations,
                        lambda rec: rx.el.div(
                            rx.icon(
                                "lightbulb",
                                class_name="h-4 w-4 text-amber-500 mr-2 flex-shrink-0 mt-0.5",
                            ),
                            rx.el.div(
                                rx.el.p(
                                    rec["title"],
                                    class_name="text-sm font-bold text-gray-800",
                                ),
                                rx.el.p(
                                    rec["description"],
                                    class_name="text-xs text-gray-600 mt-1 leading-snug",
                                ),
                            ),
                            class_name="flex items-start p-3 bg-white border border-gray-100 rounded-lg shadow-sm",
                        ),
                    ),
                    class_name="space-y-2 max-h-[300px] overflow-y-auto pr-1",
                ),
            ),
            class_name="bg-white rounded-2xl p-6 border border-indigo-100 shadow-lg shadow-indigo-50/50 h-full",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("refresh-cw", class_name="h-8 w-8 text-gray-300 mb-3"),
                rx.el.p(
                    "Sync to view Analytics Insights",
                    class_name="text-sm font-semibold text-gray-500",
                ),
                rx.el.p(
                    "Pull scores and AI advice from the Analytics module.",
                    class_name="text-xs text-gray-400 mt-1 text-center max-w-[200px]",
                ),
                class_name="flex flex-col items-center justify-center h-full min-h-[300px]",
            ),
            class_name="bg-gray-50 rounded-2xl p-6 border border-dashed border-gray-200 h-full",
        ),
    )


def post_assessment_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Post-Assessment Insights",
                    class_name="text-3xl font-bold text-gray-900",
                ),
                rx.el.p(
                    "Review audit results, identify gaps, and plan for the next cycle.",
                    class_name="text-gray-600 mt-2 text-lg",
                ),
            ),
            rx.el.div(
                rx.el.button(
                    rx.cond(
                        PostAssessmentState.is_loading,
                        rx.el.div(
                            rx.el.div(
                                class_name="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600 mr-2"
                            ),
                            "Syncing...",
                            class_name="flex items-center",
                        ),
                        rx.el.div(
                            rx.icon("refresh-cw", class_name="h-4 w-4 mr-2"),
                            "Sync from Analytics",
                            class_name="flex items-center",
                        ),
                    ),
                    on_click=PostAssessmentState.sync_from_analytics,
                    disabled=PostAssessmentState.is_loading,
                    class_name="text-sm text-indigo-700 font-bold bg-indigo-50 px-4 py-2.5 rounded-xl hover:bg-indigo-100 transition-colors border border-indigo-200 shadow-sm mr-2",
                ),
                rx.el.button(
                    "Simulate Audit Data (Demo)",
                    on_click=PostAssessmentState.simulate_audit_update,
                    class_name="text-sm text-blue-700 font-bold bg-blue-50 px-4 py-2.5 rounded-xl hover:bg-blue-100 transition-colors border border-blue-200 shadow-sm",
                ),
                class_name="flex items-center",
            ),
            class_name="flex flex-col sm:flex-row sm:justify-between sm:items-start mb-10 gap-4",
        ),
        weakness_summary_banner(),
        rx.el.div(
            rx.el.div(overall_rating_card(), class_name="lg:col-span-1"),
            rx.el.div(audit_clock_card(), class_name="lg:col-span-1"),
            rx.el.div(analytics_insights_card(), class_name="lg:col-span-1"),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10 min-h-[400px]",
        ),
        rx.el.div(category_stars_section(), class_name="mb-10"),
        rx.el.div(
            rx.el.h2(
                "Gap Analysis & Action Planning",
                class_name="text-xl font-bold text-gray-900 mb-6",
            ),
            category_gap_analysis("Teaching"),
            category_gap_analysis("Employability"),
            category_gap_analysis("Academic Development"),
            category_gap_analysis("Inclusiveness"),
            class_name="mb-20",
        ),
        class_name="max-w-7xl mx-auto pb-20 px-4 sm:px-6",
    )