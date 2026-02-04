import reflex as rx
from app.states.historical_state import HistoricalState
from app.states.hei_state import HEIState
from app.components.design_system import DS, ds_card


def score_input_historical(
    label: str, value: rx.Var, on_change: rx.event.EventType, tooltip: str = ""
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.label(
                label,
                class_name="text-xs font-bold text-amber-700 uppercase tracking-wider mb-2 block",
            ),
            rx.cond(
                tooltip != "",
                rx.el.span(
                    rx.icon("moon", class_name="h-3 w-3 text-amber-400"),
                    title=tooltip,
                    class_name="cursor-help ml-1 mb-2",
                ),
                rx.fragment(),
            ),
            class_name="flex items-center",
        ),
        rx.el.input(
            type="number",
            placeholder="0-100",
            on_change=on_change.debounce(300),
            default_value=rx.cond(value == 0, "", value.to_string()),
            class_name="w-full px-4 py-2.5 bg-amber-50/50 border border-amber-200 rounded-xl focus:ring-4 focus:ring-amber-100 focus:border-amber-500 outline-none text-center font-bold text-amber-900",
        ),
        rx.cond(
            tooltip != "",
            rx.el.p(tooltip, class_name="text-[10px] text-amber-500/70 mt-2 italic"),
            rx.fragment(),
        ),
        class_name="p-4 bg-white rounded-2xl border border-amber-100 shadow-sm",
    )


def historical_trend_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Year-on-Year Performance Trends",
            class_name="text-lg font-bold text-slate-800 mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span(class_name="w-3 h-3 rounded-full bg-amber-600 mr-2"),
                rx.el.span("Average Score", class_name="text-xs text-gray-600"),
                class_name="flex items-center mr-4",
            ),
            rx.el.div(
                rx.el.span(class_name="w-3 h-3 rounded-full bg-blue-600 mr-2"),
                rx.el.span("Academic Rep", class_name="text-xs text-gray-600"),
                class_name="flex items-center mr-4",
            ),
            rx.el.div(
                rx.el.span(class_name="w-3 h-3 rounded-full bg-emerald-600 mr-2"),
                rx.el.span("Employer Rep", class_name="text-xs text-gray-600"),
                class_name="flex items-center",
            ),
            class_name="flex items-center justify-end mb-4",
        ),
        rx.recharts.line_chart(
            rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
            rx.recharts.x_axis(data_key="year", padding={"left": 30, "right": 30}),
            rx.recharts.y_axis(domain=[0, 100]),
            rx.recharts.tooltip(
                content_style={
                    "backgroundColor": "white",
                    "borderRadius": "12px",
                    "border": "1px solid #e2e8f0",
                    "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                }
            ),
            rx.recharts.line(
                data_key="Average",
                stroke="#d97706",
                stroke_width=3,
                dot={"r": 4, "strokeWidth": 2},
                active_dot={"r": 6},
                type_="monotone",
            ),
            rx.recharts.line(
                data_key="academic_reputation",
                name="Academic Rep",
                stroke="#2563eb",
                stroke_width=2,
                stroke_dasharray="5 5",
                dot=False,
                type_="monotone",
            ),
            rx.recharts.line(
                data_key="employer_reputation",
                name="Employer Rep",
                stroke="#059669",
                stroke_width=2,
                stroke_dasharray="5 5",
                dot=False,
                type_="monotone",
            ),
            data=HistoricalState.trend_data,
            width="100%",
            height=300,
        ),
        class_name="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm mb-8",
    )


def summary_table() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Historical Data Comparison",
            class_name="text-lg font-bold text-slate-800 mb-4",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "Year",
                            class_name="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Academic Rep",
                            class_name="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Employer Rep",
                            class_name="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Sustainability",
                            class_name="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Avg Score",
                            class_name="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider",
                        ),
                    ),
                    class_name="bg-slate-50",
                ),
                rx.el.tbody(
                    rx.foreach(
                        HistoricalState.trend_data,
                        lambda row: rx.el.tr(
                            rx.el.td(
                                row["year"],
                                class_name="px-6 py-4 whitespace-nowrap text-sm font-bold text-slate-900",
                            ),
                            rx.el.td(
                                row["academic_reputation"],
                                class_name="px-6 py-4 whitespace-nowrap text-sm text-slate-600",
                            ),
                            rx.el.td(
                                row["employer_reputation"],
                                class_name="px-6 py-4 whitespace-nowrap text-sm text-slate-600",
                            ),
                            rx.el.td(
                                row["sustainability_metrics"],
                                class_name="px-6 py-4 whitespace-nowrap text-sm text-slate-600",
                            ),
                            rx.el.td(
                                rx.el.span(
                                    row["Average"],
                                    class_name="px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 text-xs font-bold",
                                ),
                                class_name="px-6 py-4 whitespace-nowrap",
                            ),
                            class_name="border-b border-slate-100 last:border-0 hover:bg-slate-50/50",
                        ),
                    ),
                    class_name="bg-white divide-y divide-slate-100",
                ),
                class_name="min-w-full divide-y divide-slate-200",
            ),
            class_name="overflow-x-auto rounded-xl border border-slate-200",
        ),
        class_name="mb-8",
    )


