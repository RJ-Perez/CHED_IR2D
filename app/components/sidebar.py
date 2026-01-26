import reflex as rx
from app.states.auth_state import AuthState


def sidebar_item(
    label: str, icon_name: str, href: str, is_active: bool = False
) -> rx.Component:
    """Reusable sidebar navigation item with white theme support."""
    return rx.el.a(
        rx.icon(
            icon_name,
            class_name=rx.cond(
                is_active, "h-5 w-5 text-blue-600 mr-3", "h-5 w-5 text-gray-500 mr-3"
            ),
        ),
        rx.el.span(label, class_name="font-medium"),
        href=href,
        class_name=rx.cond(
            is_active,
            "flex items-center px-4 py-3 bg-blue-50 text-blue-600 rounded-xl transition-all shadow-sm border border-blue-100",
            "flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-xl transition-all",
        ),
    )


def sidebar_section_label(label: str) -> rx.Component:
    """Subtle uppercase section label for grouping navigation items."""
    return rx.el.p(
        label,
        class_name="text-[10px] font-bold text-gray-400 uppercase tracking-[0.15em] px-4 mt-6 mb-2",
    )


@rx.memo
def sidebar(current_page: str) -> rx.Component:
    """Main application navigation sidebar.
    Displays links to all main modules and shows the currently logged-in user info.
    Updated to a clean white theme for improved accessibility.
    """
    return rx.el.aside(
        rx.el.div(
            rx.image(
                src="/IRRDSytemLogo.png",
                class_name="h-12 w-32 object-contain",
                alt="CHED Logo",
            ),
            class_name="flex items-center h-20 px-6 border-b border-gray-100 shrink-0",
        ),
        rx.el.nav(
            sidebar_section_label("HEI Modules"),
            sidebar_item(
                "Assessment",
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
            sidebar_section_label("CHED Modules"),
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
                "Insights",
                "line-chart",
                "/post-assessment",
                is_active=current_page == "post-assessment",
            ),
            sidebar_item(
                "Settings",
                "settings",
                "/settings",
                is_active=current_page == "settings",
            ),
            class_name="p-4 space-y-2 flex-1 overflow-y-auto",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("user", class_name="h-5 w-5 text-gray-600"),
                    class_name="h-10 w-10 rounded-full bg-gray-50 flex items-center justify-center text-gray-700 border border-gray-100 shadow-sm",
                ),
                rx.el.div(
                    rx.el.p(
                        AuthState.user_display_name,
                        class_name="text-sm font-bold text-gray-900 tracking-tight",
                    ),
                    rx.el.p(
                        AuthState.user_email_address,
                        class_name="text-[10px] text-gray-500 font-medium truncate",
                    ),
                    class_name="ml-3 overflow-hidden flex-1",
                ),
                rx.el.button(
                    rx.icon(
                        "log-out",
                        class_name="h-4 w-4 text-gray-400 group-hover:text-red-500 transition-colors",
                    ),
                    on_click=AuthState.logout,
                    class_name="p-2 hover:bg-red-50 rounded-lg transition-colors group",
                    title="Sign Out",
                ),
                class_name="flex items-center p-5 bg-gray-50/50 backdrop-blur-sm border-t border-gray-100",
            ),
            class_name="mt-auto shrink-0",
        ),
        class_name="w-64 bg-white border-r border-gray-200 h-screen sticky top-0 flex flex-col hidden md:flex shrink-0 shadow-sm",
    )