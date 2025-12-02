import reflex as rx


def placeholder_empty_state(title: str, description: str, icon: str) -> rx.Component:
    """Reusable empty state component for placeholder pages."""
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-12 w-12 text-gray-300 mb-4"),
            rx.el.h2(title, class_name="text-xl font-semibold text-gray-900 mb-2"),
            rx.el.p(description, class_name="text-gray-500 text-center max-w-sm"),
            class_name="flex flex-col items-center justify-center py-16 px-4 bg-white rounded-xl border border-gray-200 shadow-sm h-96",
        ),
        class_name="max-w-4xl mx-auto",
    )


def simple_header(title: str, subtitle: str) -> rx.Component:
    """Standard header for placeholder pages."""
    return rx.el.div(
        rx.el.h1(title, class_name="text-2xl font-bold text-gray-900"),
        rx.el.p(subtitle, class_name="text-gray-600 mt-1"),
        class_name="mb-8",
    )


from app.components.institutions_ui import institutions_dashboard_ui
from app.components.reports_ui import reports_dashboard_ui


def institutions_content() -> rx.Component:
    return institutions_dashboard_ui()


def reports_content() -> rx.Component:
    return reports_dashboard_ui()


def settings_content() -> rx.Component:
    return rx.el.div(
        simple_header("Settings", "Account and system preferences"),
        placeholder_empty_state(
            "Settings Unavailable",
            "System configurations are currently locked by the administrator. Please contact support for changes.",
            "settings",
        ),
        class_name="max-w-6xl mx-auto",
    )