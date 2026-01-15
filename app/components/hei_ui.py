import reflex as rx
from app.states.hei_state import HEIState, HEI


def ranking_framework_option(
    value: str, label: str, description: str, image_path: str
) -> rx.Component:
    is_selected = HEIState.ranking_framework == value
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.cond(
                        is_selected,
                        rx.el.div(class_name="w-3 h-3 rounded-full bg-blue-600"),
                        rx.el.div(class_name="w-3 h-3 rounded-full bg-transparent"),
                    ),
                    class_name=rx.cond(
                        is_selected,
                        "flex items-center justify-center w-5 h-5 rounded-full border-2 border-blue-600 mr-3",
                        "flex items-center justify-center w-5 h-5 rounded-full border-2 border-gray-300 mr-3",
                    ),
                ),
                rx.el.span(label, class_name="font-semibold text-gray-900"),
                class_name="flex items-center mb-2",
            ),
            rx.el.p(
                description, class_name="text-xs text-gray-500 ml-8 leading-relaxed"
            ),
        ),
        on_click=lambda: HEIState.set_ranking_framework(value),
        class_name=rx.cond(
            is_selected,
            "p-4 rounded-xl border-2 border-blue-600 bg-blue-50/50 cursor-pointer transition-all",
            "p-4 rounded-xl border border-gray-200 hover:border-blue-300 hover:bg-gray-50 cursor-pointer transition-all",
        ),
    )


def registration_form() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Institutional Profile",
            class_name="text-lg font-semibold text-gray-900 mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Institution Name",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.input(
                    placeholder="e.g. Technological University of the Philippines",
                    on_change=HEIState.set_reg_name,
                    class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors",
                    default_value=HEIState.reg_name,
                ),
                class_name="col-span-2",
            ),
            rx.el.div(
                rx.el.label(
                    "Street Address / Unit / Building",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.input(
                    placeholder="e.g. 123 Rizal St, Brgy. Central",
                    on_change=HEIState.set_reg_street,
                    class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors",
                    default_value=HEIState.reg_street,
                ),
                class_name="col-span-2",
            ),
            rx.el.div(
                rx.el.label(
                    "Region", class_name="block text-sm font-medium text-gray-700 mb-1"
                ),
                rx.el.div(
                    rx.el.select(
                        rx.el.option("Select Region", value="", disabled=True),
                        rx.foreach(
                            HEIState.regions,
                            lambda region: rx.el.option(region, value=region),
                        ),
                        on_change=HEIState.set_reg_region,
                        value=HEIState.reg_region,
                        class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none appearance-none bg-white cursor-pointer",
                    ),
                    rx.icon(
                        "chevron-down",
                        class_name="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none",
                    ),
                    class_name="relative",
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "City / Municipality",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.div(
                    rx.el.select(
                        rx.el.option("Select City", value="", disabled=True),
                        rx.foreach(
                            HEIState.available_cities,
                            lambda city: rx.el.option(city, value=city),
                        ),
                        on_change=HEIState.set_reg_city,
                        value=HEIState.reg_city,
                        class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none appearance-none bg-white cursor-pointer",
                    ),
                    rx.icon(
                        "chevron-down",
                        class_name="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none",
                    ),
                    class_name="relative",
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "ZIP Code",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.input(
                    placeholder="e.g. 1101",
                    on_change=HEIState.set_reg_zip,
                    max_length=4,
                    class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors",
                    default_value=HEIState.reg_zip,
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "Contact Number",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.input(
                    placeholder="+63 2 8123 4567",
                    on_change=HEIState.set_reg_contact,
                    class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors",
                    default_value=HEIState.reg_contact,
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "Administrator Name",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.input(
                    placeholder="Name of authorized representative",
                    on_change=HEIState.set_reg_admin,
                    class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors",
                    default_value=HEIState.reg_admin,
                ),
                class_name="col-span-2 md:col-span-1",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm animate-in fade-in slide-in-from-bottom-4",
    )


def hei_table_row(hei: HEI) -> rx.Component:
    is_selected = HEIState.selected_hei_id == hei["id"]
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.p(hei["name"], class_name="text-sm font-semibold text-gray-900"),
                rx.el.p(f"ID: {hei['id']}", class_name="text-xs text-gray-500"),
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
                    hei["address"],
                    class_name="text-sm text-gray-600 truncate max-w-[150px]",
                ),
                class_name="flex items-center",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(
                hei["type"],
                class_name="text-xs font-semibold text-gray-600 bg-gray-100 px-2.5 py-0.5 rounded-full",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.button(
                    rx.cond(is_selected, "Selected", "Select"),
                    on_click=lambda: HEIState.select_hei(hei),
                    class_name=rx.cond(
                        is_selected,
                        "px-4 py-2 bg-green-600 text-white rounded-lg text-xs font-bold shadow-sm w-24",
                        "px-4 py-2 border border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white rounded-lg text-xs font-bold transition-all w-24",
                    ),
                ),
                class_name="flex justify-end",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right",
        ),
        class_name=rx.cond(
            is_selected,
            "bg-blue-50 border-l-4 border-blue-600",
            "hover:bg-gray-50 transition-colors border-l-4 border-transparent",
        ),
    )


def hei_selection_table() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "Institution",
                            class_name="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Location",
                            class_name="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Type",
                            class_name="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Action",
                            class_name="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider",
                        ),
                        class_name="bg-gray-50 border-b border-gray-200",
                    )
                ),
                rx.el.tbody(
                    rx.foreach(HEIState.search_results, hei_table_row),
                    class_name="divide-y divide-gray-200 bg-white",
                ),
                class_name="min-w-full",
            ),
            class_name="overflow-x-auto overflow-y-auto max-h-[480px] border border-gray-200 rounded-xl",
        ),
        rx.cond(
            HEIState.search_results.length() == 0,
            rx.el.div(
                rx.icon("search-slash", class_name="h-8 w-8 text-gray-300 mb-2"),
                rx.el.p(
                    "No institutions found matching your criteria.",
                    class_name="text-sm text-gray-500",
                ),
                class_name="flex flex-col items-center justify-center py-10 bg-gray-50 border border-dashed border-gray-300 rounded-xl mt-2",
            ),
        ),
        class_name="mt-4",
    )


