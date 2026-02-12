import reflex as rx
from app.states.historical_state import HistoricalState
from app.states.hei_state import HEIState
from app.components.design_system import DS, ds_card


def score_input_historical(
    label: str, value: rx.Var, on_change: rx.event.EventType, weight: str = ""
) -> rx.Component:
    field_key_map = {
        "Academic Reputation": "academic_reputation",
        "Citations per Faculty": "citations_per_faculty",
        "Employer Reputation": "employer_reputation",
        "Employment Outcomes": "employment_outcomes",
        "Research Network": "international_research_network",
        "Int. Faculty Ratio": "international_faculty_ratio",
        "Int. Student Ratio": "international_student_ratio",
        "Faculty-Student Ratio": "faculty_student_ratio",
        "Sustainability Score": "sustainability_metrics",
    }
    field_key = field_key_map.get(label, "")
    error_msg = HistoricalState.validation_errors[field_key]
    has_error = error_msg != ""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    label,
                    class_name="text-sm font-semibold text-blue-900 tracking-tight",
                ),
                rx.cond(
                    weight != "",
                    rx.el.span(
                        weight, class_name="text-[10px] text-blue-500 font-bold ml-2"
                    ),
                    rx.fragment(),
                ),
                class_name="flex items-baseline",
            ),
            rx.el.input(
                type="number",
                on_change=on_change,
                default_value=value.to_string(),
                class_name=rx.cond(
                    has_error,
                    "w-full mt-2 p-2 border-2 border-red-500 rounded-xl",
                    "w-full mt-2 p-2 border border-blue-100 rounded-xl",
                ),
            ),
            rx.cond(
                has_error,
                rx.el.p(error_msg, class_name="text-red-500 text-xs mt-1"),
                rx.fragment(),
            ),
            class_name="flex flex-col",
        ),
        class_name="p-4 bg-blue-50/30 rounded-2xl border border-blue-100",
    )


def year_option_selector(y: str) -> rx.Component:
    """Optimized lightweight selector for better performance."""
    comp_pct = HistoricalState.year_completion_map[y]
    is_selected = HistoricalState.selected_year == y
    return rx.el.button(
        rx.el.div(
            rx.el.div(
                rx.el.span(y, class_name="text-lg font-black tracking-tight"),
                rx.el.div(
                    rx.cond(
                        comp_pct == 100,
                        rx.icon("languages", class_name="h-4 w-4 text-blue-500"),
                        rx.cond(
                            comp_pct > 0,
                            rx.icon("clock", class_name="h-4 w-4 text-blue-500"),
                            None,
                        ),
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex items-center justify-between w-full mb-2",
            ),
            rx.el.div(
                rx.el.div(
                    class_name="bg-blue-500 h-1 rounded-full",
                    style={"width": comp_pct.to_string() + "%"},
                ),
                class_name="w-full bg-slate-100 h-1 rounded-full overflow-hidden mb-1",
            ),
            rx.el.span(
                f"{comp_pct}% Filled",
                class_name="text-[9px] font-bold text-slate-400 uppercase tracking-widest",
            ),
            class_name=rx.cond(
                is_selected,
                "bg-blue-50 border-blue-400 border-2 p-4 rounded-2xl w-full",
                "bg-white border-slate-100 border p-4 rounded-2xl hover:border-blue-200 transition-colors w-full",
            ),
        ),
        on_click=lambda: HistoricalState.select_year(y),
        class_name=rx.cond(
            is_selected,
            "w-32 shrink-0 transform scale-105 z-10 shadow-lg shadow-blue-100/50 transition-all",
            "w-32 shrink-0 hover:translate-y-[-2px] hover:shadow-sm transition-all",
        ),
    )


def guidance_callout() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("info", class_name="h-5 w-5 text-blue-600 mr-3 mt-0.5"),
            rx.el.div(
                rx.el.p(
                    "Historical data is used to establish performance benchmarks and generate year-over-year growth analytics.",
                    class_name="text-sm font-bold text-blue-900",
                ),
                rx.el.p(
                    "Ensure scores entered here match official submission records for accurate trend analysis.",
                    class_name="text-xs text-blue-700 mt-1",
                ),
            ),
            class_name="flex items-start",
        ),
        class_name="bg-blue-50 border border-blue-100 p-6 rounded-3xl mb-8 max-w-5xl mx-auto",
    )


def year_summary_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                "Overall Weighted Score",
                class_name="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1",
            ),
            rx.el.h3(
                f"{HistoricalState.selected_year_overall_score}%",
                class_name="text-4xl font-black text-blue-600",
            ),
            class_name="flex-1",
        ),
        rx.el.div(
            rx.icon(
                "target",
                class_name="h-10 w-10 text-blue-500 opacity-20 absolute right-6 top-6",
            )
        ),
        class_name="bg-white p-8 rounded-[2.5rem] border border-blue-100 shadow-sm relative overflow-hidden",
    )


