import reflex as rx
from app.states.dashboard_state import DashboardState
from app.states.hei_state import HEIState
from app.components.design_system import DS


def numeric_input_metric(
    label: str,
    value: rx.Var,
    points: rx.Var,
    max_points: int,
    on_change: rx.event.EventType,
) -> rx.Component:
    """Numeric text input for weighted metrics with real-time feedback and validation warnings."""
    field_key_map = {
        "Academic Reputation": "academic_reputation",
        "Domestic Nominations": "domestic_nominations",
        "International Nominations": "international_nominations",
        "Citations per Faculty": "citations_per_faculty",
        "Employer Reputation": "employer_reputation",
        "Employment Outcomes": "employment_outcomes",
        "International Research Network": "international_research_network",
        "International Faculty Ratio": "international_faculty_ratio",
        "International Student Ratio": "international_student_ratio",
        "Faculty-Student Ratio": "faculty_student_ratio",
        "Sustainability Metrics Score": "sustainability_metrics",
        "Employer Domestic Nominations": "employer_domestic_nominations",
        "Employer International Nominations": "employer_international_nominations",
    }
    field_key = field_key_map.get(label, "")
    error_msg = DashboardState.validation_errors[field_key]
    has_error = error_msg != ""
    return rx.el.div(
        rx.el.div(
            rx.el.label(
                label, class_name="text-sm font-semibold text-slate-800 tracking-tight"
            ),
            rx.el.div(
                rx.el.span(points, class_name=f"text-sm font-bold text-{DS.PRIMARY}"),
                rx.el.span(
                    f" / {max_points} pts",
                    class_name="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1",
                ),
                class_name=f"px-2 py-0.5 bg-{DS.PRIMARY_LIGHT} rounded-md border border-blue-100 flex items-baseline",
            ),
            class_name="flex items-center justify-between mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.input(
                    type="number",
                    on_change=on_change.debounce(300),
                    min=0,
                    max=100,
                    placeholder="0-100",
                    class_name=rx.cond(
                        has_error,
                        f"w-full px-4 py-2.5 bg-{DS.ERROR_BG} border border-{DS.ERROR} rounded-xl focus:ring-4 focus:ring-red-100 outline-none transition-all text-center text-lg font-bold text-red-900",
                        f"w-full px-4 py-2.5 bg-{DS.NEUTRAL_LIGHT} border border-{DS.BORDER} rounded-xl focus:ring-4 focus:ring-blue-100 focus:border-{DS.PRIMARY} outline-none transition-all text-center text-lg font-bold text-slate-900",
                    ),
                    default_value=rx.cond(value == 0, "", value.to_string()),
                ),
                class_name="relative",
            ),
            rx.cond(
                has_error,
                rx.el.div(
                    rx.icon("wheat", class_name="h-3 w-3 text-red-500 mr-1.5"),
                    rx.el.span(
                        error_msg,
                        class_name="text-[10px] font-bold text-red-500 uppercase",
                    ),
                    class_name="flex items-center mt-2 animate-in fade-in slide-in-from-top-1",
                ),
                None,
            ),
            class_name="space-y-1",
        ),
        class_name=f"group p-6 bg-white rounded-2xl border border-{DS.BORDER} shadow-sm hover:shadow transition-all duration-300",
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
        rx.el.label(
            label,
            class_name="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2",
        ),
        rx.el.div(
            rx.upload.root(
                rx.el.div(
                    rx.cond(
                        is_uploading,
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        class_name=f"bg-{DS.SUCCESS} h-2.5 rounded-full transition-all duration-300",
                                        style={
                                            "width": str(progress_var).join(["", "%"])
                                        },
                                    ),
                                    class_name="w-48 bg-slate-200 rounded-full h-2.5 mb-4",
                                ),
                                rx.el.p(
                                    f"Uploading {count_var}... {progress_var}%",
                                    class_name=f"text-sm text-{DS.SUCCESS} font-bold",
                                ),
                                class_name="flex flex-col items-center justify-center",
                            ),
                            class_name="absolute inset-0 bg-white/90 backdrop-blur-sm flex items-center justify-center z-50 rounded-2xl",
                        ),
                        None,
                    ),
                    rx.el.div(
                        rx.icon(
                            "cloud-upload", class_name="h-8 w-8 text-slate-400 mb-2"
                        ),
                        rx.el.p(
                            "Drag & drop evidence files here",
                            class_name="text-sm text-slate-500 font-medium",
                        ),
                        rx.el.p(
                            "or click to browse",
                            class_name="text-xs text-slate-400 mt-1",
                        ),
                        class_name="flex flex-col items-center",
                    ),
                    class_name=f"relative flex flex-col items-center justify-center p-6 border-2 border-dashed border-{DS.BORDER} rounded-2xl bg-{DS.NEUTRAL_LIGHT} hover:bg-slate-100 transition-colors cursor-pointer min-h-[140px]",
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
                key=is_uploading.to_string(),
                class_name="w-full",
            ),
            class_name="mb-4 relative",
        ),
        rx.el.div(
            rx.el.p(
                "Uploaded Evidence:",
                class_name="text-[10px] font-bold text-slate-400 mt-3 uppercase tracking-widest mb-2",
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
                                    class_name=f"h-4 w-4 text-{DS.SUCCESS} mr-2 flex-shrink-0",
                                ),
                                rx.el.a(
                                    file.split("/").reverse()[0],
                                    href=rx.get_upload_url(file),
                                    target="_blank",
                                    class_name=f"hover:underline text-{DS.PRIMARY} truncate font-medium",
                                ),
                                class_name="flex items-center min-w-0",
                            ),
                            rx.el.button(
                                rx.icon("x", class_name="h-4 w-4"),
                                on_click=delete_event(file),
                                class_name=f"p-1 text-slate-400 hover:text-{DS.ERROR} transition-colors rounded-full hover:bg-red-50",
                                title="Remove file",
                            ),
                            class_name=f"flex items-center justify-between text-sm py-1.5 px-2 bg-white border border-{DS.BORDER} rounded-lg mb-1 shadow-sm",
                        ),
                    ),
                    class_name="space-y-1",
                ),
                rx.el.p(
                    "No files uploaded yet.", class_name="text-xs text-slate-400 italic"
                ),
            ),
            class_name=f"bg-{DS.NEUTRAL_LIGHT} p-3 rounded-2xl border border-{DS.BORDER}",
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


