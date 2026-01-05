import reflex as rx
from app.states.auth_state import AuthState


def sidebar_item(
    label: str, icon_name: str, href: str, is_active: bool = False
) -> rx.Component:
    """Reusable sidebar navigation item."""
    return rx.el.a(
        rx.icon(
            icon_name,
            class_name=rx.cond(
                is_active, "h-5 w-5 text-blue-600 mr-3", "h-5 w-5 text-gray-400 mr-3"
            ),
        ),
        rx.el.span(label, class_name="font-medium"),
        href=href,
        class_name=rx.cond(
            is_active,
            "flex items-center px-4 py-3 bg-blue-50 text-blue-700 rounded-lg transition-colors",
            "flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-lg transition-colors",
        ),
    )


def sidebar(current_page: str) -> rx.Component:
    """Main application sidebar."""
    return rx.el.aside(
        rx.el.div(
            rx.image(
                src="/IRRDSytemLogo.png",
                class_name="h-15 w-15 object-contain mr-3",
                alt="CHED Logo",
            ),
            class_name="flex items-center h-16 px-6 border-b border-gray-200 shrink-0",
        ),
        rx.el.nav(
            sidebar_item(
                "Dashboard",
                "layout-dashboard",
                "/dashboard",
                is_active=current_page == "dashboard",
            ),
            sidebar_item(
                "Analytics",
                "bar-chart-3",
                "/analytics",
                is_active=current_page == "analytics",
            ),
            sidebar_item(
                "Institutions",
                "building-2",
                "/institutions",
                is_active=current_page == "institutions",
            ),
            sidebar_item(
                "Reports", "file-text", "/reports", is_active=current_page == "reports"
            ),
            sidebar_item(
                "Settings",
                "settings",
                "/settings",
                is_active=current_page == "settings",
            ),
            class_name="p-4 space-y-1 flex-1 overflow-y-auto",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("user", class_name="h-4 w-4"),
                    class_name="h-9 w-9 rounded-full bg-blue-100 flex items-center justify-center text-blue-600",
                ),
                rx.el.div(
                    rx.el.p(
                        "Admin User", class_name="text-sm font-medium text-gray-900"
                    ),
                    rx.el.p("admin@ched.gov.ph", class_name="text-xs text-gray-500"),
                    class_name="ml-3 overflow-hidden flex-1",
                ),
                rx.el.button(
                    rx.icon(
                        "log-out",
                        class_name="h-5 w-5 text-gray-400 group-hover:text-red-600 transition-colors",
                    ),
                    on_click=AuthState.logout,
                    class_name="p-2 hover:bg-red-50 rounded-lg transition-colors group",
                    title="Sign Out",
                ),
                class_name="flex items-center p-4 border-t border-gray-200",
            ),
            class_name="mt-auto shrink-0",
        ),
        class_name="w-64 bg-white border-r border-gray-200 h-screen sticky top-0 flex flex-col hidden md:flex shrink-0",
    )