def historical_upload_section() -> rx.Component:
    return rx.el.div(
        rx.el.label(
            "Historical Evidence / Audit Documents",
            class_name="text-xs font-bold text-amber-700 uppercase mb-3 block",
        ),
        rx.upload.root(
            rx.el.div(
                rx.cond(
                    HistoricalState.is_uploading,
                    rx.el.div(
                        rx.el.div(
                            class_name="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-600"
                        ),
                        class_name="flex items-center justify-center p-8",
                    ),
                    rx.el.div(
                        rx.icon("history", class_name="h-8 w-8 text-amber-400 mb-2"),
                        rx.el.p(
                            "Drop historical evidence files here",
                            class_name="text-sm text-amber-700 font-medium",
                        ),
                        rx.el.p(
                            "PDF, JPG, PNG allowed",
                            class_name="text-xs text-amber-500 mt-1",
                        ),
                        class_name="flex flex-col items-center p-8",
                    ),
                ),
                class_name="border-2 border-dashed border-amber-200 rounded-2xl bg-amber-50/30 hover:bg-amber-50 transition-colors cursor-pointer",
            ),
            id="historical_upload",
            on_drop=HistoricalState.handle_upload(
                rx.upload_files(upload_id="historical_upload")
            ),
            class_name="w-full",
        ),
        rx.el.div(
            rx.foreach(
                HistoricalState.uploaded_files,
                lambda f: rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "file-check", class_name="h-4 w-4 text-emerald-500 mr-2"
                        ),
                        rx.el.span(
                            f.split("/").reverse()[0],
                            class_name="text-xs text-amber-900 truncate flex-1",
                        ),
                        class_name="flex items-center min-w-0",
                    ),
                    rx.el.button(
                        rx.icon(
                            "x", class_name="h-4 w-4 text-amber-400 hover:text-red-500"
                        ),
                        on_click=HistoricalState.delete_file(f),
                        class_name="p-1 ml-2",
                    ),
                    class_name="flex items-center justify-between p-2 bg-white border border-amber-100 rounded-lg mt-2 shadow-sm",
                ),
            ),
            class_name="mt-4",
        ),
        class_name="mt-8",
    )


def year_summary_card() -> rx.Component:
    from app.components.design_system import ds_stat_card

    return rx.el.div(
        ds_card(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "Historical Coverage",
                            class_name="text-[10px] font-bold text-amber-600 uppercase tracking-widest mb-1",
                        ),
                        rx.el.p(
                            f"{HistoricalState.historical_coverage_pct}% Complete",
                            class_name="text-lg font-black text-amber-900",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            class_name="bg-amber-500 h-2 rounded-full transition-all duration-500",
                            style={
                                "width": f"{HistoricalState.historical_coverage_pct}%"
                            },
                        ),
                        class_name="w-full bg-amber-100 rounded-full h-2",
                    ),
                    class_name="flex-1",
                ),
                rx.el.div(
                    rx.el.p(
                        "Missing Cycles",
                        class_name="text-[10px] font-bold text-amber-400 uppercase tracking-widest mt-4 mb-2",
                    ),
                    rx.cond(
                        HistoricalState.missing_years.length() > 0,
                        rx.el.div(
                            rx.foreach(
                                HistoricalState.missing_years,
                                lambda y: rx.el.span(
                                    y,
                                    class_name="px-2 py-0.5 bg-white text-amber-400 text-[10px] font-bold rounded-md border border-amber-100",
                                ),
                            ),
                            class_name="flex flex-wrap gap-1",
                        ),
                        rx.el.p(
                            "Full history captured.",
                            class_name="text-[10px] text-emerald-600 font-bold uppercase",
                        ),
                    ),
                ),
                class_name="flex flex-col",
            ),
            class_name="bg-amber-50/20 border-amber-100 h-full",
        ),
        rx.cond(
            HistoricalState.years_count > 0,
            rx.el.div(
                ds_stat_card(
                    title="Peak Performance",
                    value=HistoricalState.best_performing_year,
                    icon="award",
                    color_variant="success",
                ),
                ds_stat_card(
                    title="Life Cycle Delta",
                    value=f"{HistoricalState.overall_improvement}%",
                    icon=rx.cond(
                        HistoricalState.overall_improvement >= 0,
                        "trending-up",
                        "trending-down",
                    ),
                    color_variant=rx.cond(
                        HistoricalState.overall_improvement >= 0, "success", "error"
                    ),
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
            ),
        ),
        class_name="flex flex-col md:flex-row gap-6",
    )