def notification_item(notif: dict) -> rx.Component:
    """Renders a single notification entry for the review status using real DB values."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.match(
                    notif["status"],
                    (
                        "Reviewed",
                        rx.icon(
                            "lamp_wall_down", class_name="text-emerald-500 h-4 w-4"
                        ),
                    ),
                    (
                        "Approved",
                        rx.icon(
                            "lamp_wall_down", class_name="text-emerald-500 h-4 w-4"
                        ),
                    ),
                    ("Declined", rx.icon("wheat", class_name="text-rose-500 h-4 w-4")),
                    (
                        "In Progress",
                        rx.icon("clock", class_name="text-amber-500 h-4 w-4"),
                    ),
                    rx.icon("bell", class_name="text-blue-500 h-4 w-4"),
                ),
                rx.el.span(
                    notif["status"],
                    class_name=rx.match(
                        notif["status"],
                        (
                            "Reviewed",
                            "text-[10px] font-bold text-emerald-600 uppercase ml-2",
                        ),
                        (
                            "Approved",
                            "text-[10px] font-bold text-emerald-600 uppercase ml-2",
                        ),
                        (
                            "Declined",
                            "text-[10px] font-bold text-rose-600 uppercase ml-2",
                        ),
                        (
                            "In Progress",
                            "text-[10px] font-bold text-amber-600 uppercase ml-2",
                        ),
                        "text-[10px] font-bold text-blue-600 uppercase ml-2",
                    ),
                ),
                class_name="flex items-center mb-1",
            ),
            rx.el.p(
                notif["comments"],
                class_name="text-sm text-slate-700 font-medium leading-relaxed",
            ),
            rx.el.div(
                rx.el.span(
                    notif["reviewer_name"],
                    class_name="text-[10px] font-bold text-slate-400 uppercase tracking-tight",
                ),
                class_name="mt-2 flex items-center",
            ),
            class_name="flex-1",
        ),
        class_name=rx.match(
            notif["status"],
            (
                "Reviewed",
                "p-5 border-l-4 border-emerald-500 bg-emerald-50/30 hover:bg-emerald-50 transition-colors border-b border-slate-100",
            ),
            (
                "Approved",
                "p-5 border-l-4 border-emerald-500 bg-emerald-50/30 hover:bg-emerald-50 transition-colors border-b border-slate-100",
            ),
            (
                "Declined",
                "p-5 border-l-4 border-rose-500 bg-rose-50/30 hover:bg-rose-50 transition-colors border-b border-slate-100",
            ),
            (
                "In Progress",
                "p-5 border-l-4 border-amber-500 bg-amber-50/30 hover:bg-amber-50 transition-colors border-b border-slate-100",
            ),
            "p-5 border-l-4 border-blue-500 bg-blue-50/30 hover:bg-blue-50 transition-colors border-b border-slate-100",
        ),
    )


def notification_bell() -> rx.Component:
    """Renders the notification bell icon with dropdown logic."""
    from app.states.notification_state import NotificationState

    return rx.el.div(
        rx.el.button(
            rx.icon("bell", class_name="h-6 w-6 text-white"),
            rx.cond(
                NotificationState.unread_count > 0,
                rx.el.span(
                    NotificationState.unread_count,
                    class_name="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white ring-2 ring-blue-900",
                ),
            ),
            on_click=NotificationState.toggle_notifications,
            class_name="relative p-2 rounded-xl hover:bg-white/10 transition-colors",
        ),
        rx.cond(
            NotificationState.show_notifications,
            rx.el.div(
                rx.el.div(
                    on_click=NotificationState.toggle_notifications,
                    class_name="fixed inset-0 z-[90] bg-black/5 cursor-default",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.h4(
                            "Review Notifications",
                            class_name="text-base font-bold text-slate-900",
                        ),
                        rx.el.button(
                            rx.icon("x", class_name="h-5 w-5"),
                            on_click=NotificationState.toggle_notifications,
                            class_name="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-all",
                        ),
                        class_name="flex items-center justify-between p-5 border-b border-slate-100 bg-white sticky top-0 z-10",
                    ),
                    rx.el.div(
                        rx.cond(
                            NotificationState.notifications.length() > 0,
                            rx.el.div(
                                rx.foreach(
                                    NotificationState.notifications, notification_item
                                ),
                                class_name="max-h-[450px] overflow-y-auto scrollbar-thin scrollbar-thumb-slate-200 min-h-[150px]",
                            ),
                            rx.el.div(
                                rx.icon(
                                    "bell-off",
                                    class_name="h-12 w-12 text-slate-200 mb-4",
                                ),
                                rx.el.p(
                                    "No review updates yet.",
                                    class_name="text-sm text-slate-400 font-bold uppercase tracking-widest",
                                ),
                                class_name="flex flex-col items-center justify-center py-20 bg-slate-50",
                            ),
                        )
                    ),
                    class_name="fixed top-24 right-12 w-[400px] bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden z-[100] animate-in fade-in slide-in-from-top-4 duration-300",
                ),
                class_name="z-[100]",
            ),
        ),
        class_name="relative",
    )


def dashboard_header() -> rx.Component:
    """Dynamic header showing selected HEI context with a modern banner design."""
    from app.states.historical_state import HistoricalState

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
        rx.cond(
            DashboardState.review_status == "For Review",
            rx.el.div(
                rx.el.div(
                    rx.icon("info", class_name="h-5 w-5 text-blue-600 mr-3"),
                    rx.el.p(
                        "Your assessment is currently under formal verification and audit by CHED. Edits made now will be tracked for the next review cycle.",
                        class_name="text-sm font-semibold text-blue-800",
                    ),
                    class_name="flex items-center",
                ),
                class_name="bg-blue-50 border-b border-blue-100 px-8 py-3",
            ),
        ),
        rx.cond(
            HistoricalState.years_count > 0,
            rx.el.div(
                rx.el.div(
                    rx.icon("history", class_name="h-5 w-5 text-amber-600 mr-3"),
                    rx.el.p(
                        rx.el.span(
                            "Historical Data Available: ", class_name="font-bold"
                        ),
                        rx.el.span(
                            f"Records found for {HistoricalState.years_count} previous cycles. "
                        ),
                        rx.el.a(
                            "View multi-year trends →",
                            href="/historical",
                            class_name="underline font-bold text-amber-700 hover:text-amber-800 ml-1",
                        ),
                        class_name="text-sm text-amber-800",
                    ),
                    class_name="flex items-center",
                ),
                class_name="bg-amber-50 border-b border-amber-100 px-8 py-2",
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("building-2", class_name="h-8 w-8 text-white"),
                        class_name="p-3 bg-white/20 rounded-2xl backdrop-blur-md border border-white/30 mr-6",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.h1(
                                hei_name,
                                class_name="text-3xl font-extrabold text-white tracking-tight",
                            ),
                            notification_bell(),
                            class_name="flex items-center justify-between gap-4",
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
                            "Institutional Status",
                            class_name="text-[10px] font-bold text-blue-200 uppercase tracking-widest mb-1.5",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    class_name="h-2 w-2 rounded-full bg-emerald-400 animate-pulse mr-2"
                                ),
                                rx.el.span(
                                    "Active Data Entry",
                                    class_name="text-xs font-bold text-white uppercase",
                                ),
                                class_name="flex items-center bg-white/10 px-3 py-1.5 rounded-full border border-white/20 mb-2",
                            ),
                            rx.match(
                                DashboardState.review_status,
                                (
                                    "For Review",
                                    rx.el.div(
                                        rx.el.div(
                                            class_name="h-2 w-2 rounded-full bg-blue-400 animate-pulse mr-2"
                                        ),
                                        rx.el.span(
                                            "Under Review",
                                            class_name="text-[10px] font-bold text-blue-100 uppercase",
                                        ),
                                        class_name="flex items-center bg-blue-600/40 px-3 py-1.5 rounded-full border border-blue-300/30",
                                    ),
                                ),
                                (
                                    "Reviewed",
                                    rx.el.div(
                                        rx.icon(
                                            "warehouse",
                                            class_name="h-3 w-3 text-emerald-400 mr-1.5",
                                        ),
                                        rx.el.span(
                                            "Approved",
                                            class_name="text-[10px] font-bold text-emerald-50 uppercase",
                                        ),
                                        class_name="flex items-center bg-emerald-600/40 px-3 py-1.5 rounded-full border border-emerald-300/30",
                                    ),
                                ),
                                (
                                    "Declined",
                                    rx.el.div(
                                        rx.icon(
                                            "wheat",
                                            class_name="h-3 w-3 text-rose-400 mr-1.5",
                                        ),
                                        rx.el.span(
                                            "Declined",
                                            class_name="text-[10px] font-bold text-rose-50 uppercase",
                                        ),
                                        class_name="flex items-center bg-rose-600/40 px-3 py-1.5 rounded-full border border-rose-300/30",
                                    ),
                                ),
                                (
                                    "In Progress",
                                    rx.el.div(
                                        rx.el.div(
                                            class_name="h-2 w-2 rounded-full bg-amber-400 animate-pulse mr-2"
                                        ),
                                        rx.el.span(
                                            "In Progress",
                                            class_name="text-[10px] font-bold text-amber-100 uppercase",
                                        ),
                                        class_name="flex items-center bg-amber-600/40 px-3 py-1.5 rounded-full border border-amber-300/30",
                                    ),
                                ),
                                rx.el.div(
                                    rx.el.span(
                                        "Pending Review",
                                        class_name="text-[10px] font-bold text-slate-100 uppercase",
                                    ),
                                    class_name="flex items-center bg-white/5 px-3 py-1.5 rounded-full border border-white/10",
                                ),
                            ),
                            class_name="flex flex-col items-end",
                        ),
                        class_name="flex flex-col items-end",
                    ),
                    class_name="hidden sm:block",
                ),
                class_name="flex items-center justify-between",
            ),
            class_name="max-w-7xl mx-auto px-8 py-10",
        ),
        class_name="relative rounded-3xl bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 shadow-xl mb-10",
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
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.h4(
                                    "Academic Reputation (30%)",
                                    class_name="text-base font-bold text-slate-900",
                                ),
                                rx.el.p(
                                    "Weights: International (85%) | Domestic (15%)",
                                    class_name="text-[10px] font-bold text-slate-400 uppercase",
                                ),
                                class_name="flex flex-col",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    DashboardState.academic_reputation_points,
                                    class_name=f"text-lg font-black text-{DS.PRIMARY}",
                                ),
                                rx.el.span(
                                    " / 30 pts",
                                    class_name="text-xs font-bold text-slate-400 ml-1",
                                ),
                                class_name="bg-blue-50 px-3 py-1 rounded-xl border border-blue-100",
                            ),
                            class_name="flex items-center justify-between mb-6 border-b border-slate-50 pb-4",
                        ),
                        rx.el.div(
                            numeric_input_metric(
                                label="International Nominations",
                                value=DashboardState.international_nominations,
                                points=DashboardState.international_nominations_points,
                                max_points=25.5,
                                on_change=DashboardState.set_international_nominations,
                            ),
                            numeric_input_metric(
                                label="Domestic Nominations",
                                value=DashboardState.domestic_nominations,
                                points=DashboardState.domestic_nominations_points,
                                max_points=4.5,
                                on_change=DashboardState.set_domestic_nominations,
                            ),
                            class_name="grid grid-cols-1 sm:grid-cols-2 gap-4",
                        ),
                        class_name="p-6 bg-white rounded-2xl border border-slate-200 shadow-sm mb-4",
                    ),
                    numeric_input_metric(
                        label="Citations per Faculty",
                        value=DashboardState.citations_per_faculty,
                        points=DashboardState.citations_per_faculty_points,
                        max_points=20,
                        on_change=DashboardState.set_citations_per_faculty,
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
                        label="Research Evidence (Reports, Certifications)",
                        upload_id="upload_research",
                        handle_upload_event=DashboardState.handle_research_upload,
                        uploaded_files=DashboardState.uploaded_research_files,
                        is_uploading=DashboardState.is_uploading_research,
                        delete_event=DashboardState.delete_research_file,
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
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.h4(
                                    "Employer Reputation (15%)",
                                    class_name="text-base font-bold text-slate-900",
                                ),
                                rx.el.p(
                                    "Weights: Domestic (50%) | International (50%)",
                                    class_name="text-[10px] font-bold text-slate-400 uppercase",
                                ),
                                class_name="flex flex-col",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    DashboardState.employer_reputation_points,
                                    class_name=f"text-lg font-black text-{DS.PRIMARY}",
                                ),
                                rx.el.span(
                                    " / 15 pts",
                                    class_name="text-xs font-bold text-slate-400 ml-1",
                                ),
                                class_name="bg-blue-50 px-3 py-1 rounded-xl border border-blue-100",
                            ),
                            class_name="flex items-center justify-between mb-6 border-b border-slate-50 pb-4",
                        ),
                        rx.el.div(
                            numeric_input_metric(
                                label="Employer Domestic Nominations",
                                value=DashboardState.employer_domestic_nominations,
                                points=DashboardState.employer_domestic_nominations_points,
                                max_points=7.5,
                                on_change=DashboardState.set_employer_domestic_nominations,
                            ),
                            numeric_input_metric(
                                label="Employer International Nominations",
                                value=DashboardState.employer_international_nominations,
                                points=DashboardState.employer_international_nominations_points,
                                max_points=7.5,
                                on_change=DashboardState.set_employer_international_nominations,
                            ),
                            class_name="grid grid-cols-1 sm:grid-cols-2 gap-4",
                        ),
                        class_name="p-6 bg-white rounded-2xl border border-slate-200 shadow-sm mb-4",
                    ),
                    numeric_input_metric(
                        label="Employment Outcomes",
                        value=DashboardState.employment_outcomes,
                        points=DashboardState.employment_outcomes_points,
                        max_points=5,
                        on_change=DashboardState.set_employment_outcomes,
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
                        label="Employability Evidence (Survey Data, Testimonials)",
                        upload_id="upload_employability",
                        handle_upload_event=DashboardState.handle_employability_upload,
                        uploaded_files=DashboardState.uploaded_employability_files,
                        is_uploading=DashboardState.is_uploading_employability,
                        delete_event=DashboardState.delete_employability_file,
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
                    numeric_input_metric(
                        label="International Research Network",
                        value=DashboardState.international_research_network,
                        points=DashboardState.international_research_network_points,
                        max_points=5,
                        on_change=DashboardState.set_international_research_network,
                    ),
                    numeric_input_metric(
                        label="International Faculty Ratio",
                        value=DashboardState.international_faculty_ratio,
                        points=DashboardState.international_faculty_ratio_points,
                        max_points=5,
                        on_change=DashboardState.set_international_faculty_ratio,
                    ),
                    numeric_input_metric(
                        label="International Student Ratio",
                        value=DashboardState.international_student_ratio,
                        points=DashboardState.international_student_ratio_points,
                        max_points=5,
                        on_change=DashboardState.set_international_student_ratio,
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
                        label="Global Engagement Evidence (Partnerships, Agreements)",
                        upload_id="upload_global_engagement",
                        handle_upload_event=DashboardState.handle_global_engagement_upload,
                        uploaded_files=DashboardState.uploaded_global_engagement_files,
                        is_uploading=DashboardState.is_uploading_global_engagement,
                        delete_event=DashboardState.delete_global_engagement_file,
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
                    numeric_input_metric(
                        label="Faculty-Student Ratio",
                        value=DashboardState.faculty_student_ratio,
                        points=DashboardState.faculty_student_ratio_points,
                        max_points=10,
                        on_change=DashboardState.set_faculty_student_ratio,
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
                        label="Learning Experience Evidence (Class Size Reports, Faculty Data)",
                        upload_id="upload_learning_experience",
                        handle_upload_event=DashboardState.handle_learning_experience_upload,
                        uploaded_files=DashboardState.uploaded_learning_experience_files,
                        is_uploading=DashboardState.is_uploading_learning_experience,
                        delete_event=DashboardState.delete_learning_experience_file,
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
                    numeric_input_metric(
                        label="Sustainability Metrics Score",
                        value=DashboardState.sustainability_metrics,
                        points=DashboardState.sustainability_metrics_points,
                        max_points=5,
                        on_change=DashboardState.set_sustainability_metrics,
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
                        label="Sustainability Evidence (ESG Reports, Environmental Certifications)",
                        upload_id="upload_sustainability",
                        handle_upload_event=DashboardState.handle_sustainability_upload,
                        uploaded_files=DashboardState.uploaded_sustainability_files,
                        is_uploading=DashboardState.is_uploading_sustainability,
                        delete_event=DashboardState.delete_sustainability_file,
                    ),
                    class_name="p-5 bg-gray-50 rounded-2xl border border-gray-100 shadow-sm",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start",
            ),
            class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
        ),
    )


def dashboard_stat_cards() -> rx.Component:
    """Row of summary cards for the assessment top-view using DS tokens."""
    from app.components.design_system import ds_stat_card
    from app.states.historical_state import HistoricalState

    return rx.el.div(
        ds_stat_card(
            title="Completion Rate",
            value=f"{DashboardState.progress}%",
            icon="circle_check",
            color_variant="success",
        ),
        ds_stat_card(
            title="Evidence Files",
            value=DashboardState.uploaded_research_files.length()
            + DashboardState.uploaded_employability_files.length()
            + DashboardState.uploaded_global_engagement_files.length()
            + DashboardState.uploaded_learning_experience_files.length()
            + DashboardState.uploaded_sustainability_files.length(),
            icon="file-check-2",
            color_variant="primary",
        ),
        rx.cond(
            HistoricalState.years_count > 0,
            ds_stat_card(
                title="Historical Data",
                value=f"{HistoricalState.years_count} Years",
                icon="history",
                color_variant="warning",
            ),
        ),
        class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10",
    )


def initial_assessment_modal() -> rx.Component:
    """Modal asking the primary question before data entry."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("moon", class_name="h-12 w-12 text-blue-600 mb-4"),
                rx.el.h2(
                    "Assessment Entry Context",
                    class_name="text-2xl font-bold text-gray-900 mb-4",
                ),
                rx.el.p(
                    "Has your institution conducted a formal assessment of QS 2025 metrics in the last 6 months?",
                    class_name="text-gray-600 mb-8",
                ),
                rx.el.div(
                    rx.el.button(
                        "Yes, I have assessed scores",
                        on_click=lambda: DashboardState.set_formal_path(True),
                        class_name="w-full py-3 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 transition-all mb-3",
                    ),
                    rx.el.button(
                        "No, start fresh assessment",
                        on_click=lambda: DashboardState.set_formal_path(False),
                        class_name="w-full py-3 bg-white border border-gray-200 text-gray-600 rounded-xl font-bold hover:bg-gray-50 transition-all",
                    ),
                    class_name="flex flex-col w-full",
                ),
                class_name="bg-white p-10 rounded-[2.5rem] shadow-2xl max-w-md w-full text-center",
            ),
            class_name="fixed inset-0 z-[200] flex items-center justify-center bg-gray-900/60 backdrop-blur-md px-4",
        ),
        class_name=rx.cond(DashboardState.show_initial_question, "block", "hidden"),
    )