def historical_trend_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Historical Performance Trend",
            class_name="text-lg font-bold text-blue-900 mb-6",
        ),
        rx.recharts.line_chart(
            rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
            rx.recharts.graphing_tooltip(),
            rx.recharts.x_axis(data_key="year"),
            rx.recharts.y_axis(domain=[0, 100]),
            rx.recharts.line(
                data_key="Average",
                stroke="#2563eb",
                stroke_width=3,
                dot=True,
                type_="monotone",
            ),
            data=HistoricalState.trend_data,
            width="100%",
            height=300,
        ),
        class_name="bg-white p-8 rounded-[2.5rem] border border-blue-100 shadow-sm mb-8",
    )


def summary_table() -> rx.Component:
    return rx.el.div(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th(
                        "Year",
                        class_name="px-6 py-3 text-left text-xs font-bold text-slate-400 uppercase",
                    ),
                    rx.el.th(
                        "Score",
                        class_name="px-6 py-3 text-left text-xs font-bold text-slate-400 uppercase",
                    ),
                    rx.el.th(
                        "Research",
                        class_name="px-6 py-3 text-left text-xs font-bold text-slate-400 uppercase",
                    ),
                    class_name="border-b border-slate-100",
                )
            ),
            rx.el.tbody(
                rx.foreach(
                    HistoricalState.trend_data,
                    lambda row: rx.el.tr(
                        rx.el.td(
                            row["year"],
                            class_name="px-6 py-4 text-sm font-bold text-slate-900",
                        ),
                        rx.el.td(
                            f"{row['Average']}%",
                            class_name="px-6 py-4 text-sm font-medium text-blue-600",
                        ),
                        rx.el.td(
                            f"{row['academic_reputation']}%",
                            class_name="px-6 py-4 text-sm text-slate-500",
                        ),
                        class_name="border-b border-slate-50 last:border-0",
                    ),
                )
            ),
            class_name="w-full",
        ),
        class_name="bg-white rounded-[2.5rem] border border-slate-100 overflow-hidden mb-8",
    )


def historical_upload_section() -> rx.Component:
    return rx.el.div(
        rx.el.label(
            "Historical Evidence (Audit Reports, Scopus Certifications)",
            class_name="block text-xs font-bold text-blue-600 uppercase tracking-widest mb-4",
        ),
        rx.upload.root(
            rx.el.div(
                rx.cond(
                    HistoricalState.is_uploading,
                    rx.el.p(
                        "Syncing files...",
                        class_name="text-blue-600 font-bold animate-pulse",
                    ),
                    rx.el.div(
                        rx.icon(
                            "cloud-upload", class_name="h-8 w-8 text-blue-400 mb-2"
                        ),
                        rx.el.p(
                            "Drag evidence files here",
                            class_name="text-sm text-slate-500 font-medium",
                        ),
                    ),
                ),
                class_name="flex flex-col items-center justify-center p-8 border-2 border-dashed border-blue-100 rounded-3xl bg-blue-50/20 hover:bg-blue-50 transition-colors cursor-pointer",
            ),
            id="historical_upload",
            multiple=True,
            on_drop=HistoricalState.handle_upload(
                rx.upload_files(upload_id="historical_upload")
            ),
        ),
        rx.el.div(
            rx.foreach(
                HistoricalState.uploaded_files,
                lambda f: rx.el.div(
                    rx.el.span(
                        f.split("/").reverse()[0],
                        class_name="text-xs font-medium text-blue-700 truncate flex-1",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-3 w-3"),
                        on_click=lambda: HistoricalState.delete_file(f),
                        class_name="ml-2 text-slate-400 hover:text-red-500",
                    ),
                    class_name="flex items-center px-3 py-1.5 bg-white border border-blue-100 rounded-lg",
                ),
            ),
            class_name="mt-4 flex flex-wrap gap-2",
        ),
        class_name="mt-8 pt-8 border-t border-blue-100",
    )


