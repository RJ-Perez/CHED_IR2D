import reflex as rx
from app.states.hei_state import HEIState, HEI


@rx.memo
def ranking_framework_option(
    value: str, label: str, description: str, icon: str
) -> rx.Component:
    is_selected = HEIState.ranking_framework == value
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        icon,
                        class_name=rx.cond(
                            is_selected,
                            "h-6 w-6 text-blue-600",
                            "h-6 w-6 text-gray-400",
                        ),
                    ),
                    class_name=rx.cond(
                        is_selected,
                        "p-3 bg-blue-100 rounded-xl mb-4",
                        "p-3 bg-gray-50 rounded-xl mb-4",
                    ),
                ),
                rx.el.h4(label, class_name="text-lg font-bold text-gray-900 mb-2"),
                rx.el.p(
                    description, class_name="text-sm text-gray-500 leading-relaxed"
                ),
                class_name="flex flex-col",
            ),
            class_name="flex-1",
        ),
        rx.cond(
            is_selected,
            rx.el.div(
                rx.icon("circle_check", class_name="h-5 w-5 text-blue-600"),
                class_name="absolute top-4 right-4 animate-in zoom-in duration-300",
            ),
        ),
        on_click=HEIState.set_ranking_framework(value),
        class_name=rx.cond(
            is_selected,
            "relative p-6 rounded-3xl border-2 border-blue-600 bg-blue-50/30 shadow-lg shadow-blue-100/50 cursor-pointer transition-all transform scale-[1.02]",
            "relative p-6 rounded-3xl border border-gray-200 bg-white hover:border-blue-300 hover:bg-gray-50/50 cursor-pointer transition-all hover:shadow-md",
        ),
    )


def registration_form() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("landmark", class_name="h-6 w-6 text-blue-600 mr-3"),
            rx.el.h3(
                "Institutional Profile", class_name="text-xl font-bold text-gray-900"
            ),
            class_name="flex items-center mb-8 border-b border-gray-100 pb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Institution Name",
                    class_name="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2",
                ),
                rx.el.input(
                    placeholder="e.g. Technological University of the Philippines",
                    on_change=HEIState.set_reg_name,
                    class_name="w-full px-5 py-3 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all text-gray-900 font-medium",
                    default_value=HEIState.reg_name,
                ),
                class_name="col-span-2",
            ),
            rx.el.div(
                rx.el.label(
                    "Street Address / Unit / Building",
                    class_name="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2",
                ),
                rx.el.input(
                    placeholder="e.g. 123 Rizal St, Brgy. Central",
                    on_change=HEIState.set_reg_street,
                    class_name="w-full px-5 py-3 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all text-gray-900 font-medium",
                    default_value=HEIState.reg_street,
                ),
                class_name="col-span-2",
            ),
            rx.el.div(
                rx.el.label(
                    "Region",
                    class_name="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2",
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
                        class_name="w-full px-5 py-3 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 outline-none appearance-none cursor-pointer text-gray-900 font-medium",
                    ),
                    rx.icon(
                        "chevron-down",
                        class_name="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none",
                    ),
                    class_name="relative",
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "City / Municipality",
                    class_name="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2",
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
                        class_name="w-full px-5 py-3 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 outline-none appearance-none cursor-pointer text-gray-900 font-medium",
                    ),
                    rx.icon(
                        "chevron-down",
                        class_name="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none",
                    ),
                    class_name="relative",
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "ZIP Code",
                    class_name="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2",
                ),
                rx.el.input(
                    placeholder="e.g. 1101",
                    on_change=HEIState.set_reg_zip,
                    max_length=4,
                    class_name="w-full px-5 py-3 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all text-gray-900 font-medium",
                    default_value=HEIState.reg_zip,
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "Contact Number",
                    class_name="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2",
                ),
                rx.el.input(
                    placeholder="+63 2 8123 4567",
                    on_change=HEIState.set_reg_contact,
                    class_name="w-full px-5 py-3 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all text-gray-900 font-medium",
                    default_value=HEIState.reg_contact,
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "Administrator Name",
                    class_name="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2",
                ),
                rx.el.input(
                    placeholder="Name of authorized representative",
                    on_change=HEIState.set_reg_admin,
                    class_name="w-full px-5 py-3 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all text-gray-900 font-medium",
                    default_value=HEIState.reg_admin,
                ),
                class_name="col-span-2 md:col-span-1",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8",
        ),
        class_name="bg-white p-8 rounded-3xl border border-gray-100 shadow-xl shadow-slate-200/50 animate-in fade-in slide-in-from-bottom-6 duration-500",
    )


