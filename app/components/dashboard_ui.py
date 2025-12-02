import reflex as rx
from app.states.dashboard_state import DashboardState
from app.states.hei_state import HEIState


def form_input(
    label: str, placeholder: str, value: rx.Var, on_change: rx.event.EventType
) -> rx.Component:
    """Standard form input for dashboard."""
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
    """Top progress bar component."""
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
        class_name="bg-white p-4 rounded-xl border border-gray-200 shadow-sm mb-6",
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
        "QS Stars Assessment",
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
            class_name="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors disabled:opacity-70",
        ),
        class_name="flex items-center justify-between mb-6",
    )


def data_entry_forms() -> rx.Component:
    """Main data entry area split by thematic sections."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("microscope", class_name="h-6 w-6 text-purple-600 mr-3"),
                rx.el.h3(
                    "Research and Discovery",
                    class_name="text-lg font-bold text-gray-900",
                ),
                class_name="flex items-center mb-4 border-b pb-2",
            ),
            rx.el.div(
                rx.el.div(
                    form_input(
                        "Total Research Output",
                        "e.g. 1,250 publications",
                        DashboardState.research_output,
                        DashboardState.set_research_output,
                    ),
                    form_input(
                        "Citations per Faculty",
                        "e.g. 15.4",
                        DashboardState.citations,
                        DashboardState.set_citations,
                    ),
                    form_input(
                        "Grants Secured (PHP)",
                        "e.g. 50,000,000",
                        DashboardState.grants,
                        DashboardState.set_grants,
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
                rx.el.h3(
                    "Employability and Outcomes",
                    class_name="text-lg font-bold text-gray-900",
                ),
                class_name="flex items-center mb-4 border-b pb-2",
            ),
            rx.el.div(
                rx.el.div(
                    form_input(
                        "Graduate Employment Rate (%)",
                        "e.g. 94.5",
                        DashboardState.employment_rate,
                        DashboardState.set_employment_rate,
                    ),
                    form_input(
                        "Employer Reputation Score",
                        "e.g. 85/100",
                        DashboardState.employer_reputation,
                        DashboardState.set_employer_reputation,
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
            class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
        ),
    )


def dashboard_content() -> rx.Component:
    """Aggregated dashboard content view."""
    return rx.el.div(
        dashboard_header(),
        progress_tracker(),
        data_entry_forms(),
        class_name="max-w-6xl mx-auto",
    )