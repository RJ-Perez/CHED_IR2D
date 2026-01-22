import reflex as rx
from app.states.institutions_state import InstitutionsState
from app.states.hei_state import HEI


def register_institution_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 bg-black/60 backdrop-blur-sm z-[110]"
            ),
            rx.radix.primitives.dialog.content(
                rx.radix.primitives.dialog.title(
                    "Register New HEI",
                    class_name="text-xl font-bold text-gray-900 mb-2",
                ),
                rx.radix.primitives.dialog.description(
                    "Enter the institutional details to register a new Higher Education Institution in the system.",
                    class_name="text-sm text-gray-500 mb-6",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Institution Name",
                            class_name="block text-xs font-bold text-gray-500 uppercase mb-1",
                        ),
                        rx.el.input(
                            placeholder="e.g. University of Santo Tomas",
                            on_change=InstitutionsState.set_new_name,
                            class_name="w-full px-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none",
                            default_value=InstitutionsState.new_name,
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Street Address",
                            class_name="block text-xs font-bold text-gray-500 uppercase mb-1",
                        ),
                        rx.el.input(
                            placeholder="e.g. España Blvd, Sampaloc",
                            on_change=InstitutionsState.set_new_street,
                            class_name="w-full px-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none",
                            default_value=InstitutionsState.new_street,
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Region",
                                class_name="block text-xs font-bold text-gray-500 uppercase mb-1",
                            ),
                            rx.el.div(
                                rx.el.select(
                                    rx.el.option(
                                        "Select Region", value="", disabled=True
                                    ),
                                    rx.foreach(
                                        InstitutionsState.regions,
                                        lambda r: rx.el.option(r, value=r),
                                    ),
                                    on_change=InstitutionsState.set_new_region,
                                    value=InstitutionsState.new_region,
                                    class_name="w-full px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm appearance-none cursor-pointer outline-none",
                                ),
                                rx.icon(
                                    "chevron-down",
                                    class_name="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none",
                                ),
                                class_name="relative",
                            ),
                            class_name="flex-1",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "City / Municipality",
                                class_name="block text-xs font-bold text-gray-500 uppercase mb-1",
                            ),
                            rx.el.div(
                                rx.el.select(
                                    rx.el.option(
                                        "Select City", value="", disabled=True
                                    ),
                                    rx.foreach(
                                        InstitutionsState.available_register_cities,
                                        lambda c: rx.el.option(c, value=c),
                                    ),
                                    on_change=InstitutionsState.set_new_city,
                                    value=InstitutionsState.new_city,
                                    class_name="w-full px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm appearance-none cursor-pointer outline-none",
                                ),
                                rx.icon(
                                    "chevron-down",
                                    class_name="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none",
                                ),
                                class_name="relative",
                            ),
                            class_name="flex-1",
                        ),
                        class_name="grid grid-cols-2 gap-4 mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "ZIP Code",
                                class_name="block text-xs font-bold text-gray-500 uppercase mb-1",
                            ),
                            rx.el.input(
                                placeholder="e.g. 1015",
                                on_change=InstitutionsState.set_new_zip,
                                class_name="w-full px-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none",
                                default_value=InstitutionsState.new_zip,
                            ),
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Contact Number",
                                class_name="block text-xs font-bold text-gray-500 uppercase mb-1",
                            ),
                            rx.el.input(
                                placeholder="e.g. 02-8731-3101",
                                on_change=InstitutionsState.set_new_contact,
                                class_name="w-full px-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none",
                                default_value=InstitutionsState.new_contact,
                            ),
                        ),
                        class_name="grid grid-cols-2 gap-4 mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Authorized Administrator",
                            class_name="block text-xs font-bold text-gray-500 uppercase mb-1",
                        ),
                        rx.el.input(
                            placeholder="e.g. Dr. Richard G. Gonzales",
                            on_change=InstitutionsState.set_new_admin,
                            class_name="w-full px-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none",
                            default_value=InstitutionsState.new_admin,
                        ),
                        class_name="mb-6",
                    ),
                    class_name="flex flex-col",
                ),
                rx.el.div(
                    rx.radix.primitives.dialog.close(
                        rx.el.button(
                            "Cancel",
                            class_name="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition-colors",
                        )
                    ),
                    rx.el.button(
                        rx.cond(
                            InstitutionsState.is_registering,
                            rx.el.div(
                                rx.el.div(
                                    class_name="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"
                                ),
                                "Registering...",
                                class_name="flex items-center",
                            ),
                            "Register Institution",
                        ),
                        on_click=InstitutionsState.register_new_institution,
                        disabled=~InstitutionsState.is_register_form_valid
                        | InstitutionsState.is_registering,
                        class_name=rx.cond(
                            InstitutionsState.is_register_form_valid,
                            "px-6 py-2 bg-blue-600 text-white rounded-lg text-sm font-bold hover:bg-blue-700 shadow-md transition-all",
                            "px-6 py-2 bg-gray-200 text-gray-400 rounded-lg text-sm font-bold cursor-not-allowed",
                        ),
                    ),
                    class_name="flex justify-end items-center gap-3 pt-4 border-t border-gray-100",
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-2xl shadow-2xl p-8 w-full max-w-lg z-[120]",
            ),
        ),
        open=InstitutionsState.show_register_modal,
        on_open_change=InstitutionsState.set_show_register_modal,
    )