def guidance_callout() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                "info", class_name="h-6 w-6 text-amber-600 mr-4 flex-shrink-0 mt-1"
            ),
            rx.el.div(
                rx.el.h4(
                    "Already have previous ranking results?",
                    class_name="text-lg font-bold text-amber-900 mb-1",
                ),
                rx.el.p(
                    "Use this module to upload your past scores from 2020-2024. Entering historical data allows the IR²D system to generate trend analysis, track improvements, and provide better AI-driven strategic advice.",
                    class_name="text-sm text-amber-800 leading-relaxed",
                ),
                rx.el.details(
                    rx.el.summary(
                        "Quick Start Guide & Instructions",
                        class_name="text-xs font-bold text-amber-700 cursor-pointer mt-4 hover:underline outline-none",
                    ),
                    rx.el.div(
                        rx.el.ul(
                            rx.el.li(
                                "1. Select a year from the dropdown that matches your existing QS or THE assessment results.",
                                class_name="mb-2",
                            ),
                            rx.el.li(
                                "2. Input the numerical scores (0-100) for each metric found in your past audit reports.",
                                class_name="mb-2",
                            ),
                            rx.el.li(
                                "3. Upload PDFs or images of your official certificates or audit summaries as evidence.",
                                class_name="mb-2",
                            ),
                            rx.el.li(
                                "4. Click 'Commit Historical Data' to save and move to the next incomplete year.",
                                class_name="mb-2",
                            ),
                            class_name="text-xs text-amber-700 mt-3 list-decimal pl-4",
                        ),
                        class_name="p-4 bg-white/50 rounded-xl mt-2 border border-amber-200/50",
                    ),
                    class_name="mt-2",
                ),
            ),
            class_name="flex items-start",
        ),
        class_name="bg-amber-50 border border-amber-200 rounded-[2rem] p-8 mb-10 shadow-sm",
    )


def year_option_selector(y: str) -> rx.Component:
    has_data = HistoricalState.years_with_data.contains(y)
    is_selected = HistoricalState.selected_year == y
    is_first_incomplete = HistoricalState.first_incomplete_year == y
    return rx.el.button(
        rx.el.div(
            rx.el.div(
                rx.cond(
                    has_data,
                    rx.icon(
                        "lamp_wall_down", class_name="h-4 w-4 text-emerald-500 mr-2"
                    ),
                    rx.cond(
                        is_first_incomplete,
                        rx.el.span(
                            "START HERE",
                            class_name="text-[8px] font-black bg-blue-600 text-white px-1.5 py-0.5 rounded mr-2",
                        ),
                        rx.fragment(),
                    ),
                ),
                rx.el.span(y, class_name="font-bold"),
                class_name="flex items-center",
            ),
            class_name=rx.cond(
                is_selected,
                "bg-amber-100 text-amber-900 border-amber-300",
                rx.cond(
                    has_data,
                    "bg-emerald-50 text-emerald-700 border-emerald-100",
                    "bg-white text-slate-400 border-slate-200",
                ),
            ),
        ),
        on_click=lambda: HistoricalState.set_selected_year(y),
        class_name=rx.cond(
            is_selected,
            "px-6 py-3 rounded-2xl border-2 shadow-md scale-105 transition-all outline-none",
            "px-6 py-3 rounded-2xl border hover:border-amber-200 hover:bg-amber-50/30 transition-all outline-none",
        ),
    )


