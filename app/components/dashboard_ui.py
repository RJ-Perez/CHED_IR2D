import reflex as rx
from app.states.dashboard_state import DashboardState
from app.states.hei_state import HEIState


def form_input(
    label: str, placeholder: str, value: rx.Var, on_change: rx.event.EventType
) -> rx.Component:
    """Standard form input for assessment."""
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-gray-700 mb-1"),
        rx.el.input(
            placeholder=placeholder,
            default_value=value,
            on_change=on_change,
            class_name="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors text-sm",
        ),
        class_name="mb-4",
    )


def synced_slider_input(
    label: str,
    value: rx.Var,
    points: rx.Var,
    max_points: int,
    on_change: rx.event.EventType,
) -> rx.Component:
    """Synced slider and number input for weighted metrics."""
    return rx.el.div(
        rx.el.div(
            rx.el.label(label, class_name="text-sm font-medium text-gray-700"),
            rx.el.span(
                f"{points} / {max_points} pts",
                class_name="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full",
            ),
            class_name="flex items-center justify-between mb-2",
        ),
        rx.el.div(
            rx.el.input(
                type="range",
                key=value.to_string(),
                default_value=value.to_string(),
                on_change=on_change.throttle(500),
                min=0,
                max=100,
                step=1,
                class_name="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600",
            ),
            rx.el.input(
                type="number",
                min=0,
                max=100,
                default_value=value.to_string(),
                on_change=on_change,
                class_name="w-20 px-2 py-1 bg-white border border-gray-300 rounded-lg text-sm text-center focus:ring-2 focus:ring-blue-500 outline-none transition-colors",
            ),
            class_name="flex items-center gap-4",
        ),
        class_name="mb-6 p-4 bg-gray-50/50 rounded-xl border border-gray-100",
    )


def file_upload_section(
    label: str,
    upload_id: str,
    handle_upload_event: rx.event.EventType,
    uploaded_files: rx.Var,
) -> rx.Component:
    """Reusable file upload section."""
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-gray-700 mb-2"),
        rx.el.div(
            rx.upload.root(
                rx.el.div(
                    rx.icon("cloud-upload", class_name="h-8 w-8 text-gray-400 mb-2"),
                    rx.el.p(
                        "Drag & drop evidence files here",
                        class_name="text-sm text-gray-500",
                    ),
                    rx.el.p(
                        "or click to browse", class_name="text-xs text-gray-400 mt-1"
                    ),
                    class_name="flex flex-col items-center justify-center p-6 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer",
                ),
                id=upload_id,
                accept={
                    "application/pdf": [".pdf"],
                    "image/png": [".png"],
                    "image/jpeg": [".jpg"],
                },
                multiple=True,
                max_files=5,
                class_name="w-full",
            ),
            rx.el.div(
                rx.foreach(
                    rx.selected_files(upload_id),
                    lambda file: rx.el.div(
                        rx.icon("file", class_name="h-4 w-4 mr-2"),
                        rx.el.span(file),
                        class_name="flex items-center text-sm text-gray-600 mt-1",
                    ),
                ),
                class_name="mt-2",
            ),
            rx.el.button(
                "Upload Selected Files",
                on_click=handle_upload_event(rx.upload_files(upload_id=upload_id)),
                class_name="mt-2 text-sm text-blue-600 hover:text-blue-800 font-medium",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.p(
                "Uploaded Evidence:",
                class_name="text-xs font-semibold text-gray-500 mt-3 uppercase tracking-wider mb-2",
            ),
            rx.cond(
                uploaded_files.length() > 0,
                rx.foreach(
                    uploaded_files,
                    lambda file: rx.el.div(
                        rx.icon(
                            "check_check", class_name="h-4 w-4 text-green-500 mr-2"
                        ),
                        rx.el.a(
                            file,
                            href=rx.get_upload_url(file),
                            target="_blank",
                            class_name="hover:underline text-blue-600",
                        ),
                        class_name="flex items-center text-sm py-1",
                    ),
                ),
                rx.el.p(
                    "No files uploaded yet.", class_name="text-sm text-gray-400 italic"
                ),
            ),
            class_name="bg-gray-50 p-3 rounded-lg border border-gray-100",
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
                class_name="text-sm font-bold text-blue-600",
            ),
            class_name="flex justify-between items-center",
        ),
        rx.el.div(
            rx.el.div(
                class_name="bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-in-out",
                style={"width": f"{DashboardState.progress}%"},
            ),
            class_name="w-full bg-gray-200 rounded-full h-2.5",
        ),
        class_name="flex-1",
    )


def dashboard_header() -> rx.Component:
    """Dynamic header showing selected HEI context."""
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
        "QS University Rankings",
        rx.cond(
            HEIState.ranking_framework == "THE",
            "THE Impact Assessment",
            "Ranking Assessment",
        ),
    )
    return rx.el.div(
        rx.el.div(
            rx.el.h1(hei_name, class_name="text-2xl font-bold text-gray-900"),
            rx.el.div(
                rx.icon("award", class_name="h-5 w-5 text-amber-500 mr-2"),
                rx.el.span(framework_name, class_name="font-medium text-gray-600"),
                class_name="flex items-center mt-1",
            ),
            class_name="flex-1",
        ),
        class_name="flex items-center justify-between mb-8",
    )


