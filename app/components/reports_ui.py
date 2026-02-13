import reflex as rx
from app.states.reports_state import ReportsState, ReportItem
from app.components.analytics_ui import TOOLTIP_PROPS
from app.components.design_system import DS, ds_card


def score_badge(score: int) -> rx.Component:
    """Visual badge for scores with color coding."""
    from app.components.design_system import ds_badge

    return rx.cond(
        score >= 80,
        ds_badge(label=f"{score}%", variant="success"),
        rx.cond(
            score >= 60,
            ds_badge(label=f"{score}%", variant="warning"),
            rx.cond(
                score > 0,
                ds_badge(label=f"{score}%", variant="error"),
                ds_badge(label="N/A", variant="neutral"),
            ),
        ),
    )


def report_status_badge(status: str) -> rx.Component:
    """Status badge component with review states."""
    return rx.match(
        status,
        (
            "Reviewed",
            rx.el.div(
                rx.icon("check", class_name="h-3 w-3 mr-1"),
                rx.el.span("Reviewed"),
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 w-fit",
            ),
        ),
        (
            "Declined",
            rx.el.div(
                rx.icon("x", class_name="h-3 w-3 mr-1"),
                rx.el.span("Declined"),
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800 w-fit",
            ),
        ),
        (
            "For Review",
            rx.el.span(
                "For Review",
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 w-fit",
            ),
        ),
        (
            "In Progress",
            rx.el.span(
                "In Progress",
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 w-fit",
            ),
        ),
        (
            "Pending",
            rx.el.span(
                "Pending",
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 w-fit",
            ),
        ),
        (
            "Incomplete",
            rx.el.span(
                "Incomplete",
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 w-fit",
            ),
        ),
        rx.el.span(
            "In Progress",
            class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600 w-fit",
        ),
    )


def evidence_file_item(file_path: str) -> rx.Component:
    """Renders a single evidence file link with appropriate icon."""
    file_name = file_path.split("/")[-1]
    is_pdf = file_path.lower().endswith(".pdf")
    icon_name = rx.cond(is_pdf, "file-text", "file-image")
    icon_color = rx.cond(is_pdf, "text-red-500", "text-blue-500")
    return rx.el.div(
        rx.icon(icon_name, class_name=f"h-4 w-4 mr-2 {icon_color}"),
        rx.el.a(
            file_name,
            href=rx.get_upload_url(file_path),
            target="_blank",
            class_name="text-xs text-blue-600 hover:text-blue-800 hover:underline truncate max-w-[150px]",
        ),
        class_name="flex items-center p-1 bg-gray-50 rounded border border-gray-100",
    )


def evidence_list_section(files: list[str]) -> rx.Component:
    """Renders the list of evidence files or an empty state."""
    return rx.el.div(
        rx.el.p(
            "Evidence Files:",
            class_name="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1",
        ),
        rx.cond(
            files.length() > 0,
            rx.el.div(
                rx.foreach(files, lambda f: evidence_file_item(f)),
                class_name="grid grid-cols-1 gap-1",
            ),
            rx.el.p("No evidence uploaded.", class_name="text-xs text-gray-400 italic"),
        ),
        class_name="mt-2 pt-2 border-t border-gray-100",
    )


def dimension_score_row(label: str, score: int) -> rx.Component:
    """Helper component to render a single dimension row with aligned label and badge using standard tokens."""
    return rx.el.div(
        rx.el.span(label, class_name="text-xs font-medium text-gray-700 min-w-[200px]"),
        rx.el.div(
            score_badge(score), class_name="flex-1 flex justify-end min-w-[60px]"
        ),
        class_name="flex items-center justify-between gap-4 py-1.5 border-b border-gray-50 last:border-0",
    )