def historical_content() -> rx.Component:
    from app.states.historical_analytics_state import HistoricalAnalyticsState
    from app.components.historical_analytics_ui import historical_analytics_view
    from app.states.hei_state import HEIState

    hei_name = rx.cond(
        HEIState.is_registration_mode,
        HEIState.reg_name,
        rx.cond(
            HEIState.selected_hei,
            HEIState.selected_hei["name"],
            "Institution Not Selected",
        ),
    )
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                class_name="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-10"
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon("history", class_name="h-8 w-8 text-white"),
                            class_name="p-4 bg-white/20 rounded-[1.5rem] backdrop-blur-xl border border-white/30 mr-8 shadow-inner",
                        ),
                        rx.el.div(
                            rx.el.h1(
                                hei_name,
                                class_name="text-3xl md:text-4xl font-black text-white tracking-tighter",
                            ),
                            rx.el.div(
                                rx.el.h2(
                                    "Historical Performance Archive",
                                    class_name="text-lg font-bold text-blue-100 opacity-90",
                                ),
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.span(
                                            "Database Coverage: ",
                                            class_name="text-blue-200/80",
                                        ),
                                        rx.el.span(
                                            f"{HistoricalState.historical_coverage_pct}%",
                                            class_name="text-white font-black",
                                        ),
                                        class_name="flex items-center mr-6",
                                    ),
                                    rx.el.div(
                                        rx.el.span(
                                            "Years Audited: ",
                                            class_name="text-blue-200/80",
                                        ),
                                        rx.el.span(
                                            HistoricalState.years_count.to_string(),
                                            class_name="text-white font-black",
                                        ),
                                        class_name="flex items-center",
                                    ),
                                    class_name="flex items-center text-[10px] uppercase tracking-[0.1em] mt-2 font-bold",
                                ),
                                class_name="flex flex-col",
                            ),
                            class_name="flex-1",
                        ),
                        class_name="flex items-center",
                    ),
                    class_name="max-w-7xl mx-auto",
                ),
                class_name="relative z-10",
            ),
            class_name="relative rounded-[2.5rem] bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 shadow-2xl mb-12 p-12 overflow-hidden animate-in fade-in slide-in-from-top-4 duration-1000",
        ),
        rx.el.div(
            rx.el.button(
                "Data Entry",
                on_click=lambda: HistoricalAnalyticsState.set_active_view("entry"),
                class_name=rx.cond(
                    HistoricalAnalyticsState.active_view == "entry",
                    "px-8 py-3 bg-blue-600 text-white rounded-full font-black shadow-lg shadow-blue-100",
                    "px-8 py-3 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-full font-black",
                ),
            ),
            rx.el.button(
                "View Analytics",
                on_click=lambda: HistoricalAnalyticsState.set_active_view("analytics"),
                class_name=rx.cond(
                    HistoricalAnalyticsState.active_view == "analytics",
                    "px-8 py-3 bg-blue-600 text-white rounded-full font-black shadow-lg shadow-blue-100",
                    "px-8 py-3 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-full font-black",
                ),
            ),
            class_name="flex items-center gap-4 mb-8 max-w-5xl mx-auto",
        ),
        rx.cond(
            HistoricalAnalyticsState.active_view == "analytics",
            rx.el.div(historical_analytics_view(), class_name="max-w-5xl mx-auto"),
            rx.el.div(
                guidance_callout(),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.p(
                                    "Select Ranking Year",
                                    class_name="text-xs font-black text-blue-600 uppercase tracking-[0.2em] mb-4",
                                ),
                                rx.el.div(
                                    rx.foreach(
                                        HistoricalState.available_years,
                                        year_option_selector,
                                    ),
                                    class_name="flex flex-wrap gap-3",
                                ),
                                class_name="mb-6",
                            ),
                            class_name="bg-white p-8 rounded-[2.5rem] border border-blue-100 shadow-sm",
                        ),
                        year_summary_card(),
                        class_name="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8",
                    ),
                    rx.cond(
                        HistoricalState.years_with_data.length() > 1,
                        rx.el.div(historical_trend_chart(), summary_table()),
                    ),
                    rx.el.div(
                        rx.cond(
                            HistoricalState.is_loading,
                            rx.el.div(
                                rx.foreach(
                                    rx.Var.range(4),
                                    lambda _: rx.el.div(
                                        class_name="h-24 bg-slate-100 animate-pulse rounded-2xl"
                                    ),
                                ),
                                class_name="grid grid-cols-1 md:grid-cols-2 gap-6 p-8",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.h3(
                                            "Research & Discovery",
                                            class_name="text-lg font-bold text-blue-900",
                                        ),
                                        rx.el.span(
                                            "Weight: 50%",
                                            class_name="text-[10px] font-black text-white bg-blue-600 px-2 py-0.5 rounded-md ml-3 tracking-widest",
                                        ),
                                        class_name="flex items-center mb-4",
                                    ),
                                    rx.el.div(
                                        score_input_historical(
                                            "Academic Reputation",
                                            HistoricalState.academic_reputation,
                                            HistoricalState.set_academic_reputation,
                                            weight="30%",
                                        ),
                                        score_input_historical(
                                            "Citations per Faculty",
                                            HistoricalState.citations_per_faculty,
                                            HistoricalState.set_citations_per_faculty,
                                            weight="20%",
                                        ),
                                        class_name="grid grid-cols-1 sm:grid-cols-2 gap-4",
                                    ),
                                    class_name="mb-8",
                                ),
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.h3(
                                            "Employability & Outcomes",
                                            class_name="text-lg font-bold text-blue-900",
                                        ),
                                        rx.el.span(
                                            "Weight: 20%",
                                            class_name="text-[10px] font-black text-white bg-blue-600 px-2 py-0.5 rounded-md ml-3 tracking-widest",
                                        ),
                                        class_name="flex items-center mb-4",
                                    ),
                                    rx.el.div(
                                        score_input_historical(
                                            "Employer Reputation",
                                            HistoricalState.employer_reputation,
                                            HistoricalState.set_employer_reputation,
                                            weight="15%",
                                        ),
                                        score_input_historical(
                                            "Employment Outcomes",
                                            HistoricalState.employment_outcomes,
                                            HistoricalState.set_employment_outcomes,
                                            weight="5%",
                                        ),
                                        class_name="grid grid-cols-1 sm:grid-cols-2 gap-4",
                                    ),
                                    class_name="mb-8",
                                ),
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.h3(
                                            "Global Engagement",
                                            class_name="text-lg font-bold text-blue-900",
                                        ),
                                        rx.el.span(
                                            "Weight: 15%",
                                            class_name="text-[10px] font-black text-white bg-blue-600 px-2 py-0.5 rounded-md ml-3 tracking-widest",
                                        ),
                                        class_name="flex items-center mb-4",
                                    ),
                                    rx.el.div(
                                        score_input_historical(
                                            "Research Network",
                                            HistoricalState.international_research_network,
                                            HistoricalState.set_international_research_network,
                                            weight="5%",
                                        ),
                                        score_input_historical(
                                            "Int. Faculty Ratio",
                                            HistoricalState.international_faculty_ratio,
                                            HistoricalState.set_international_faculty_ratio,
                                            weight="5%",
                                        ),
                                        score_input_historical(
                                            "Int. Student Ratio",
                                            HistoricalState.international_student_ratio,
                                            HistoricalState.set_international_student_ratio,
                                            weight="5%",
                                        ),
                                        class_name="grid grid-cols-1 sm:grid-cols-3 gap-4",
                                    ),
                                    class_name="mb-8",
                                ),
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.h3(
                                            "Learning & Sustainability",
                                            class_name="text-lg font-bold text-blue-900",
                                        ),
                                        rx.el.span(
                                            "Weight: 15%",
                                            class_name="text-[10px] font-black text-white bg-blue-600 px-2 py-0.5 rounded-md ml-3 tracking-widest",
                                        ),
                                        class_name="flex items-center mb-4",
                                    ),
                                    rx.el.div(
                                        score_input_historical(
                                            "Faculty-Student Ratio",
                                            HistoricalState.faculty_student_ratio,
                                            HistoricalState.set_faculty_student_ratio,
                                            weight="10%",
                                        ),
                                        score_input_historical(
                                            "Sustainability Score",
                                            HistoricalState.sustainability_metrics,
                                            HistoricalState.set_sustainability_metrics,
                                            weight="5%",
                                        ),
                                        class_name="grid grid-cols-1 sm:grid-cols-2 gap-4",
                                    ),
                                ),
                                historical_upload_section(),
                                rx.el.div(
                                    rx.el.button(
                                        rx.match(
                                            HistoricalState.is_saving,
                                            (
                                                True,
                                                rx.el.div(
                                                    rx.el.div(
                                                        class_name="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"
                                                    ),
                                                    "Syncing Archive...",
                                                    class_name="flex items-center justify-center",
                                                ),
                                            ),
                                            rx.el.div(
                                                rx.icon(
                                                    "cloud-upload",
                                                    class_name="h-5 w-5 mr-3",
                                                ),
                                                "Commit Historical Data",
                                                class_name="flex items-center justify-center",
                                            ),
                                        ),
                                        on_click=HistoricalState.save_historical_scores,
                                        disabled=HistoricalState.is_saving
                                        | HistoricalState.is_loading
                                        | HistoricalState.has_validation_errors,
                                        class_name=rx.cond(
                                            HistoricalState.has_validation_errors,
                                            "w-full sm:w-80 py-4 bg-slate-200 text-slate-400 rounded-2xl font-black text-lg cursor-not-allowed mt-10 transition-all flex items-center justify-center",
                                            "w-full sm:w-80 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl font-black text-lg shadow-xl shadow-blue-100 hover:shadow-blue-200 hover:scale-[1.02] active:scale-[0.98] transition-all mt-10 border border-white/20 flex items-center justify-center",
                                        ),
                                    ),
                                    class_name="flex items-center justify-center mb-10",
                                ),
                                class_name="bg-white/60 backdrop-blur-sm p-8 rounded-3xl border border-blue-100 shadow-lg",
                            ),
                        )
                    ),
                    class_name="max-w-5xl mx-auto",
                ),
            ),
        ),
        class_name="animate-in fade-in duration-700 pb-24",
    )