def bottom_action_bar() -> rx.Component:
    """Sticky-ready bottom bar containing progress and save functionality."""
    return rx.el.div(
        rx.el.div(
            progress_tracker(),
            rx.el.button(
                rx.cond(
                    DashboardState.is_saving,
                    rx.el.div(
                        rx.el.div(
                            class_name="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"
                        ),
                        "Saving...",
                        class_name="flex items-center",
                    ),
                    rx.el.div(
                        rx.icon("save", class_name="h-4 w-4 mr-2"),
                        "Save Progress",
                        class_name="flex items-center",
                    ),
                ),
                on_click=DashboardState.save_progress,
                disabled=DashboardState.is_saving,
                class_name="flex items-center px-6 py-2.5 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors disabled:opacity-70 font-semibold",
            ),
            class_name="flex items-center gap-8",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm mt-8 sticky bottom-0",
    )


def data_entry_forms() -> rx.Component:
    """Main data entry area split by thematic sections."""
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
                    synced_slider_input(
                        "Academic Reputation",
                        DashboardState.academic_reputation,
                        DashboardState.academic_reputation_points,
                        30,
                        DashboardState.set_academic_reputation,
                    ),
                    synced_slider_input(
                        "Citations per Faculty",
                        DashboardState.citations_per_faculty,
                        DashboardState.citations_per_faculty_points,
                        20,
                        DashboardState.set_citations_per_faculty,
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
                    ),
                    class_name="mt-2",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-8",
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
                    form_input(
                        "Employer Reputation Score",
                        "e.g. 85/100 (Weight: 15%)",
                        DashboardState.employer_reputation,
                        DashboardState.set_employer_reputation,
                    ),
                    form_input(
                        "Employment Outcomes (Graduate Employment Rate %)",
                        "e.g. 94.5 (Weight: 5%)",
                        DashboardState.employment_outcomes,
                        DashboardState.set_employment_outcomes,
                    ),
                    class_name="space-y-1",
                ),
                rx.el.div(
                    file_upload_section(
                        "Employability Evidence (Survey Data, Testimonials)",
                        "upload_employability",
                        DashboardState.handle_employability_upload,
                        DashboardState.uploaded_employability_files,
                    ),
                    class_name="mt-2",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-8",
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
                    form_input(
                        "International Research Network Score",
                        "e.g. 75/100 (Weight: 5%)",
                        DashboardState.international_research_network,
                        DashboardState.set_international_research_network,
                    ),
                    form_input(
                        "International Faculty Ratio (%)",
                        "e.g. 12.5 (Weight: 5%)",
                        DashboardState.international_faculty_ratio,
                        DashboardState.set_international_faculty_ratio,
                    ),
                    form_input(
                        "International Student Ratio (%)",
                        "e.g. 8.3 (Weight: 5%)",
                        DashboardState.international_student_ratio,
                        DashboardState.set_international_student_ratio,
                    ),
                    form_input(
                        "International Student Diversity (Countries)",
                        "e.g. 45 countries (Tracked, 0% weight)",
                        DashboardState.international_student_diversity,
                        DashboardState.set_international_student_diversity,
                    ),
                    class_name="space-y-1",
                ),
                rx.el.div(
                    file_upload_section(
                        "Global Engagement Evidence (Partnerships, Agreements)",
                        "upload_global_engagement",
                        DashboardState.handle_global_engagement_upload,
                        DashboardState.uploaded_global_engagement_files,
                    ),
                    class_name="mt-2",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-8",
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
                    form_input(
                        "Faculty-Student Ratio",
                        "e.g. 1:15 (Weight: 10%)",
                        DashboardState.faculty_student_ratio,
                        DashboardState.set_faculty_student_ratio,
                    ),
                    class_name="space-y-1",
                ),
                rx.el.div(
                    file_upload_section(
                        "Learning Experience Evidence (Class Size Reports, Faculty Data)",
                        "upload_learning_experience",
                        DashboardState.handle_learning_experience_upload,
                        DashboardState.uploaded_learning_experience_files,
                    ),
                    class_name="mt-2",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-8",
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
                    form_input(
                        "Sustainability Metrics Score",
                        "e.g. 80/100 (Weight: 5%)",
                        DashboardState.sustainability_metrics,
                        DashboardState.set_sustainability_metrics,
                    ),
                    class_name="space-y-1",
                ),
                rx.el.div(
                    file_upload_section(
                        "Sustainability Evidence (ESG Reports, Environmental Certifications)",
                        "upload_sustainability",
                        DashboardState.handle_sustainability_upload,
                        DashboardState.uploaded_sustainability_files,
                    ),
                    class_name="mt-2",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-8",
            ),
            class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
        ),
    )


def dashboard_content() -> rx.Component:
    """Aggregated assessment content view."""
    return rx.el.div(
        dashboard_header(),
        data_entry_forms(),
        bottom_action_bar(),
        class_name="max-w-6xl mx-auto pb-12",
    )