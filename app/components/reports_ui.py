import reflex as rx
from app.states.reports_state import ReportsState, ReportItem


def report_stat_card(
    title: str, value: int, icon: str, color_class: str
) -> rx.Component:
    """Display a statistic summary card for reports."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(title, class_name="text-sm font-medium text-gray-500"),
                rx.el.h3(value, class_name="text-2xl font-bold text-gray-900 mt-1"),
            ),
            rx.el.div(
                rx.icon(icon, class_name=f"h-6 w-6 {color_class}"),
                class_name="p-3 bg-gray-50 rounded-lg",
            ),
            class_name="flex justify-between items-start",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def score_badge(score: int) -> rx.Component:
    """Visual badge for scores with color coding."""
    return rx.cond(
        score >= 80,
        rx.el.span(
            f"{score}%",
            class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-green-100 text-green-800",
        ),
        rx.cond(
            score >= 60,
            rx.el.span(
                f"{score}%",
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-yellow-100 text-yellow-800",
            ),
            rx.cond(
                score > 0,
                rx.el.span(
                    f"{score}%",
                    class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-red-100 text-red-800",
                ),
                rx.el.span(
                    "N/A",
                    class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-500",
                ),
            ),
        ),
    )


def report_status_badge(status: str) -> rx.Component:
    """Status badge component."""
    return rx.match(
        status,
        (
            "Completed",
            rx.el.span(
                "Completed",
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800",
            ),
        ),
        (
            "In Progress",
            rx.el.span(
                "In Progress",
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800",
            ),
        ),
        rx.el.span(
            "Pending",
            class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600",
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
    """Helper component to render a single dimension row with aligned label and badge."""
    return rx.el.div(
        rx.el.span(label, class_name="text-xs font-medium text-gray-600 min-w-[200px]"),
        rx.el.div(
            score_badge(score), class_name="flex-1 flex justify-end min-w-[60px]"
        ),
        class_name="flex items-center justify-between gap-4 py-1",
    )


def report_table_row(report: ReportItem) -> rx.Component:
    """Row component for the Reports table."""
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.p(report["name"], class_name="text-sm font-medium text-gray-900"),
                rx.el.p(f"ID: {report['id']}", class_name="text-xs text-gray-500"),
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
                    class_name="flex items-center justify-center min-h-screen p-4",
                ),
                class_name="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center",
                on_click=ReportsState.cancel_delete_report,
            )
        ),
    )


def reports_dashboard_ui() -> rx.Component:
    """Main UI for the Reports page."""
    return rx.el.div(
        delete_report_modal(),
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Reports & Exports", class_name="text-2xl font-bold text-gray-900"
                ),
                rx.el.p(
                    "Generate and download performance reports based on Overall Readiness Score and all 5 performance categories per school.",
                    class_name="text-gray-600 mt-1",
                ),
                class_name="flex-1",
            ),
            rx.el.button(
                rx.icon("file-down", class_name="h-5 w-5 mr-2"),
                "Download All Reports",
                on_click=ReportsState.download_all_reports,
                class_name="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors text-sm font-medium",
            ),
            class_name="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4",
        ),
        rx.el.div(
            report_stat_card(
                "Total Institutions",
                ReportsState.total_reports,
                "building-2",
                "text-blue-600",
            ),
            report_stat_card(
                "Reports Completed",
                ReportsState.completed_count,
                "square_check",
                "text-green-600",
            ),
            report_stat_card(
                "Pending / In Progress",
                ReportsState.pending_count,
                "clock",
                "text-orange-600",
            ),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8",
        ),
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
                            rx.foreach(ReportsState.filtered_reports, report_table_row),
                            class_name="divide-y divide-gray-200",
                        ),
                        class_name="min-w-full divide-y divide-gray-200",
                    ),
                    class_name="overflow-x-auto shadow-md rounded-lg",
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
        class_name="p-6 max-w-7xl mx-auto",
    )