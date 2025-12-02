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


def report_table_row(report: ReportItem) -> rx.Component:
    """Row component for the Reports table."""
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.p(report["name"], class_name="text-sm font-medium text-gray-900"),
                rx.el.p(f"ID: {report['id']}", class_name="text-xs text-gray-500"),
                class_name="flex flex-col",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            score_badge(report["overall_score"]),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.span(
                    f"R: {report['research_score']}",
                    class_name="text-xs text-gray-600 mr-2",
                ),
                rx.el.span(
                    f"E: {report['employability_score']}",
                    class_name="text-xs text-gray-600",
                ),
                class_name="flex items-center",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            report_status_badge(report["status"]),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(report["last_generated"], class_name="text-sm text-gray-500"),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.button(
                rx.icon("download", class_name="h-4 w-4 mr-1"),
                "CSV",
                on_click=ReportsState.download_report(report["id"]),
                class_name="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right",
        ),
        class_name="hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0",
    )


def reports_dashboard_ui() -> rx.Component:
    """Main UI for the Reports page."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Reports & Exports", class_name="text-2xl font-bold text-gray-900"
                ),
                rx.el.p(
                    "Generate and download performance reports for compliance and monitoring.",
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
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4",
                    ),
                    rx.el.input(
                        placeholder="Search reports by institution...",
                        on_change=ReportsState.set_search_query,
                        class_name="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm w-full md:w-80",
                        default_value=ReportsState.search_query,
                    ),
                    class_name="relative",
                ),
                class_name="p-5 border-b border-gray-200 bg-white rounded-t-xl",
            ),
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Institution",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Overall Readiness",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Breakdown",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Status",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Last Generated",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Actions",
                                class_name="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                        ),
                        class_name="bg-gray-50",
                    ),
                    rx.el.tbody(
                        rx.foreach(ReportsState.filtered_reports, report_table_row),
                        class_name="bg-white divide-y divide-gray-200",
                    ),
                    class_name="min-w-full divide-y divide-gray-200",
                ),
                class_name="overflow-x-auto",
            ),
            rx.el.div(
                rx.el.p(
                    f"Showing {ReportsState.filtered_reports.length()} results",
                    class_name="text-sm text-gray-500",
                ),
                class_name="px-6 py-4 border-t border-gray-200 flex items-center justify-between bg-gray-50 rounded-b-xl",
            ),
            class_name="bg-white rounded-xl border border-gray-200 shadow-sm mb-10",
        ),
        class_name="max-w-7xl mx-auto",
    )