def preliminary_notice_modal() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "triangle-alert", class_name="h-12 w-12 text-amber-500 mb-4"
                        ),
                        rx.el.h2(
                            "⚠️ Preliminary Assessment Notice",
                            class_name="text-xl font-bold text-gray-900 mb-4",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Welcome to the HEI Self-Assessment Dashboard. Please note that the scores and benchmarks displayed here are provisional results based on your initial data entry.",
                                class_name="text-sm text-gray-600 mb-4 leading-relaxed",
                            ),
                            rx.el.p(
                                "To ensure accuracy and official recognition, all submitted data is subject to a formal verification and audit by the Commission on Higher Education (CHED).",
                                class_name="text-sm text-gray-600 mb-6 leading-relaxed",
                            ),
                            rx.el.div(
                                rx.el.p(
                                    "Key Reminder: Results are not final until you receive official confirmation from CHED.",
                                    class_name="text-sm font-bold text-amber-800",
                                ),
                                class_name="bg-amber-50 border-l-4 border-amber-400 p-4 rounded-r-lg mb-8",
                            ),
                            class_name="text-left",
                        ),
                        rx.el.button(
                            "I Understand, Proceed to Dashboard",
                            on_click=HEIState.acknowledge_and_proceed,
                            class_name="w-full py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold text-sm shadow-lg shadow-blue-100 transition-all transform active:scale-[0.98]",
                        ),
                        class_name="bg-white rounded-[2rem] shadow-2xl p-10 max-w-lg w-full mx-4 text-center border border-gray-100",
                    ),
                    class_name="flex items-center justify-center min-h-screen",
                ),
                class_name="fixed inset-0 bg-gray-900/60 backdrop-blur-md z-[200] overflow-y-auto",
            )
        ),
        class_name=rx.cond(HEIState.show_preliminary_notice, "block", "hidden"),
    )


@rx.memo
def hei_dropdown_item(hei: HEI) -> rx.Component:
    return rx.el.button(
        rx.el.div(
            rx.el.div(
                rx.el.p(hei["name"], class_name="text-sm font-semibold text-gray-900"),
                class_name="text-left",
            ),
            rx.el.div(
                rx.el.span(
                    hei["address"],
                    class_name="text-xs text-gray-500 truncate block max-w-[200px]",
                ),
                class_name="text-right ml-auto",
            ),
            class_name="flex items-center justify-between w-full",
        ),
        on_click=HEIState.select_hei(hei),
        class_name="w-full px-4 py-3 hover:bg-blue-50 transition-colors border-b border-gray-100 last:border-0",
    )


def info_field(label: str, value: str) -> rx.Component:
    return rx.el.div(
        rx.el.p(
            label,
            class_name="text-[10px] font-bold text-gray-400 uppercase tracking-wider",
        ),
        rx.el.p(value, class_name="text-sm font-semibold text-gray-700"),
        class_name="flex flex-col gap-0.5",
    )