@rx.memo
def report_table_row(report: ReportItem) -> rx.Component:
    """Row component for the Reports table."""
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.p(report["name"], class_name="text-sm font-medium text-gray-900"),
                evidence_list_section(report["evidence_files"]),
                class_name="flex flex-col",
            ),
            class_name="px-6 py-4",
        ),
        rx.el.td(
            score_badge(report["overall_score"]),
            class_name="px-6 py-4 whitespace-nowrap text-center",
        ),
        rx.el.td(
            rx.el.div(
                dimension_score_row(
                    "Research & Discovery (50%)", report["research_score"]
                ),
                dimension_score_row(
                    "Employability & Outcomes (20%)", report["employability_score"]
                ),
                dimension_score_row(
                    "Global Engagement (15%)", report["global_engagement_score"]
                ),
                dimension_score_row(
                    "Learning Experience (10%)", report["learning_experience_score"]
                ),
                dimension_score_row(
                    "Sustainability (5%)", report["sustainability_score"]
                ),
                class_name="flex flex-col divide-y divide-gray-50 w-full max-w-[280px]",
            ),
            class_name="px-6 py-4",
        ),
        rx.el.td(
            report_status_badge(report["status"]),
            class_name="px-6 py-4 whitespace-nowrap text-center",
        ),
        rx.el.td(
            rx.el.span(report["last_generated"], class_name="text-sm text-gray-500"),
            class_name="px-6 py-4 whitespace-nowrap text-center",
        ),
        rx.el.td(
            rx.el.div(
                rx.cond(
                    report["status"] == "For Review",
                    rx.el.button(
                        rx.icon("clipboard-check", class_name="h-4 w-4 mr-1"),
                        "Review",
                        on_click=ReportsState.open_review_modal(report["id"]),
                        class_name="inline-flex items-center px-3 py-1.5 border border-blue-300 shadow-sm text-xs font-bold rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 mr-2",
                    ),
                ),
                rx.el.button(
                    rx.icon("download", class_name="h-4 w-4 mr-1"),
                    "CSV",
                    on_click=ReportsState.download_report(report["id"]),
                    class_name="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="h-4 w-4 mr-1"),
                    "Delete",
                    on_click=ReportsState.confirm_delete_report(
                        report["id"], report["name"]
                    ),
                    class_name="inline-flex items-center px-3 py-1.5 border border-red-300 shadow-sm text-xs font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 ml-2",
                ),
                class_name="flex items-center justify-end",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right",
        ),
        class_name="hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0",
    )


def report_recommendation_card(rec: dict) -> rx.Component:
    """Card component for AI recommendations in reports."""
    return rx.el.div(
        rx.icon(
            rec["icon"], class_name=f"h-6 w-6 {rec['color_class']} mr-4 flex-shrink-0"
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h5(
                    rec["title"],
                    class_name="font-bold text-gray-900 whitespace-normal break-words",
                ),
                rx.el.span(
                    rec["priority"],
                    class_name=f"ml-2 text-[10px] px-2 py-0.5 rounded-full {rec['bg_class']} {rec['color_class']} font-bold border border-current uppercase",
                ),
                class_name="flex items-start justify-between gap-2 mb-2",
            ),
            rx.el.p(
                rec["description"],
                class_name="text-sm text-gray-600 leading-relaxed whitespace-normal break-words",
            ),
            rx.el.span(
                rec["category"],
                class_name="text-[10px] font-bold text-gray-400 uppercase tracking-widest mt-4 block pt-2 border-t border-gray-100/50",
            ),
        ),
        class_name=f"flex items-start p-4 {rec['bg_class']} border rounded-xl",
    )


