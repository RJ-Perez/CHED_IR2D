import reflex as rx
from app.components.auth_ui import auth_form
from app.states.auth_state import AuthState


def branding_section() -> rx.Component:
    """Left side branding section."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                class_name="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-10"
            ),
            rx.el.div(
                rx.el.div(
                    rx.image(
                        src="https://chedcar.com/wp-content/uploads/2020/09/Commission_on_Higher_Education_CHEd.svg_.png",
                        class_name="h-16 w-16 object-contain mb-6",
                        alt="CHED Logo",
                    ),
                    class_name="bg-white/20 w-fit p-4 rounded-2xl backdrop-blur-sm",
                ),
                rx.el.h1(
                    "CHED-NCR",
                    class_name="text-4xl lg:text-5xl font-bold text-white mb-2 tracking-tight",
                ),
                rx.el.h2(
                    "International Ranking Readiness Dashboard",
                    class_name="text-2xl lg:text-3xl font-semibold text-blue-100 mb-6 leading-tight",
                ),
                rx.el.p(
                    "Empowering Higher Education Institutions in the National Capital Region to achieve global excellence through data-driven readiness assessment and strategic tracking.",
                    class_name="text-lg text-blue-50 max-w-xl leading-relaxed",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon("bar-chart-2", class_name="h-6 w-6 text-blue-200"),
                        rx.el.span(
                            "Analytics Driven", class_name="text-white font-medium ml-2"
                        ),
                        class_name="flex items-center bg-white/10 px-4 py-2 rounded-full backdrop-blur-sm",
                    ),
                    rx.el.div(
                        rx.icon("globe", class_name="h-6 w-6 text-blue-200"),
                        rx.el.span(
                            "Global Standards", class_name="text-white font-medium ml-2"
                        ),
                        class_name="flex items-center bg-white/10 px-4 py-2 rounded-full backdrop-blur-sm",
                    ),
                    class_name="flex gap-4 mt-8",
                ),
                class_name="relative z-10 flex flex-col justify-center h-full max-w-2xl mx-auto px-8 lg:px-12",
            ),
            class_name="relative hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-900 to-blue-700 overflow-hidden",
        )
    )


def landing_page() -> rx.Component:
    return rx.el.div(
        branding_section(),
        rx.el.div(
            rx.el.div(auth_form(), class_name="w-full max-w-xl px-4"),
            class_name="flex-1 flex items-center justify-center min-h-screen bg-gray-50",
        ),
        class_name="flex min-h-screen w-full font-['Inter']",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(landing_page, route="/")
from app.components.hei_ui import selection_screen_content


def hei_selection_page() -> rx.Component:
    return rx.el.div(
        rx.el.header(
            rx.el.div(
                rx.el.div(
                    rx.image(
                        src="https://chedcar.com/wp-content/uploads/2020/09/Commission_on_Higher_Education_CHEd.svg_.png",
                        class_name="h-8 w-8 object-contain mr-3",
                        alt="CHED Logo",
                    ),
                    rx.el.h1(
                        "CHED IR²D",
                        class_name="text-xl font-bold text-gray-900 tracking-tight",
                    ),
                    class_name="flex items-center",
                ),
                rx.el.button(
                    "Sign Out",
                    class_name="text-sm font-medium text-gray-600 hover:text-gray-900",
                    on_click=AuthState.logout,
                ),
                class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between",
            ),
            class_name="bg-white border-b border-gray-200 sticky top-0 z-50",
        ),
        rx.el.div(
            selection_screen_content(), class_name="flex-1 py-12 px-4 sm:px-6 lg:px-8"
        ),
        class_name="min-h-screen bg-gray-50 font-['Inter'] flex flex-col",
    )


app.add_page(hei_selection_page, route="/hei-selection")
from app.components.sidebar import sidebar
from app.components.dashboard_ui import dashboard_content
from app.components.placeholder_pages import institutions_content, reports_content
from app.components.settings_ui import settings_content
from app.states.settings_state import SettingsState


def dashboard_page() -> rx.Component:
    return rx.el.div(
        sidebar(current_page="dashboard"),
        rx.el.main(dashboard_content(), class_name="flex-1 p-8 overflow-y-auto h-full"),
        class_name="flex h-screen w-full bg-gray-50 font-['Inter']",
    )


def institutions_page() -> rx.Component:
    return rx.el.div(
        sidebar(current_page="institutions"),
        rx.el.main(
            institutions_content(), class_name="flex-1 p-8 overflow-y-auto h-full"
        ),
        class_name="flex h-screen w-full bg-gray-50 font-['Inter']",
    )


from app.components.analytics_ui import analytics_content_ui
from app.states.analytics_state import AnalyticsState


def analytics_page() -> rx.Component:
    return rx.el.div(
        sidebar(current_page="analytics"),
        rx.el.main(
            analytics_content_ui(), class_name="flex-1 p-8 overflow-y-auto h-full"
        ),
        class_name="flex h-screen w-full bg-gray-50 font-['Inter']",
        on_mount=AnalyticsState.on_load,
    )


def reports_page() -> rx.Component:
    return rx.el.div(
        sidebar(current_page="reports"),
        rx.el.main(reports_content(), class_name="flex-1 p-8 overflow-y-auto h-full"),
        class_name="flex h-screen w-full bg-gray-50 font-['Inter']",
    )


def settings_page() -> rx.Component:
    return rx.el.div(
        sidebar(current_page="settings"),
        rx.el.main(settings_content(), class_name="flex-1 p-8 overflow-y-auto h-full"),
        class_name="flex h-screen w-full bg-gray-50 font-['Inter']",
        on_mount=SettingsState.on_load,
    )


app.add_page(dashboard_page, route="/dashboard")
app.add_page(institutions_page, route="/institutions")
app.add_page(analytics_page, route="/analytics")
app.add_page(reports_page, route="/reports")
app.add_page(settings_page, route="/settings")