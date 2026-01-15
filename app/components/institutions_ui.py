import reflex as rx
from app.states.institutions_state import InstitutionsState
from app.states.hei_state import HEI


def stat_card(title: str, value: int, icon: str, color_class: str) -> rx.Component:
    """Display a statistic in a card."""
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


def status_badge(hei_id: str) -> rx.Component:
    """Mock status badge based on ID parity for variety."""
    is_active = rx.cond(hei_id.to(int) % 2 == 0, True, False)
    return rx.cond(
        is_active,
        rx.el.span(
            "Active",
            class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800",
        ),
        rx.el.span(
            "Pending Review",
            class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800",
        ),
    )


def action_button(
    icon: str, label: str, on_click: rx.event.EventType, is_destructive: bool = False
) -> rx.Component:
    """Reusable action button for table rows."""
    color_class = rx.cond(
        is_destructive,
        "text-red-600 hover:bg-red-50",
        "text-gray-600 hover:bg-gray-100",
    )
    return rx.el.button(
        rx.icon(icon, class_name="h-4 w-4"),
        class_name=f"p-1.5 rounded-md transition-colors {color_class}",
        on_click=on_click,
        title=label,
    )


def hei_table_row(hei: HEI) -> rx.Component:
    """Row component for the HEI table."""
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.p(hei["name"], class_name="text-sm font-medium text-gray-900"),
                class_name="flex flex-col",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.icon(
                    "map-pin", class_name="h-4 w-4 text-gray-400 mr-2 flex-shrink-0"
                ),
                rx.el.span(
                    hei["address"], class_name="text-sm text-gray-600 truncate max-w-xs"
                ),
                class_name="flex items-center",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(status_badge(hei["id"]), class_name="px-6 py-4 whitespace-nowrap"),
        rx.el.td(
            rx.el.div(
                action_button(
                    "eye", "View Details", InstitutionsState.view_details(hei["id"])
                ),
                action_button(
                    "pencil", "Edit", InstitutionsState.edit_institution(hei["id"])
                ),
                action_button(
                    "trash-2",
                    "Delete",
                    InstitutionsState.confirm_delete(hei["id"], hei["name"]),
                    is_destructive=True,
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium",
        ),
        class_name="hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0",
    )


def delete_confirmation_modal() -> rx.Component:
    """Delete confirmation modal component."""
    return rx.cond(
        InstitutionsState.show_delete_modal,
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
                                "Delete Institution",
                                class_name="text-lg font-semibold text-gray-900 mb-2",
                            ),
                            rx.el.p(
                                rx.el.span(
                                    "Are you sure you want to delete ",
                                    class_name="text-sm text-gray-600",
                                ),
                                rx.el.span(
                                    InstitutionsState.delete_confirm_name,
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
                                    on_click=InstitutionsState.cancel_delete,
                                    class_name="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors",
                                ),
                                rx.el.button(
                                    "Delete",
                                    on_click=InstitutionsState.delete_institution,
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
                on_click=InstitutionsState.cancel_delete,
            )
        ),
    )


def institutions_dashboard_ui() -> rx.Component:
    """Main content for the Institutions Management page."""
    return rx.el.div(
        delete_confirmation_modal(),
        rx.el.div(
            rx.el.h1(
                "Institutions Management", class_name="text-2xl font-bold text-gray-900"
            ),
            rx.el.p(
                "Monitor and manage registered Higher Education Institutions.",
                class_name="text-gray-600 mt-1",
            ),
            class_name="mb-8",
        ),
        rx.el.div(
            stat_card(
                "Total Institutions",
                InstitutionsState.stats["total"],
                "building-2",
                "text-blue-600",
            ),
            stat_card(
                "Active Assessments",
                InstitutionsState.stats["active"],
                "activity",
                "text-green-600",
            ),
            stat_card(
                "Pending Reviews",
                InstitutionsState.stats["pending"],
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
                        placeholder="Search institutions by name or address...",
                        on_change=InstitutionsState.set_search_query,
                        class_name="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm w-full md:w-80",
                        default_value=InstitutionsState.search_query,
                    ),
                    class_name="relative",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4 mr-2"),
                    "Add Institution",
                    class_name="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium transition-colors",
                ),
                class_name="p-5 border-b border-gray-200 flex flex-col md:flex-row justify-between items-center gap-4",
            ),
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Institution Name",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Address",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Status",
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
                        rx.foreach(InstitutionsState.filtered_heis, hei_table_row),
                        class_name="bg-white divide-y divide-gray-200",
                    ),
                    class_name="min-w-full divide-y divide-gray-200",
                ),
                class_name="overflow-x-auto",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p("Showing all results", class_name="text-sm text-gray-500"),
                    class_name="flex-1",
                ),
                class_name="px-6 py-4 border-t border-gray-200 flex items-center justify-between bg-gray-50 rounded-b-xl",
            ),
            class_name="bg-white rounded-xl border border-gray-200 shadow-sm",
        ),
        class_name="max-w-7xl mx-auto",
    )