@rx.memo
def selected_hei_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("building-2", class_name="h-10 w-10 text-white"),
                    class_name="p-5 bg-blue-600 rounded-3xl mr-8 shadow-lg shadow-blue-200",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                HEIState.selected_hei["name"],
                                class_name="text-2xl font-black text-gray-900 tracking-tight leading-none",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    class_name="h-2 w-2 rounded-full bg-emerald-400 animate-pulse mr-2"
                                ),
                                rx.el.span(
                                    "Verified CHED Partner",
                                    class_name="text-[10px] font-black text-emerald-600 uppercase tracking-widest",
                                ),
                                class_name="flex items-center mt-2 bg-emerald-50 px-3 py-1 rounded-full w-fit",
                            ),
                            class_name="flex flex-col",
                        ),
                        rx.el.button(
                            rx.icon("refresh-cw", class_name="h-4 w-4 mr-2"),
                            "Change",
                            on_click=HEIState.deselect_hei,
                            class_name="flex items-center px-4 py-2 text-xs font-bold text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-xl border border-slate-200 transition-all",
                        ),
                        class_name="flex items-start justify-between w-full mb-8",
                    ),
                    rx.el.div(
                        info_field("Classification", HEIState.selected_hei["type"]),
                        info_field(
                            "Authorized Admin", HEIState.selected_hei["admin_name"]
                        ),
                        info_field("Location", HEIState.selected_hei["street"]),
                        info_field(
                            "City / Jurisdiction", HEIState.selected_hei["city"]
                        ),
                        class_name="grid grid-cols-1 sm:grid-cols-2 gap-y-6 gap-x-12 pt-8 border-t border-slate-100",
                    ),
                    class_name="flex-1",
                ),
                class_name="flex items-start",
            ),
            class_name="p-10",
        ),
        class_name="bg-white rounded-3xl border border-slate-100 border-l-[8px] border-l-blue-600 shadow-[0_20px_50px_-12px_rgba(0,0,0,0.05)] mb-12 animate-in fade-in slide-in-from-bottom-8 duration-500",
    )


def hei_selection_dropdown() -> rx.Component:
    return rx.el.div(
        rx.cond(
            HEIState.is_dropdown_open,
            rx.el.div(
                rx.cond(
                    HEIState.search_results.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            HEIState.search_results,
                            lambda hei: hei_dropdown_item(hei=hei, key=hei["id"]),
                        ),
                        class_name="max-h-[300px] overflow-y-auto",
                    ),
                    rx.cond(
                        ~HEIState.is_searching,
                        rx.el.div(
                            rx.el.p(
                                "No institutions found matching your criteria.",
                                class_name="text-sm text-gray-500 p-4 text-center",
                            )
                        ),
                    ),
                ),
                class_name="absolute z-[100] w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl animate-in fade-in slide-in-from-top-2",
            ),
        ),
        class_name="relative",
    )