def historical_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("history", class_name="h-8 w-8 text-white"),
                    class_name="p-3 bg-white/20 rounded-2xl backdrop-blur-md border border-white/30 mr-6",
                ),
                rx.el.div(
                    rx.el.h1(
                        "Historical Ranking Entry",
                        class_name="text-3xl font-extrabold text-white tracking-tight",
                    ),
                    rx.el.p(
                        "Capture and audit past institutional scores for year-on-year growth analysis.",
                        class_name="text-amber-50 text-sm mt-1 font-medium",
                    ),
                    class_name="flex-1",
                ),
                class_name="flex items-center",
            ),
            class_name="relative rounded-3xl bg-gradient-to-r from-amber-700 via-amber-600 to-orange-700 shadow-xl mb-10 p-10",
        ),
        guidance_callout(),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "Select Ranking Year",
                            class_name="text-xs font-black text-amber-600 uppercase tracking-[0.2em] mb-4",
                        ),
                        rx.el.div(
                            rx.foreach(
                                HistoricalState.available_years, year_option_selector
                            ),
                            class_name="flex flex-wrap gap-3",
                        ),
                        class_name="mb-6",
                    ),
                    class_name="bg-white p-8 rounded-[2.5rem] border border-amber-100 shadow-sm",
                ),
                year_summary_card(),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8",
            ),
            rx.cond(
                HistoricalState.years_with_data.length() > 1,
                rx.el.div(historical_trend_chart(), summary_table()),
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Research & Discovery",
                        class_name="text-lg font-bold text-amber-900 mb-4 flex items-center",
                    ),
                    rx.el.div(
                        score_input_historical(
                            "Academic Reputation",
                            HistoricalState.academic_reputation,
                            HistoricalState.set_academic_reputation,
                            tooltip="Reputation score based on QS Academic Survey results.",
                        ),
                        score_input_historical(
                            "Citations per Faculty",
                            HistoricalState.citations_per_faculty,
                            HistoricalState.set_citations_per_faculty,
                            tooltip="Normalized number of citations for the 5-year period.",
                        ),
                        class_name="grid grid-cols-1 sm:grid-cols-2 gap-4",
                    ),
                    class_name="mb-8",
                ),
                rx.el.div(
                    rx.el.h3(
                        "Employability & Outcomes",
                        class_name="text-lg font-bold text-amber-900 mb-4",
                    ),
                    rx.el.div(
                        score_input_historical(
                            "Employer Reputation",
                            HistoricalState.employer_reputation,
                            HistoricalState.set_employer_reputation,
                            tooltip="Reputation score based on QS Employer Survey results.",
                        ),
                        score_input_historical(
                            "Employment Outcomes",
                            HistoricalState.employment_outcomes,
                            HistoricalState.set_employment_outcomes,
                            tooltip="Scores derived from graduate employment rates.",
                        ),
                        class_name="grid grid-cols-1 sm:grid-cols-2 gap-4",
                    ),
                    class_name="mb-8",
                ),
                rx.el.div(
                    rx.el.h3(
                        "Global Engagement",
                        class_name="text-lg font-bold text-amber-900 mb-4",
                    ),
                    rx.el.div(
                        score_input_historical(
                            "Research Network",
                            HistoricalState.international_research_network,
                            HistoricalState.set_international_research_network,
                            tooltip="Number of unique international partners in collaborative research.",
                        ),
                        score_input_historical(
                            "Int. Faculty Ratio",
                            HistoricalState.international_faculty_ratio,
                            HistoricalState.set_international_faculty_ratio,
                            tooltip="Percentage of faculty members from foreign countries.",
                        ),
                        score_input_historical(
                            "Int. Student Ratio",
                            HistoricalState.international_student_ratio,
                            HistoricalState.set_international_student_ratio,
                            tooltip="Percentage of students from foreign countries.",
                        ),
                        class_name="grid grid-cols-1 sm:grid-cols-3 gap-4",
                    ),
                    class_name="mb-8",
                ),
                rx.el.div(
                    rx.el.h3(
                        "Learning & Sustainability",
                        class_name="text-lg font-bold text-amber-900 mb-4",
                    ),
                    rx.el.div(
                        score_input_historical(
                            "Faculty-Student Ratio",
                            HistoricalState.faculty_student_ratio,
                            HistoricalState.set_faculty_student_ratio,
                            tooltip="Number of students per one faculty member.",
                        ),
                        score_input_historical(
                            "Sustainability Score",
                            HistoricalState.sustainability_metrics,
                            HistoricalState.set_sustainability_metrics,
                            tooltip="Overall ESG performance score from previous audits.",
                        ),
                        class_name="grid grid-cols-1 sm:grid-cols-2 gap-4",
                    ),
                ),
                historical_upload_section(),
                rx.el.div(
                    rx.el.button(
                        rx.cond(
                            HistoricalState.is_saving,
                            rx.el.div(
                                rx.el.div(
                                    class_name="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"
                                ),
                                "Storing Archives...",
                                class_name="flex items-center",
                            ),
                            rx.el.div(
                                rx.icon("save", class_name="h-5 w-5 mr-3"),
                                "Commit Historical Data",
                                class_name="flex items-center",
                            ),
                        ),
                        on_click=HistoricalState.save_historical_scores,
                        disabled=HistoricalState.is_saving | HistoricalState.is_loading,
                        class_name="w-full py-4 bg-gradient-to-r from-amber-600 to-orange-600 text-white rounded-2xl font-black text-lg shadow-xl hover:shadow-amber-100 hover:scale-[1.01] active:scale-[0.99] transition-all mt-10",
                    )
                ),
                class_name="bg-white/60 backdrop-blur-sm p-8 rounded-3xl border border-amber-100 shadow-lg",
            ),
            class_name="max-w-5xl mx-auto",
        ),
        class_name="animate-in fade-in duration-700",
    )