def ai_analysis_section() -> rx.Component:
    """Section for AI-powered strategic recommendations."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("sparkles", class_name="h-6 w-6 text-purple-600 mr-2"),
                rx.el.h3(
                    "AI-Powered Strategic Recommendations",
                    class_name="text-xl font-bold text-gray-900",
                ),
                class_name="flex items-center mb-2",
            ),
            rx.el.p(
                "Select an institution to generate data-driven improvement strategies based on their assessment scores.",
                class_name="text-gray-600 mb-6",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.select(
                        rx.el.option("Select Institution for Analysis...", value=""),
                        rx.foreach(
                            ReportsState.reports,
                            lambda r: rx.el.option(r["name"], value=r["id"]),
                        ),
                        on_change=lambda val: ReportsState.select_report_for_analysis(
                            val
                        ),
                        value=ReportsState.selected_report_id,
                        class_name="w-full px-4 py-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-sm appearance-none cursor-pointer",
                    ),
                    rx.icon(
                        "chevron-down",
                        class_name="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none",
                    ),
                    class_name="relative w-full md:w-80",
                ),
                class_name="mb-8",
            ),
        ),
        rx.cond(
            ReportsState.selected_report_id != "",
            rx.cond(
                ReportsState.is_generating_report_recommendations,
                rx.el.div(
                    rx.el.div(
                        class_name="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"
                    ),
                    rx.el.p(
                        "Generating strategic insights...",
                        class_name="text-sm text-gray-600 mt-3 text-center",
                    ),
                    class_name="flex flex-col items-center justify-center p-12 bg-white rounded-xl border border-gray-200",
                ),
                rx.cond(
                    ReportsState.selected_report_recommendations.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            ReportsState.selected_report_recommendations,
                            report_recommendation_card,
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "No recommendations available for this report.",
                            class_name="text-sm text-gray-500 italic",
                        ),
                        class_name="p-8 text-center bg-gray-50 rounded-xl border border-gray-200",
                    ),
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("bar-chart-2", class_name="h-12 w-12 text-gray-300 mb-3"),
                    rx.el.p(
                        "Select an institution above to view AI recommendations",
                        class_name="text-gray-500 font-medium",
                    ),
                    class_name="flex flex-col items-center justify-center h-48",
                ),
                class_name="bg-white rounded-xl border border-dashed border-gray-300",
            ),
        ),
        class_name="mt-12 pt-8 border-t border-gray-200",
    )


def delete_report_modal() -> rx.Component:
    """Delete report confirmation modal component."""
    return rx.cond(
        ReportsState.show_delete_modal,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "triangle_alert",
                                class_name="h-12 w-12 text-red-600 mx-auto mb-4",
                            ),
                            rx.el.h3(
                                "Delete Report",
                                class_name="text-lg font-semibold text-gray-900 mb-2",
                            ),
                            rx.el.p(
                                rx.el.span(
                                    "Are you sure you want to delete the report for ",
                                    class_name="text-sm text-gray-600",
                                ),
                                rx.el.span(
                                    ReportsState.delete_confirm_name,
                                    class_name="text-sm font-semibold text-gray-900",
                                ),
                                rx.el.span(
                                    "? This action cannot be undone.",
                                    class_name="text-sm text-gray-600",
                                ),
                                class_name="mb-6",
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "Cancel",
                                    on_click=ReportsState.cancel_delete_report,
                                    class_name="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors",
                                ),
                                rx.el.button(
                                    "Delete",
                                    on_click=ReportsState.delete_report,
                                    class_name="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors",
                                ),
                                class_name="flex items-center justify-end gap-3",
                            ),
                            class_name="text-center",
                        ),
                        class_name="bg-white rounded-xl shadow-xl p-6 max-w-md w-full mx-4",
                    ),
                    class_name="flex items-start justify-center min-h-screen p-4 pt-24",
                ),
                class_name="fixed inset-0 bg-black bg-opacity-50 z-[100] flex items-start justify-center",
                on_click=ReportsState.cancel_delete_report,
            )
        ),
    )


def reset_confirmation_modal() -> rx.Component:
    """Global reset confirmation modal component."""
    return rx.cond(
        ReportsState.show_reset_modal,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.icon(
                                    "triangle_alert",
                                    class_name="h-12 w-12 text-red-600 mx-auto mb-4",
                                ),
                                rx.el.h3(
                                    "Reset All Assessments",
                                    class_name="text-lg font-bold text-gray-900 mb-2",
                                ),
                                rx.el.p(
                                    "This will permanently delete all scores and evidence files for all institutions. This action cannot be undone.",
                                    class_name="text-sm text-gray-600 mb-6",
                                ),
                                rx.el.div(
                                    rx.el.button(
                                        "Cancel",
                                        on_click=ReportsState.cancel_reset_assessment,
                                        class_name="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors",
                                    ),
                                    rx.el.button(
                                        rx.cond(
                                            ReportsState.is_resetting,
                                            rx.el.span(
                                                "Purging Data...",
                                                class_name="animate-pulse",
                                            ),
                                            "Reset All Data",
                                        ),
                                        on_click=ReportsState.reset_all_assessments,
                                        disabled=ReportsState.is_resetting,
                                        class_name="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-bold hover:bg-red-700 disabled:opacity-50 transition-colors",
                                    ),
                                    class_name="flex items-center justify-end gap-3",
                                ),
                                class_name="text-center",
                            ),
                            class_name="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4",
                            on_click=rx.stop_propagation,
                        ),
                        class_name="flex items-start justify-center min-h-screen p-4 pt-24",
                    ),
                    class_name="fixed inset-0 bg-black/60 backdrop-blur-sm z-[110] flex items-start justify-center",
                    on_click=ReportsState.cancel_reset_assessment,
                ),
                class_name="fixed inset-0 z-[110]",
            )
        ),
    )


def review_report_modal() -> rx.Component:
    """Responsive centered modal for reviewing institution assessments."""
    return rx.cond(
        ReportsState.show_review_modal,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                rx.el.span(
                                    "Review Assessment: ",
                                    class_name="text-gray-500 font-medium",
                                ),
                                rx.el.span(
                                    ReportsState.selected_review_report["name"],
                                    class_name="text-blue-700",
                                ),
                                class_name="text-xl font-black mb-6",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.p(
                                        "Overall Readiness Score",
                                        class_name="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1",
                                    ),
                                    rx.el.p(
                                        f"{ReportsState.selected_review_report['overall_score']}%",
                                        class_name="text-4xl font-black text-blue-600",
                                    ),
                                    class_name="mb-8 p-6 bg-blue-50 rounded-2xl border border-blue-100",
                                ),
                                rx.el.div(
                                    dimension_score_row(
                                        "Research & Discovery (50%)",
                                        ReportsState.selected_review_report[
                                            "research_score"
                                        ],
                                    ),
                                    dimension_score_row(
                                        "Employability & Outcomes (20%)",
                                        ReportsState.selected_review_report[
                                            "employability_score"
                                        ],
                                    ),
                                    dimension_score_row(
                                        "Global Engagement (15%)",
                                        ReportsState.selected_review_report[
                                            "global_engagement_score"
                                        ],
                                    ),
                                    dimension_score_row(
                                        "Learning Experience (10%)",
                                        ReportsState.selected_review_report[
                                            "learning_experience_score"
                                        ],
                                    ),
                                    dimension_score_row(
                                        "Sustainability (5%)",
                                        ReportsState.selected_review_report[
                                            "sustainability_score"
                                        ],
                                    ),
                                    class_name="space-y-1 mb-8 bg-white border border-gray-100 p-4 rounded-xl",
                                ),
                                evidence_list_section(
                                    ReportsState.selected_review_report[
                                        "evidence_files"
                                    ]
                                ),
                                rx.el.div(
                                    rx.el.label(
                                        "Reviewer Comments",
                                        class_name="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 mt-6",
                                    ),
                                    rx.el.textarea(
                                        placeholder="Add feedback, observations, or reasons for decline...",
                                        on_change=ReportsState.set_review_comments,
                                        class_name="w-full h-24 p-4 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none",
                                        default_value=ReportsState.review_comments,
                                    ),
                                    class_name="mb-8",
                                ),
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "Cancel",
                                    on_click=ReportsState.close_review_modal,
                                    class_name="px-4 py-2.5 text-sm font-bold text-gray-500 hover:text-gray-900 transition-colors",
                                ),
                                rx.el.div(
                                    rx.el.button(
                                        rx.cond(
                                            ReportsState.is_saving_review,
                                            "Processing...",
                                            "Decline Assessment",
                                        ),
                                        on_click=ReportsState.process_review(
                                            "Declined"
                                        ),
                                        disabled=ReportsState.is_saving_review,
                                        class_name="px-6 py-2.5 bg-rose-50 text-rose-600 border border-rose-200 rounded-xl text-sm font-bold hover:bg-rose-100 transition-all",
                                    ),
                                    rx.el.button(
                                        rx.cond(
                                            ReportsState.is_saving_review,
                                            "Processing...",
                                            "Approve Assessment",
                                        ),
                                        on_click=ReportsState.process_review(
                                            "Reviewed"
                                        ),
                                        disabled=ReportsState.is_saving_review,
                                        class_name="px-6 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-bold hover:bg-emerald-700 shadow-lg shadow-emerald-100 transition-all",
                                    ),
                                    class_name="flex gap-3",
                                ),
                                class_name="flex items-center justify-between pt-6 border-t border-gray-100",
                            ),
                        ),
                        class_name="bg-white rounded-[2rem] shadow-2xl p-8 max-w-2xl w-full mx-4",
                    ),
                    class_name="flex items-center justify-center min-h-screen p-4",
                ),
                class_name="fixed inset-0 bg-black/60 backdrop-blur-md z-[120] overflow-y-auto",
            )
        ),
    )


def status_distribution_chart() -> rx.Component:
    """Renders a doughnut chart for institutional status distribution."""
    return ds_card(
        rx.el.div(
            rx.el.div(
                rx.icon("pie-chart", class_name="h-5 w-5 text-blue-600 mr-2"),
                rx.el.h3("Status Distribution", class_name=DS.H3),
                class_name="flex items-center mb-6",
            ),
            rx.el.div(
                rx.el.div(
                    rx.recharts.pie_chart(
                        rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
                        rx.recharts.pie(
                            data=ReportsState.status_distribution_data,
                            data_key="value",
                            name_key="name",
                            cx="50%",
                            cy="50%",
                            inner_radius="60%",
                            outer_radius="90%",
                            stroke="none",
                            stroke_width=0,
                            padding_angle=2,
                        ),
                        width="100%",
                        height=220,
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Total",
                            class_name="text-[10px] font-bold text-gray-400 uppercase tracking-widest",
                        ),
                        rx.el.p(
                            ReportsState.total_reports.to_string(),
                            class_name="text-2xl font-black text-gray-900",
                        ),
                        class_name="absolute inset-0 flex flex-col items-center justify-center pointer-events-none",
                    ),
                    class_name="relative",
                ),
                rx.el.div(
                    rx.foreach(
                        ReportsState.status_distribution_percentages,
                        lambda item: rx.el.div(
                            rx.el.div(
                                rx.el.span(
                                    class_name="w-2.5 h-2.5 rounded-full mr-2",
                                    style={"backgroundColor": item["fill"]},
                                ),
                                rx.el.span(
                                    item["name"],
                                    class_name="text-xs font-semibold text-gray-600",
                                ),
                                class_name="flex items-center",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    item["value"].to_string(),
                                    class_name="text-xs font-bold text-gray-900",
                                ),
                                rx.el.span(
                                    f" ({item['percentage']})",
                                    class_name="text-[10px] text-gray-400 font-medium",
                                ),
                                class_name="flex items-center",
                            ),
                            class_name="flex items-center justify-between py-1.5 border-b border-gray-50 last:border-0",
                        ),
                    ),
                    class_name="mt-4",
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-8 items-center",
            ),
        )
    )


def reports_dashboard_ui() -> rx.Component:
    """Main UI for the Reports page."""
    from app.components.design_system import ds_pagination, ds_stat_card, DS

    return rx.el.div(
        review_report_modal(),
        delete_report_modal(),
        reset_confirmation_modal(),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h1("Reports & Exports", class_name=DS.H1),
                    rx.el.p(
                        "Generate and download performance reports based on Overall Readiness Score and all 5 performance categories per school.",
                        class_name="text-slate-600 mt-1 font-medium",
                    ),
                    class_name="flex-1",
                )
            ),
            class_name="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4",
        ),
        rx.el.div(
            ds_stat_card(
                title="Total Institutions",
                value=ReportsState.total_reports,
                icon="building-2",
                color_variant="primary",
            ),
            ds_stat_card(
                title="For Review",
                value=ReportsState.for_review_count,
                icon="square_check",
                color_variant="success",
            ),
            ds_stat_card(
                title="Reviewed",
                value=ReportsState.reviewed_count,
                icon="languages",
                color_variant="primary",
            ),
            ds_stat_card(
                title="In Progress",
                value=ReportsState.in_progress_count,
                icon="clock",
                color_variant="warning",
            ),
            ds_stat_card(
                title="Pending",
                value=ReportsState.pending_count,
                icon="hourglass",
                color_variant="neutral",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8",
        ),
        rx.el.div(status_distribution_chart(), class_name="mb-8"),
        rx.el.div(
            rx.el.div(
                rx.el.input(
                    placeholder="Search reports by institution name...",
                    on_change=ReportsState.set_search_query,
                    class_name="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500",
                    default_value=ReportsState.search_query,
                ),
                class_name="mb-4",
            ),
            rx.cond(
                ReportsState.filtered_reports.length() > 0,
                rx.el.div(
                    rx.el.div(
                        rx.el.table(
                            rx.el.thead(
                                rx.el.tr(
                                    rx.el.th(
                                        "Institution",
                                        class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Overall Score",
                                        class_name="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Dimension Scores",
                                        class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Status",
                                        class_name="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Last Generated",
                                        class_name="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Actions",
                                        class_name="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    class_name="bg-gray-50 border-b border-gray-200",
                                ),
                                class_name="bg-gray-50",
                            ),
                            rx.el.tbody(
                                rx.cond(
                                    ReportsState.is_loading_page,
                                    rx.foreach(
                                        rx.Var.range(ReportsState.page_size),
                                        lambda _: rx.el.tr(
                                            rx.el.td(
                                                rx.el.div(
                                                    class_name="animate-pulse bg-gray-100 h-10 rounded-lg"
                                                ),
                                                class_name="px-6 py-4",
                                                col_span=6,
                                            )
                                        ),
                                    ),
                                    rx.foreach(
                                        ReportsState.paginated_reports,
                                        lambda report: report_table_row(
                                            report=report, key=report["id"]
                                        ),
                                    ),
                                ),
                                class_name="divide-y divide-gray-200",
                            ),
                            class_name="min-w-full divide-y divide-gray-200",
                        ),
                        class_name="overflow-x-auto",
                    ),
                    ds_pagination(
                        current_page=ReportsState.current_page,
                        total_pages=ReportsState.total_pages,
                        on_prev=ReportsState.prev_page,
                        on_next=ReportsState.next_page,
                        on_page_change=rx.noop(),
                        page_size=ReportsState.page_size,
                        on_page_size_change=ReportsState.set_page_size,
                    ),
                    class_name="shadow-md rounded-lg",
                ),
                rx.el.div(
                    rx.el.p(
                        "No reports found. Try adjusting your search criteria.",
                        class_name="text-center py-8 text-gray-500",
                    ),
                    class_name="bg-white rounded-lg shadow-md p-8",
                ),
            ),
            class_name="bg-white rounded-lg shadow-md p-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.button(
                    rx.icon("trash-2", class_name="h-5 w-5 mr-2"),
                    "Reset Assessments",
                    on_click=ReportsState.confirm_reset_assessment,
                    class_name="flex items-center px-6 py-3 bg-red-600 text-white rounded-xl shadow-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-all text-sm font-bold",
                ),
                rx.el.button(
                    rx.icon("file-down", class_name="h-5 w-5 mr-2"),
                    "Download All Reports",
                    on_click=ReportsState.download_all_reports,
                    class_name="flex items-center px-6 py-3 bg-blue-600 text-white rounded-xl shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors text-sm font-medium",
                ),
                class_name="flex items-center justify-center gap-4",
            ),
            class_name="mt-8 py-6 border-t border-gray-100",
        ),
        ai_analysis_section(),
        class_name="p-6 max-w-7xl mx-auto",
    )