def selection_screen_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Select Institution", class_name="text-3xl font-bold text-gray-900 mb-2"
            ),
            rx.el.p(
                "Identify the Higher Education Institution (HEI) you are representing.",
                class_name="text-gray-600 mb-8",
            ),
            rx.cond(
                ~HEIState.is_registration_mode,
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.cond(
                                HEIState.is_searching,
                                rx.el.div(
                                    class_name="absolute left-4 top-3.5 h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"
                                ),
                                rx.icon(
                                    "search",
                                    class_name="absolute left-4 top-3.5 text-gray-400 h-5 w-5",
                                ),
                            ),
                            rx.el.input(
                                placeholder="Search by name, city, or ID...",
                                on_change=HEIState.set_search_query.debounce(500),
                                class_name="w-full pl-12 pr-12 py-3 bg-white border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-shadow shadow-sm text-lg",
                                default_value=HEIState.search_query,
                            ),
                            rx.cond(
                                HEIState.search_query.length() > 0,
                                rx.el.button(
                                    rx.icon("x", class_name="h-4 w-4"),
                                    on_click=HEIState.set_search_query(""),
                                    class_name="absolute right-4 top-4 text-gray-400 hover:text-gray-600",
                                ),
                            ),
                            class_name="relative mb-6",
                        )
                    ),
                    hei_selection_table(),
                    rx.el.div(
                        rx.el.span(
                            "Cannot find your institution? ",
                            class_name="text-sm text-gray-600",
                        ),
                        rx.el.button(
                            "Register HEI Account",
                            on_click=HEIState.toggle_registration_mode,
                            class_name="text-sm font-semibold text-blue-600 hover:text-blue-700 hover:underline",
                        ),
                        class_name="mt-4 flex items-center justify-center",
                    ),
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("arrow-left", class_name="h-4 w-4 mr-2"),
                        "Back to Search",
                        on_click=HEIState.toggle_registration_mode,
                        class_name="flex items-center text-sm text-gray-500 hover:text-gray-800 mb-4 transition-colors",
                    ),
                    rx.el.h2(
                        "Register New Institution",
                        class_name="text-xl font-semibold text-gray-900 mb-4",
                    ),
                    registration_form(),
                ),
            ),
            class_name="mb-10",
        ),
        rx.cond(
            HEIState.selected_hei | HEIState.is_registration_mode,
            rx.el.div(
                rx.el.div(class_name="border-t border-gray-200 my-8"),
                rx.el.h2(
                    "Select Ranking Framework",
                    class_name="text-xl font-semibold text-gray-900 mb-4",
                ),
                rx.el.div(
                    ranking_framework_option(
                        "QS",
                        "QS World University Rankings",
                        "Focuses on academic reputation, employer reputation, faculty/student ratio, citations per faculty, international faculty ratio, and international student ratio.",
                        "/qs-logo.png",
                    ),
                    ranking_framework_option(
                        "THE",
                        "The World University Rankings",
                        "Evaluates universities across teaching, research environment, research quality, industry, and international outlook.",
                        "/the-logo.png",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 animate-in fade-in slide-in-from-bottom-8",
                ),
                rx.el.button(
                    rx.cond(
                        HEIState.is_loading,
                        rx.el.div(
                            rx.el.div(
                                class_name="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"
                            ),
                            "Processing...",
                            class_name="flex items-center justify-center",
                        ),
                        rx.el.span(
                            "Continue to Assessment",
                            rx.icon(
                                "arrow-right", class_name="ml-2 h-5 w-5 inline-block"
                            ),
                        ),
                    ),
                    on_click=HEIState.submit_selection,
                    disabled=~HEIState.is_form_valid | HEIState.is_loading,
                    class_name=rx.cond(
                        HEIState.is_form_valid,
                        "w-full py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold text-lg shadow-lg shadow-blue-200 transition-all transform hover:scale-[1.02]",
                        "w-full py-4 bg-gray-200 text-gray-400 rounded-xl font-semibold text-lg cursor-not-allowed",
                    ),
                ),
            ),
        ),
        class_name="max-w-4xl mx-auto w-full",
    )