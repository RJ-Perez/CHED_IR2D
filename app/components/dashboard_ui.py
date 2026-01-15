import reflex as rx
from app.states.dashboard_state import DashboardState
from app.states.hei_state import HEIState


def text_input_metric(
    label: str,
    value: rx.Var,
    points: rx.Var,
    max_points: int,
    on_change: rx.event.EventType,
    error_msg: rx.Var = "",
) -> rx.Component:
    """Text box input for weighted metrics with standardized design tokens."""
    has_error = error_msg != ""
    return rx.el.div(
        rx.el.div(
            rx.el.label(
                label, class_name="text-sm font-semibold text-gray-800 tracking-tight"
            ),
            rx.el.div(
                rx.el.span(points, class_name="text-sm font-bold text-blue-700"),
                rx.el.span(
                    f" / {max_points} pts",
                    class_name="text-[10px] font-bold text-gray-400 uppercase tracking-widest ml-1",
                ),
                class_name="px-2 py-0.5 bg-blue-50 rounded-md border border-blue-100 flex items-baseline",
            ),
            class_name="flex items-center justify-between mb-4",
        ),
        rx.el.div(
            rx.el.input(
                type="number",
                min=0,
                max=100,
                step=1,
                pattern="[0-9]*",
                input_mode="numeric",
                placeholder="0 - 100",
                default_value=rx.cond(value == 0, "", value.to_string()),
                on_change=on_change.debounce(300),
                on_key_down=lambda key: rx.cond(
                    (key == ".")
                    | (key == "e")
                    | (key == "E")
                    | (key == "+")
                    | (key == "-"),
                    rx.event.prevent_default,
                    rx.noop(),
                ),
                class_name=rx.cond(
                    has_error,
                    "w-full text-center text-sm font-medium text-red-600 bg-red-50 border border-red-200 rounded-lg py-2.5 focus:ring-2 focus:ring-red-500 outline-none transition-all",
                    "w-full text-center text-sm font-medium text-slate-900 bg-gray-50 border border-gray-200 rounded-lg py-2.5 focus:ring-2 focus:ring-blue-500 outline-none transition-all hover:border-gray-300",
                ),
            ),
            class_name="relative",
        ),
        rx.cond(
            has_error,
            rx.el.div(
                rx.icon("triangle-alert", class_name="h-4 w-4 stroke-red-500 mr-2"),
                rx.el.span(error_msg),
                class_name="text-xs text-red-600 mt-2 flex items-center justify-center font-medium bg-red-50 py-2 rounded-lg",
            ),
            rx.el.div(
                rx.el.div(
                    class_name=rx.cond(value > 0, "bg-emerald-500", "bg-gray-200"),
                    style={"width": f"{value}%", "height": "4px"},
                ),
                class_name="w-full bg-gray-100 h-1 rounded-full mt-4 overflow-hidden flex",
            ),
        ),
        class_name="group p-6 bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow transition-all duration-300",
    )


def text_metric_card(
    label: str, placeholder: str, value: rx.Var, on_change: rx.event.EventType
) -> rx.Component:
    """Styled text input card used for qualitative/tracked metrics (0% weight)."""
    return rx.el.div(
        rx.el.div(
            rx.el.label(
                label, class_name="text-sm font-bold text-gray-800 tracking-tight"
            ),
            rx.el.div(
                rx.el.span(
                    "Tracked",
                    class_name="text-[10px] font-bold text-gray-400 uppercase tracking-widest",
                ),
                class_name="px-2.5 py-1 bg-slate-50 rounded-lg border border-slate-100",
            ),
            class_name="flex items-center justify-between mb-5",
        ),
        rx.el.div(
            rx.el.input(
                type="text",
                placeholder=placeholder,
                default_value=value,
                on_change=on_change.debounce(300),
                class_name="w-full text-center text-base font-bold text-slate-800 bg-slate-50 border border-slate-200 rounded-lg py-2.5 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all shadow-inner hover:border-slate-300",
            ),
            class_name="relative",
        ),
        rx.el.div(
            rx.el.p(
                "Note: This data is for institutional tracking and does not affect the readiness score.",
                class_name="text-[10px] text-gray-400 italic text-center mt-3",
            )
        ),
        class_name="group mb-6 p-6 bg-white rounded-3xl border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300",
    )