def formal_assessment_form() -> rx.Component:
    """Streamlined form for users with pre-calculated aggregate scores."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Pre-Assessed Score Entry",
                        class_name="text-xl font-bold text-gray-900",
                    ),
                    rx.el.p(
                        "Input your aggregate scores and upload evidence from your formal institutional assessment.",
                        class_name="text-sm text-gray-500 mt-1",
                    ),
                ),
                rx.el.div(
                    rx.el.p(
                        "Total Weighted Score",
                        class_name="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1",
                    ),
                    rx.el.p(
                        f"{DashboardState.formal_total_weighted_score} / 100",
                        class_name="text-3xl font-black text-blue-600",
                    ),
                    class_name="bg-blue-50 px-6 py-4 rounded-2xl border border-blue-100 text-right",
                ),
                class_name="flex items-center justify-between mb-8",
            )
        ),
        rx.el.div(
            rx.el.div(
                numeric_input_metric(
                    "Research & Discovery (50%)",
                    DashboardState.formal_research_score,
                    rx.Var.create(DashboardState.formal_research_score.to(float) * 0.5),
                    50,
                    DashboardState.set_formal_research_score,
                ),
                file_upload_section(
                    "Research Evidence",
                    "upload_formal_research",
                    DashboardState.handle_formal_research_upload,
                    DashboardState.uploaded_formal_research_files,
                    DashboardState.is_uploading_formal_research,
                    DashboardState.delete_formal_research_file,
                ),
                class_name="space-y-4",
            ),
            rx.el.div(
                numeric_input_metric(
                    "Employability & Outcomes (20%)",
                    DashboardState.formal_employability_score,
                    rx.Var.create(
                        DashboardState.formal_employability_score.to(float) * 0.2
                    ),
                    20,
                    DashboardState.set_formal_employability_score,
                ),
                file_upload_section(
                    "Employability Evidence",
                    "upload_formal_employability",
                    DashboardState.handle_formal_employability_upload,
                    DashboardState.uploaded_formal_employability_files,
                    DashboardState.is_uploading_formal_employability,
                    DashboardState.delete_formal_employability_file,
                ),
                class_name="space-y-4",
            ),
            rx.el.div(
                numeric_input_metric(
                    "Global Engagement (15%)",
                    DashboardState.formal_global_engagement_score,
                    rx.Var.create(
                        DashboardState.formal_global_engagement_score.to(float) * 0.15
                    ),
                    15,
                    DashboardState.set_formal_global_engagement_score,
                ),
                file_upload_section(
                    "Global Engagement Evidence",
                    "upload_formal_global",
                    DashboardState.handle_formal_global_upload,
                    DashboardState.uploaded_formal_global_files,
                    DashboardState.is_uploading_formal_global,
                    DashboardState.delete_formal_global_file,
                ),
                class_name="space-y-4",
            ),
            rx.el.div(
                numeric_input_metric(
                    "Learning Experience (10%)",
                    DashboardState.formal_learning_experience_score,
                    rx.Var.create(
                        DashboardState.formal_learning_experience_score.to(float) * 0.1
                    ),
                    10,
                    DashboardState.set_formal_learning_experience_score,
                ),
                file_upload_section(
                    "Learning Experience Evidence",
                    "upload_formal_learning",
                    DashboardState.handle_formal_learning_upload,
                    DashboardState.uploaded_formal_learning_files,
                    DashboardState.is_uploading_formal_learning,
                    DashboardState.delete_formal_learning_file,
                ),
                class_name="space-y-4",
            ),
            rx.el.div(
                numeric_input_metric(
                    "Sustainability (5%)",
                    DashboardState.formal_sustainability_score,
                    rx.Var.create(
                        DashboardState.formal_sustainability_score.to(float) * 0.05
                    ),
                    5,
                    DashboardState.set_formal_sustainability_score,
                ),
                file_upload_section(
                    "Sustainability Evidence",
                    "upload_formal_sustainability",
                    DashboardState.handle_formal_sustainability_upload,
                    DashboardState.uploaded_formal_sustainability_files,
                    DashboardState.is_uploading_formal_sustainability,
                    DashboardState.delete_formal_sustainability_file,
                ),
                class_name="space-y-4",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-8 items-start",
        ),
        class_name="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm",
    )


def dashboard_content() -> rx.Component:
    """Aggregated assessment content view with improved spacing and dual-path logic."""
    return rx.el.div(
        initial_assessment_modal(),
        dashboard_header(),
        dashboard_stat_cards(),
        rx.cond(
            DashboardState.has_formal_assessment,
            formal_assessment_form(),
            data_entry_forms(),
        ),
        bottom_action_bar(),
        class_name="max-w-7xl mx-auto pb-12 px-4",
    )