def selection_screen_content() -> rx.Component:
    return rx.el.div(
        preliminary_notice_modal(),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon("school", class_name="h-8 w-8 text-white"),
                            class_name="p-4 bg-white/20 rounded-2xl backdrop-blur-md border border-white/30 mr-6",
                        ),
                        rx.el.div(
                            rx.el.h1(
                                "Select Higher Education Institution",
                                class_name="text-4xl font-bold text-white tracking-tighter",
                            ),
                            class_name="flex-1",
                        ),
                        class_name="flex items-center",
                    ),
                    class_name="max-w-5xl mx-auto px-10 py-12",
                ),
                class_name="relative overflow-hidden rounded-3xl bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 shadow-2xl mb-12",
            ),
            rx.cond(
                ~HEIState.is_registration_mode,
                rx.el.div(
                    rx.cond(
                        HEIState.selected_hei,
                        selected_hei_card(),
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    rx.cond(
                                        HEIState.is_searching,
                                        rx.el.div(
                                            class_name="absolute left-5 top-5 h-6 w-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin z-10"
                                        ),
                                        rx.icon(
                                            "search",
                                            class_name="absolute left-5 top-5 text-slate-400 h-6 w-6 z-10",
                                        ),
                                    ),
                                    rx.el.input(
                                        placeholder="Search your institution (e.g. University of Santo Tomas)...",
                                        on_change=HEIState.set_search_query.debounce(
                                            150
                                        ),
                                        on_focus=rx.cond(
                                            HEIState.search_query != "",
                                            HEIState.set_is_dropdown_open(True),
                                            rx.noop(),
                                        ),
                                        class_name="w-full pl-16 pr-16 py-5 bg-white/80 backdrop-blur-xl border border-slate-200 rounded-[2.5rem] focus:ring-8 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all shadow-[0_15px_40px_-15px_rgba(0,0,0,0.1)] text-xl font-medium placeholder-slate-400",
                                        default_value=HEIState.search_query,
                                    ),
                                    rx.cond(
                                        HEIState.search_query.length() > 0,
                                        rx.el.button(
                                            rx.icon("x", class_name="h-5 w-5"),
                                            on_click=HEIState.clear_search,
                                            class_name="absolute right-6 top-5 text-slate-400 hover:text-slate-600 transition-colors",
                                        ),
                                    ),
                                    class_name="relative mb-2",
                                ),
                                hei_selection_dropdown(),
                                class_name="relative mb-12",
                            ),
                            rx.el.div(
                                rx.el.div(class_name="h-px flex-1 bg-slate-100"),
                                rx.el.div(
                                    rx.el.span(
                                        "Missing your HEI?",
                                        class_name="text-sm text-slate-400 font-medium px-4",
                                    ),
                                    rx.el.button(
                                        rx.icon(
                                            "circle_plus", class_name="h-4 w-4 mr-2"
                                        ),
                                        "Register NEW HEI",
                                        on_click=HEIState.toggle_registration_mode,
                                        class_name="flex items-center px-6 py-2.5 bg-slate-50 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-full text-sm font-bold border border-slate-200 transition-all",
                                    ),
                                    class_name="flex flex-col items-center gap-4",
                                ),
                                rx.el.div(class_name="h-px flex-1 bg-slate-100"),
                                class_name="flex items-center justify-center gap-4 mb-12",
                            ),
                        ),
                    )
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("chevron-left", class_name="h-4 w-4 mr-1"),
                        "Return to Search",
                        on_click=HEIState.toggle_registration_mode,
                        class_name="flex items-center text-xs font-black uppercase tracking-widest text-slate-400 hover:text-blue-600 mb-6 transition-colors",
                    ),
                    registration_form(),
                    class_name="mb-12",
                ),
            ),
        ),
        rx.cond(
            HEIState.selected_hei | HEIState.is_registration_mode,
            rx.el.div(
                rx.el.div(
                    rx.icon("award", class_name="h-6 w-6 text-indigo-600 mr-3"),
                    rx.el.h2(
                        "Ranking Framework",
                        class_name="text-2xl font-black text-gray-900",
                    ),
                    class_name="flex items-center mb-8 pb-4 border-b border-slate-100",
                ),
                rx.el.div(
                    ranking_framework_option(
                        value="QS",
                        label="QS World University Rankings",
                        description="Evaluates based on academic reputation, employer reputation, and faculty impact metrics.",
                        icon="sparkles",
                    ),
                    ranking_framework_option(
                        value="THE",
                        label="THE World University Rankings",
                        description="Comprehensive assessment across teaching, research quality, and international outlook.",
                        icon="target",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12 animate-in fade-in slide-in-from-bottom-10 duration-700",
                ),
                rx.el.button(
                    rx.cond(
                        HEIState.is_loading,
                        rx.el.div(
                            rx.el.div(
                                class_name="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"
                            ),
                            "Syncing Selection...",
                            class_name="flex items-center justify-center",
                        ),
                        rx.el.div(
                            rx.el.span("Readiness Assessment Dashboard"),
                            rx.icon(
                                "arrow-right",
                                class_name="ml-3 h-6 w-6 inline-block group-hover:translate-x-1 transition-transform",
                            ),
                            class_name="group",
                        ),
                    ),
                    on_click=HEIState.submit_selection,
                    disabled=~HEIState.is_form_valid | HEIState.is_loading,
                    class_name=rx.cond(
                        HEIState.is_form_valid,
                        "w-full py-6 bg-gradient-to-r from-blue-700 to-indigo-800 hover:from-blue-800 hover:to-indigo-900 text-white rounded-[2rem] font-black text-xl shadow-[0_20px_40px_-15px_rgba(37,99,235,0.4)] transition-all transform active:scale-[0.98]",
                        "w-full py-6 bg-slate-200 text-slate-400 rounded-[2rem] font-black text-xl cursor-not-allowed",
                    ),
                ),
            ),
        ),
        class_name="max-w-5xl mx-auto w-full px-6",
    )