def file_upload_section(
    label: str,
    upload_id: str,
    handle_upload_event: rx.event.EventType,
    uploaded_files: rx.Var,
    is_uploading: rx.Var,
    delete_event: rx.event.EventType,
) -> rx.Component:
    """Reusable file upload section with auto-upload and progress indicator."""
    progress_var = rx.match(
        upload_id,
        ("upload_research", DashboardState.upload_progress_research),
        ("upload_employability", DashboardState.upload_progress_employability),
        ("upload_global_engagement", DashboardState.upload_progress_global_engagement),
        (
            "upload_learning_experience",
            DashboardState.upload_progress_learning_experience,
        ),
        ("upload_sustainability", DashboardState.upload_progress_sustainability),
        0,
    )
    count_var = rx.match(
        upload_id,
        ("upload_research", DashboardState.upload_count_research),
        ("upload_employability", DashboardState.upload_count_employability),
        ("upload_global_engagement", DashboardState.upload_count_global_engagement),
        ("upload_learning_experience", DashboardState.upload_count_learning_experience),
        ("upload_sustainability", DashboardState.upload_count_sustainability),
        "",
    )
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-gray-700 mb-2"),
        rx.el.div(
            rx.upload.root(
                rx.el.div(
                    rx.cond(
                        is_uploading,
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        class_name="bg-emerald-500 h-2.5 rounded-full transition-all duration-300",
                                        style={"width": f"{progress_var}%"},
                                    ),
                                    class_name="w-48 bg-gray-200 rounded-full h-2.5 mb-4",
                                ),
                                rx.el.p(
                                    f"Uploading {count_var}... {progress_var}%",
                                    class_name="text-sm text-emerald-600 font-bold",
                                ),
                                class_name="flex flex-col items-center justify-center",
                            ),
                            class_name="absolute inset-0 bg-white/90 backdrop-blur-sm flex items-center justify-center z-10 rounded-xl",
                        ),
                        None,
                    ),
                    rx.el.div(
                        rx.icon(
                            "cloud-upload", class_name="h-8 w-8 text-gray-400 mb-2"
                        ),
                        rx.el.p(
                            "Drag & drop evidence files here",
                            class_name="text-sm text-gray-500",
                        ),
                        rx.el.p(
                            "or click to browse",
                            class_name="text-xs text-gray-400 mt-1",
                        ),
                        class_name="flex flex-col items-center",
                    ),
                    class_name="relative flex flex-col items-center justify-center p-6 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer min-h-[140px]",
                ),
                id=upload_id,
                accept={
                    "application/pdf": [".pdf"],
                    "image/png": [".png"],
                    "image/jpeg": [".jpg"],
                },
                multiple=True,
                max_files=5,
                on_drop=handle_upload_event(rx.upload_files(upload_id=upload_id)),
                class_name="w-full",
            ),
            class_name="mb-4 relative",
        ),
        rx.el.div(
            rx.el.p(
                "Uploaded Evidence:",
                class_name="text-xs font-semibold text-gray-500 mt-3 uppercase tracking-wider mb-2",
            ),
            rx.cond(
                uploaded_files.length() > 0,
                rx.el.div(
                    rx.foreach(
                        uploaded_files,
                        lambda file: rx.el.div(
                            rx.el.div(
                                rx.icon(
                                    "check_check",
                                    class_name="h-4 w-4 text-green-500 mr-2 flex-shrink-0",
                                ),
                                rx.el.a(
                                    file.split("/").reverse()[0],
                                    href=rx.get_upload_url(file),
                                    target="_blank",
                                    class_name="hover:underline text-blue-600 truncate",
                                ),
                                class_name="flex items-center min-w-0",
                            ),
                            rx.el.button(
                                rx.icon("x", class_name="h-4 w-4"),
                                on_click=delete_event(file),
                                class_name="p-1 text-gray-400 hover:text-red-500 transition-colors rounded-full hover:bg-red-50",
                                title="Remove file",
                            ),
                            class_name="flex items-center justify-between text-sm py-1.5 px-2 bg-white border border-gray-100 rounded-lg mb-1 shadow-sm",
                        ),
                    ),
                    class_name="space-y-1",
                ),
                rx.el.p(
                    "No files uploaded yet.", class_name="text-sm text-gray-400 italic"
                ),
            ),
            class_name="bg-gray-50 p-3 rounded-xl border border-gray-100",
        ),
        class_name="mt-2",
    )


