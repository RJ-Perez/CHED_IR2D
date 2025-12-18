import reflex as rx
from app.states.hei_state import HEIState, HEI


def search_result_item(hei: HEI) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("building-2", class_name="h-5 w-5 text-gray-400 mr-3"),
            rx.el.div(
                rx.el.p(hei["name"], class_name="text-sm font-medium text-gray-900"),
                rx.el.p(hei["address"], class_name="text-xs text-gray-500"),
            ),
            class_name="flex items-center",
        ),
        on_click=lambda: HEIState.select_hei(hei),
        class_name="p-3 cursor-pointer hover:bg-blue-50 transition-colors border-b last:border-b-0",
    )


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
                    "Address", class_name="block text-sm font-medium text-gray-700 mb-1"
                ),
                rx.el.input(
                    placeholder="Complete institutional address",
                    on_change=HEIState.set_reg_address,
                    class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors",
                    default_value=HEIState.reg_address,
                ),
                class_name="col-span-2",
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
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm animate-in fade-in slide-in-from-bottom-4",
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
                            rx.icon(
                                "search",
                                class_name="absolute left-4 top-3.5 text-gray-400 h-5 w-5",
                            ),
                            rx.el.input(
                                placeholder="Search for an HEI in NCR...",
                                on_change=HEIState.set_search_query,
                                class_name="w-full pl-12 pr-4 py-3 bg-white border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-shadow shadow-sm text-lg",
                                default_value=HEIState.search_query,
                            ),
                            class_name="relative mb-2",
                        ),
                        rx.cond(
                            HEIState.search_query & ~HEIState.selected_hei,
                            rx.el.div(
                                rx.cond(
                                    HEIState.filtered_heis.length() > 0,
                                    rx.foreach(
                                        HEIState.filtered_heis, search_result_item
                                    ),
                                    rx.el.div(
                                        "No institutions found.",
                                        class_name="p-4 text-sm text-gray-500 text-center italic",
                                    ),
                                ),
                                class_name="absolute z-10 w-full bg-white mt-1 rounded-xl border border-gray-200 shadow-lg overflow-hidden max-h-60 overflow-y-auto",
                            ),
                        ),
                        class_name="relative",
                    ),
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
                            "Continue to Dashboard",
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
        class_name="max-w-2xl mx-auto w-full",
    )