def stat_card(title: str, value: int, icon: str, color_class: str) -> rx.Component:
    """Display a statistic in a card with consistent design tokens."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    title,
                    class_name="text-xs font-bold text-gray-500 uppercase tracking-widest",
                ),
                rx.el.h3(
                    value,
                    class_name="text-2xl font-black text-slate-900 mt-2 tracking-tight",
                ),
            ),
            rx.el.div(
                rx.icon(
                    icon,
                    class_name=f"h-6 w-6 stroke-{color_class.split('-')[-2]}-{color_class.split('-')[-1]}",
                ),
                class_name="p-3 bg-gray-50 rounded-xl",
            ),
            class_name="flex justify-between items-start",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
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


@rx.memo
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
                    class_name="flex items-start justify-center min-h-screen p-4 pt-24",
                ),
                class_name="fixed inset-0 bg-black bg-opacity-50 z-[100] flex items-start justify-center",
                on_click=InstitutionsState.cancel_delete,
            )
        ),
    )


def view_institution_modal() -> rx.Component:
    return rx.cond(
        InstitutionsState.show_view_modal,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                "Institution Details",
                                class_name="text-xl font-bold text-gray-900 mb-6",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.p(
                                        "Name",
                                        class_name="text-xs font-bold text-gray-400 uppercase tracking-widest",
                                    ),
                                    rx.el.p(
                                        InstitutionsState.selected_hei_data["name"],
                                        class_name="text-sm font-semibold text-gray-700",
                                    ),
                                    class_name="mb-4",
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        "Address",
                                        class_name="text-xs font-bold text-gray-400 uppercase tracking-widest",
                                    ),
                                    rx.el.p(
                                        InstitutionsState.selected_hei_data["address"],
                                        class_name="text-sm font-semibold text-gray-700",
                                    ),
                                    class_name="mb-4",
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        "Administrator",
                                        class_name="text-xs font-bold text-gray-400 uppercase tracking-widest",
                                    ),
                                    rx.el.p(
                                        InstitutionsState.selected_hei_data[
                                            "admin_name"
                                        ],
                                        class_name="text-sm font-semibold text-gray-700",
                                    ),
                                    class_name="mb-4",
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        "Street",
                                        class_name="text-xs font-bold text-gray-400 uppercase tracking-widest",
                                    ),
                                    rx.el.p(
                                        InstitutionsState.selected_hei_data["street"],
                                        class_name="text-sm font-semibold text-gray-700",
                                    ),
                                    class_name="mb-4",
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        "City",
                                        class_name="text-xs font-bold text-gray-400 uppercase tracking-widest",
                                    ),
                                    rx.el.p(
                                        InstitutionsState.selected_hei_data["city"],
                                        class_name="text-sm font-semibold text-gray-700",
                                    ),
                                    class_name="mb-4",
                                ),
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "Close",
                                    on_click=InstitutionsState.close_modals,
                                    class_name="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors",
                                ),
                                class_name="mt-8",
                            ),
                            class_name="bg-white rounded-2xl shadow-2xl p-8 max-w-lg w-full",
                        ),
                        class_name="flex items-center justify-center min-h-screen p-4",
                    ),
                    class_name="fixed inset-0 bg-black/60 backdrop-blur-sm z-[110] overflow-y-auto",
                )
            )
        ),
    )


def edit_institution_modal() -> rx.Component:
    return rx.cond(
        InstitutionsState.show_edit_modal,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                "Edit Institution",
                                class_name="text-xl font-bold text-gray-900 mb-6",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.label(
                                        "Institution Name",
                                        class_name="block text-xs font-bold text-gray-500 uppercase mb-2",
                                    ),
                                    rx.el.input(
                                        default_value=InstitutionsState.edit_name,
                                        on_change=InstitutionsState.set_edit_name,
                                        class_name="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm",
                                    ),
                                    class_name="mb-4",
                                ),
                                rx.el.div(
                                    rx.el.label(
                                        "Street Address",
                                        class_name="block text-xs font-bold text-gray-500 uppercase mb-2",
                                    ),
                                    rx.el.input(
                                        default_value=InstitutionsState.edit_street,
                                        on_change=InstitutionsState.set_edit_street,
                                        class_name="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm",
                                    ),
                                    class_name="mb-4",
                                ),
                                rx.el.div(
                                    rx.el.label(
                                        "City",
                                        class_name="block text-xs font-bold text-gray-500 uppercase mb-2",
                                    ),
                                    rx.el.input(
                                        default_value=InstitutionsState.edit_city,
                                        on_change=InstitutionsState.set_edit_city,
                                        class_name="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm",
                                    ),
                                    class_name="mb-4",
                                ),
                                rx.el.div(
                                    rx.el.label(
                                        "Administrator Name",
                                        class_name="block text-xs font-bold text-gray-500 uppercase mb-2",
                                    ),
                                    rx.el.input(
                                        default_value=InstitutionsState.edit_admin,
                                        on_change=InstitutionsState.set_edit_admin,
                                        class_name="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm",
                                    ),
                                    class_name="mb-4",
                                ),
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "Cancel",
                                    on_click=InstitutionsState.close_modals,
                                    class_name="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors",
                                ),
                                rx.el.button(
                                    rx.cond(
                                        InstitutionsState.is_saving_edit,
                                        "Saving...",
                                        "Save Changes",
                                    ),
                                    on_click=InstitutionsState.save_institution_edit,
                                    disabled=InstitutionsState.is_saving_edit,
                                    class_name="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors",
                                ),
                                class_name="flex justify-end gap-3 mt-8",
                            ),
                            class_name="bg-white rounded-2xl shadow-2xl p-8 max-w-lg w-full",
                        ),
                        class_name="flex items-center justify-center min-h-screen p-4",
                    ),
                    class_name="fixed inset-0 bg-black/60 backdrop-blur-sm z-[110] overflow-y-auto",
                )
            )
        ),
    )


def institutions_dashboard_ui() -> rx.Component:
    """Main content for the Institutions Management page."""
    from app.components.design_system import ds_pagination

    return rx.el.div(
        delete_confirmation_modal(),
        view_institution_modal(),
        edit_institution_modal(),
        register_institution_modal(),
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
                    on_click=InstitutionsState.open_register_modal,
                    class_name="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium transition-colors",
                ),
                class_name="p-5 border-b border-gray-200 flex flex-col md:flex-row justify-between items-center gap-4",
            ),
            rx.el.div(
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
                                    "Actions",
                                    class_name="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                            ),
                            class_name="bg-gray-50",
                        ),
                        rx.el.tbody(
                            rx.cond(
                                InstitutionsState.is_loading_page,
                                rx.foreach(
                                    rx.Var.range(InstitutionsState.page_size),
                                    lambda _: rx.el.tr(
                                        rx.el.td(
                                            rx.el.div(
                                                class_name="animate-pulse bg-gray-100 h-10 rounded-lg"
                                            ),
                                            class_name="px-6 py-4",
                                            col_span=3,
                                        )
                                    ),
                                ),
                                rx.foreach(
                                    InstitutionsState.paginated_heis,
                                    lambda hei: hei_table_row(hei=hei, key=hei["id"]),
                                ),
                            ),
                            class_name="bg-white divide-y divide-gray-200",
                        ),
                        class_name="min-w-full divide-y divide-gray-200",
                    ),
                    class_name="overflow-x-auto",
                ),
                ds_pagination(
                    current_page=InstitutionsState.current_page,
                    total_pages=InstitutionsState.total_pages,
                    on_prev=InstitutionsState.prev_page,
                    on_next=InstitutionsState.next_page,
                    on_page_change=rx.noop(),
                    page_size=InstitutionsState.page_size,
                    on_page_size_change=InstitutionsState.set_page_size,
                ),
            ),
            class_name="bg-white rounded-xl border border-gray-200 shadow-sm",
        ),
        class_name="max-w-7xl mx-auto",
    )