def progress_tracker() -> rx.Component:
    """Progress bar element for the bottom bar."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                "Assessment Progress",
                class_name="text-sm font-medium text-gray-700 mb-1",
            ),
            rx.el.div(
                f"{DashboardState.progress}%",
                class_name="text-sm font-bold text-emerald-600",
            ),
            class_name="flex justify-between items-center",
        ),
        rx.el.div(
            rx.el.div(
                class_name="bg-emerald-500 h-2.5 rounded-full transition-all duration-500 ease-in-out",
                style={"width": f"{DashboardState.progress}%"},
            ),
            class_name="w-full bg-gray-200 rounded-full h-2.5",
        ),
        class_name="flex-1",
    )


def dashboard_header() -> rx.Component:
    """Dynamic header showing selected HEI context with a modern banner design."""
    hei_name = rx.cond(
        HEIState.is_registration_mode,
        HEIState.reg_name,
        rx.cond(
            HEIState.selected_hei,
            HEIState.selected_hei["name"],
            "Institution Not Selected",
        ),
    )
    framework_name = rx.cond(
        HEIState.ranking_framework == "QS",
        "QS World University Rankings",
        rx.cond(
            HEIState.ranking_framework == "THE",
            "THE Impact Rankings",
            "Academic Assessment Framework",
        ),
    )
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("building-2", class_name="h-8 w-8 text-white"),
                        class_name="p-3 bg-white/20 rounded-2xl backdrop-blur-md border border-white/30 mr-6",
                    ),
                    rx.el.div(
                        rx.el.h1(
                            hei_name,
                            class_name="text-3xl font-extrabold text-white tracking-tight",
                        ),
                        rx.el.div(
                            rx.icon("award", class_name="h-4 w-4 text-blue-200 mr-2"),
                            rx.el.span(
                                framework_name,
                                class_name="text-sm font-semibold text-blue-50 uppercase tracking-widest",
                            ),
                            class_name="flex items-center mt-2 opacity-90",
                        ),
                        class_name="flex-1",
                    ),
                    class_name="flex items-center",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "Assessment Status",
                            class_name="text-[10px] font-bold text-blue-200 uppercase tracking-widest mb-1",
                        ),
                        rx.el.div(
                            rx.el.div(
                                class_name="h-2 w-2 rounded-full bg-emerald-400 animate-pulse mr-2"
                            ),
                            rx.el.span(
                                "Active Data Entry",
                                class_name="text-xs font-bold text-white uppercase",
                            ),
                            class_name="flex items-center bg-white/10 px-3 py-1.5 rounded-full border border-white/20",
                        ),
                        class_name="flex flex-col items-end",
                    ),
                    class_name="hidden sm:block",
                ),
                class_name="flex items-center justify-between",
            ),
            class_name="max-w-7xl mx-auto px-8 py-10",
        ),
        class_name="relative overflow-hidden rounded-3xl bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 shadow-xl mb-10",
    )


def bottom_action_bar() -> rx.Component:
    """Sticky-ready bottom bar containing progress and save functionality with a horizontal floating design."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "Submission Status",
                            class_name="text-[10px] font-bold text-gray-400 uppercase tracking-widest",
                        ),
                        rx.cond(
                            DashboardState.has_validation_errors,
                            rx.el.span(
                                "Action Required",
                                class_name="text-xs font-bold text-red-500",
                            ),
                            rx.el.span(
                                "Ready to Sync",
                                class_name="text-xs font-bold text-emerald-500",
                            ),
                        ),
                        class_name="flex flex-col mr-8 shrink-0",
                    ),
                    progress_tracker(),
                    class_name="flex items-center flex-1",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.cond(
                            DashboardState.is_saving,
                            rx.el.div(
                                rx.el.div(
                                    class_name="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"
                                ),
                                "Syncing Data...",
                                class_name="flex items-center",
                            ),
                            rx.el.div(
                                rx.icon("cloud-upload", class_name="h-5 w-5 mr-3"),
                                "Submit & Save",
                                class_name="flex items-center",
                            ),
                        ),
                        on_click=DashboardState.save_progress,
                        disabled=DashboardState.is_saving
                        | DashboardState.has_validation_errors,
                        class_name=rx.cond(
                            DashboardState.has_validation_errors,
                            "flex items-center justify-center px-6 py-3 bg-slate-200 text-slate-400 rounded-2xl shadow-lg cursor-not-allowed transition-all font-bold text-sm whitespace-nowrap",
                            "flex items-center justify-center px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl shadow-xl hover:shadow-blue-200 hover:scale-[1.01] active:scale-[0.99] focus:outline-none focus:ring-4 focus:ring-blue-100 transition-all disabled:opacity-70 font-bold text-sm whitespace-nowrap",
                        ),
                    ),
                    rx.cond(
                        DashboardState.save_successful,
                        rx.el.button(
                            rx.el.div(
                                rx.icon("bar-chart-2", class_name="h-5 w-5 mr-3"),
                                "View Results",
                                class_name="flex items-center",
                            ),
                            on_click=rx.redirect("/analytics"),
                            class_name="flex items-center justify-center px-6 py-3 bg-gradient-to-r from-emerald-500 to-green-600 text-white rounded-2xl shadow-xl hover:shadow-emerald-200 hover:scale-[1.01] active:scale-[0.99] focus:outline-none focus:ring-4 focus:ring-emerald-100 transition-all font-bold text-sm whitespace-nowrap",
                        ),
                    ),
                    class_name="flex items-center gap-4",
                ),
                class_name="flex items-center justify-between w-full gap-10",
            ),
            class_name="max-w-7xl mx-auto px-10 py-6",
        ),
        class_name="bg-white/90 backdrop-blur-xl border border-white/20 shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.1)] mt-12 sticky bottom-6 rounded-[2rem] mx-8 z-[40]",
    )


def data_entry_forms() -> rx.Component:
    """Main data entry area split by thematic sections using a 2-column layout."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("microscope", class_name="h-6 w-6 text-purple-600 mr-3"),
                rx.el.div(
                    rx.el.h3(
                        "Research and Discovery",
                        class_name="text-lg font-bold text-gray-900",
                    ),
                    rx.el.p(
                        "Weight: 50% | Academic Reputation: 30% | Citations per Faculty: 20%",
                        class_name="text-xs text-gray-500 mt-1",
                    ),
                ),
                class_name="flex items-center mb-4 border-b pb-2",
            ),
            rx.el.div(
                rx.el.div(
                    text_input_metric(
                        "Academic Reputation",
                        DashboardState.academic_reputation,
                        DashboardState.academic_reputation_points,
                        30,
                        DashboardState.set_academic_reputation,
                        DashboardState.academic_reputation_error,
                    ),
                    text_input_metric(
                        "Citations per Faculty",
                        DashboardState.citations_per_faculty,
                        DashboardState.citations_per_faculty_points,
                        20,
                        DashboardState.set_citations_per_faculty,
                        DashboardState.citations_per_faculty_error,
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "Research Section Total",
                                class_name="text-sm font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.p(
                                f"{DashboardState.research_section_total} / 50 pts",
                                class_name="text-xl font-black text-gray-900",
                            ),
                            class_name="flex flex-col",
                        ),
                        rx.el.div(
                            rx.el.div(
                                class_name="bg-blue-600 h-2 rounded-full transition-all duration-300",
                                style={
                                    "width": f"{DashboardState.research_section_total / 50 * 100}%"
                                },
                            ),
                            class_name="w-full bg-gray-200 rounded-full h-2 mt-2",
                        ),
                        class_name="bg-white border border-gray-200 p-4 rounded-xl shadow-sm mt-4",
                    ),
                    class_name="space-y-1",
                ),
                rx.el.div(
                    file_upload_section(
                        "Research Evidence (Reports, Certifications)",
                        "upload_research",
                        DashboardState.handle_research_upload,
                        DashboardState.uploaded_research_files,
                        DashboardState.is_uploading_research,
                        DashboardState.delete_research_file,
                    ),
                    class_name="p-5 bg-gray-50 rounded-2xl border border-gray-100 shadow-sm",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start",
            ),
            class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("briefcase", class_name="h-6 w-6 text-emerald-600 mr-3"),
                rx.el.div(
                    rx.el.h3(
                        "Employability and Outcomes",
                        class_name="text-lg font-bold text-gray-900",
                    ),
                    rx.el.p(
                        "Weight: 20% | Employer Reputation: 15% | Employment Outcomes: 5%",
                        class_name="text-xs text-gray-500 mt-1",
                    ),
                ),
                class_name="flex items-center mb-4 border-b pb-2",
            ),
            rx.el.div(
                rx.el.div(
                    text_input_metric(
                        "Employer Reputation",
                        DashboardState.employer_reputation,
                        DashboardState.employer_reputation_points,
                        15,
                        DashboardState.set_employer_reputation,
                        DashboardState.employer_reputation_error,
                    ),
                    text_input_metric(
                        "Employment Outcomes",
                        DashboardState.employment_outcomes,
                        DashboardState.employment_outcomes_points,
                        5,
                        DashboardState.set_employment_outcomes,
                        DashboardState.employment_outcomes_error,
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "Employability Section Total",
                                class_name="text-sm font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.p(
                                f"{DashboardState.employability_section_total} / 20 pts",
                                class_name="text-xl font-black text-gray-900",
                            ),
                            class_name="flex flex-col",
                        ),
                        rx.el.div(
                            rx.el.div(
                                class_name="bg-blue-600 h-2 rounded-full transition-all duration-300",
                                style={
                                    "width": f"{DashboardState.employability_section_total / 20 * 100}%"
                                },
                            ),
                            class_name="w-full bg-gray-200 rounded-full h-2 mt-2",
                        ),
                        class_name="bg-white border border-gray-200 p-4 rounded-xl shadow-sm mt-4",
                    ),
                    class_name="space-y-1",
                ),
                rx.el.div(
                    file_upload_section(
                        "Employability Evidence (Survey Data, Testimonials)",
                        "upload_employability",
                        DashboardState.handle_employability_upload,
                        DashboardState.uploaded_employability_files,
                        DashboardState.is_uploading_employability,
                        DashboardState.delete_employability_file,
                    ),
                    class_name="p-5 bg-gray-50 rounded-2xl border border-gray-100 shadow-sm",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start",
            ),
            class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("globe", class_name="h-6 w-6 text-blue-600 mr-3"),
                rx.el.div(
                    rx.el.h3(
                        "Global Engagement",
                        class_name="text-lg font-bold text-gray-900",
                    ),
                    rx.el.p(
                        "Weight: 15% | Research Network: 5% | Faculty Ratio: 5% | Student Ratio: 5% | Diversity: 0% (tracked)",
                        class_name="text-xs text-gray-500 mt-1",
                    ),
                ),
                class_name="flex items-center mb-4 border-b pb-2",
            ),
            rx.el.div(
                rx.el.div(
                    text_input_metric(
                        "International Research Network",
                        DashboardState.international_research_network,
                        DashboardState.international_research_network_points,
                        5,
                        DashboardState.set_international_research_network,
                        DashboardState.international_research_network_error,
                    ),
                    text_input_metric(
                        "International Faculty Ratio",
                        DashboardState.international_faculty_ratio,
                        DashboardState.international_faculty_ratio_points,
                        5,
                        DashboardState.set_international_faculty_ratio,
                        DashboardState.international_faculty_ratio_error,
                    ),
                    text_input_metric(
                        "International Student Ratio",
                        DashboardState.international_student_ratio,
                        DashboardState.international_student_ratio_points,
                        5,
                        DashboardState.set_international_student_ratio,
                        DashboardState.international_student_ratio_error,
                    ),
                    text_metric_card(
                        "International Student Diversity",
                        "e.g. 45 countries (Count and Origin)",
                        DashboardState.international_student_diversity,
                        DashboardState.set_international_student_diversity,
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "Global Engagement Total",
                                class_name="text-sm font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.p(
                                f"{DashboardState.global_engagement_section_total} / 15 pts",
                                class_name="text-xl font-black text-gray-900",
                            ),
                            class_name="flex flex-col",
                        ),
                        rx.el.div(
                            rx.el.div(
                                class_name="bg-blue-600 h-2 rounded-full transition-all duration-300",
                                style={
                                    "width": f"{DashboardState.global_engagement_section_total / 15 * 100}%"
                                },
                            ),
                            class_name="w-full bg-gray-200 rounded-full h-2 mt-2",
                        ),
                        class_name="bg-white border border-gray-200 p-4 rounded-xl shadow-sm mt-4",
                    ),
                    class_name="space-y-1",
                ),
                rx.el.div(
                    file_upload_section(
                        "Global Engagement Evidence (Partnerships, Agreements)",
                        "upload_global_engagement",
                        DashboardState.handle_global_engagement_upload,
                        DashboardState.uploaded_global_engagement_files,
                        DashboardState.is_uploading_global_engagement,
                        DashboardState.delete_global_engagement_file,
                    ),
                    class_name="p-5 bg-gray-50 rounded-2xl border border-gray-100 shadow-sm",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start",
            ),
            class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("graduation-cap", class_name="h-6 w-6 text-indigo-600 mr-3"),
                rx.el.div(
                    rx.el.h3(
                        "Learning Experience",
                        class_name="text-lg font-bold text-gray-900",
                    ),
                    rx.el.p(
                        "Weight: 10% | Faculty-Student Ratio: 10%",
                        class_name="text-xs text-gray-500 mt-1",
                    ),
                ),
                class_name="flex items-center mb-4 border-b pb-2",
            ),
            rx.el.div(
                rx.el.div(
                    text_input_metric(
                        "Faculty-Student Ratio",
                        DashboardState.faculty_student_ratio,
                        DashboardState.faculty_student_ratio_points,
                        10,
                        DashboardState.set_faculty_student_ratio,
                        DashboardState.faculty_student_ratio_error,
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "Learning Experience Total",
                                class_name="text-sm font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.p(
                                f"{DashboardState.learning_experience_section_total} / 10 pts",
                                class_name="text-xl font-black text-gray-900",
                            ),
                            class_name="flex flex-col",
                        ),
                        rx.el.div(
                            rx.el.div(
                                class_name="bg-blue-600 h-2 rounded-full transition-all duration-300",
                                style={
                                    "width": f"{DashboardState.learning_experience_section_total / 10 * 100}%"
                                },
                            ),
                            class_name="w-full bg-gray-200 rounded-full h-2 mt-2",
                        ),
                        class_name="bg-white border border-gray-200 p-4 rounded-xl shadow-sm mt-4",
                    ),
                    class_name="space-y-1",
                ),
                rx.el.div(
                    file_upload_section(
                        "Learning Experience Evidence (Class Size Reports, Faculty Data)",
                        "upload_learning_experience",
                        DashboardState.handle_learning_experience_upload,
                        DashboardState.uploaded_learning_experience_files,
                        DashboardState.is_uploading_learning_experience,
                        DashboardState.delete_learning_experience_file,
                    ),
                    class_name="p-5 bg-gray-50 rounded-2xl border border-gray-100 shadow-sm",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start",
            ),
            class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("leaf", class_name="h-6 w-6 text-green-600 mr-3"),
                rx.el.div(
                    rx.el.h3(
                        "Sustainability", class_name="text-lg font-bold text-gray-900"
                    ),
                    rx.el.p(
                        "Weight: 5% | Sustainability Metrics: 5%",
                        class_name="text-xs text-gray-500 mt-1",
                    ),
                ),
                class_name="flex items-center mb-4 border-b pb-2",
            ),
            rx.el.div(
                rx.el.div(
                    text_input_metric(
                        "Sustainability Metrics Score",
                        DashboardState.sustainability_metrics,
                        DashboardState.sustainability_metrics_points,
                        5,
                        DashboardState.set_sustainability_metrics,
                        DashboardState.sustainability_metrics_error,
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "Sustainability Total",
                                class_name="text-sm font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.p(
                                f"{DashboardState.sustainability_section_total} / 5 pts",
                                class_name="text-xl font-black text-gray-900",
                            ),
                            class_name="flex flex-col",
                        ),
                        rx.el.div(
                            rx.el.div(
                                class_name="bg-blue-600 h-2 rounded-full transition-all duration-300",
                                style={
                                    "width": f"{DashboardState.sustainability_section_total / 5 * 100}%"
                                },
                            ),
                            class_name="w-full bg-gray-200 rounded-full h-2 mt-2",
                        ),
                        class_name="bg-white border border-gray-200 p-4 rounded-xl shadow-sm mt-4",
                    ),
                    class_name="space-y-1",
                ),
                rx.el.div(
                    file_upload_section(
                        "Sustainability Evidence (ESG Reports, Environmental Certifications)",
                        "upload_sustainability",
                        DashboardState.handle_sustainability_upload,
                        DashboardState.uploaded_sustainability_files,
                        DashboardState.is_uploading_sustainability,
                        DashboardState.delete_sustainability_file,
                    ),
                    class_name="p-5 bg-gray-50 rounded-2xl border border-gray-100 shadow-sm",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start",
            ),
            class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
        ),
    )


def dashboard_stat_cards() -> rx.Component:
    """Row of summary cards for the assessment top-view."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("circle_check", class_name="h-6 w-6 text-emerald-600"),
                    class_name="p-3 bg-emerald-50 rounded-2xl",
                ),
                rx.el.div(
                    rx.el.p(
                        "Completion Rate",
                        class_name="text-xs font-bold text-gray-400 uppercase tracking-widest",
                    ),
                    rx.el.h3(
                        f"{DashboardState.progress}%",
                        class_name="text-2xl font-black text-slate-900 mt-1",
                    ),
                    class_name="ml-4",
                ),
                class_name="flex items-center",
            ),
            class_name="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("file-check-2", class_name="h-6 w-6 text-blue-600"),
                    class_name="p-3 bg-blue-50 rounded-2xl",
                ),
                rx.el.div(
                    rx.el.p(
                        "Evidence Files",
                        class_name="text-xs font-bold text-gray-400 uppercase tracking-widest",
                    ),
                    rx.el.h3(
                        f"{DashboardState.uploaded_research_files.length() + DashboardState.uploaded_employability_files.length() + DashboardState.uploaded_global_engagement_files.length() + DashboardState.uploaded_learning_experience_files.length() + DashboardState.uploaded_sustainability_files.length()}",
                        class_name="text-2xl font-black text-slate-900 mt-1",
                    ),
                    class_name="ml-4",
                ),
                class_name="flex items-center",
            ),
            class_name="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm",
        ),
        class_name="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10",
    )


def dashboard_content() -> rx.Component:
    """Aggregated assessment content view with improved spacing."""
    return rx.el.div(
        dashboard_header(),
        dashboard_stat_cards(),
        data_entry_forms(),
        bottom_action_bar(),
        class_name="max-w-7xl mx-auto pb-12 px-4",
    )