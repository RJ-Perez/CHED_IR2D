import reflex as rx
from app.states.auth_state import AuthState


def sidebar_item(
    label: str, icon_name: str, href: str, is_active: bool = False
) -> rx.Component:
    """Reusable sidebar navigation item with dark theme support."""
    return rx.el.a(
        rx.icon(
            icon_name,
            class_name=rx.cond(
                is_active, "h-5 w-5 text-blue-400 mr-3", "h-5 w-5 text-blue-200/60 mr-3"
            ),
        ),
        rx.el.span(label, class_name="font-medium"),
        href=href,
        class_name=rx.cond(
            is_active,
            "flex items-center px-4 py-3 bg-white/10 text-white rounded-xl transition-all shadow-sm border border-white/10",
            "flex items-center px-4 py-3 text-blue-100/70 hover:bg-white/5 hover:text-white rounded-xl transition-all",
        ),
    )


@rx.memo
def sidebar(current_page: str) -> rx.Component:
    """Main application navigation sidebar.
    Displays links to all main modules and shows the currently logged-in user info.
    Updated to use the brand blue gradient for consistency.
    """
    return rx.el.aside(
        rx.el.div(
            rx.image(
                src="/IRRDSytemLogo.png",
                class_name="h-12 w-32 object-contain brightness-0 invert",
                alt="CHED Logo",
            ),
            class_name="flex items-center h-20 px-6 border-b border-white/10 shrink-0",
        ),
        rx.el.nav(
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
            class_name="p-4 space-y-2 flex-1 overflow-y-auto",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("user", class_name="h-5 w-5 text-blue-100"),
                    class_name="h-10 w-10 rounded-full bg-white/10 flex items-center justify-center text-white border border-white/20 shadow-inner",
                ),
                rx.el.div(
                    rx.el.p(
                        AuthState.user_display_name,
                        class_name="text-sm font-bold text-white tracking-tight",
                    ),
                    rx.el.p(
                        AuthState.user_email_address,
                        class_name="text-[10px] text-blue-200/60 font-medium truncate",
                    ),
                    class_name="ml-3 overflow-hidden flex-1",
                ),
                rx.el.button(
                    rx.icon(
                        "log-out",
                        class_name="h-4 w-4 text-blue-200/60 group-hover:text-red-400 transition-colors",
                    ),
                    on_click=AuthState.logout,
                    class_name="p-2 hover:bg-red-500/10 rounded-lg transition-colors group",
                    title="Sign Out",
                ),
                class_name="flex items-center p-5 bg-black/10 backdrop-blur-sm border-t border-white/10",
            ),
            class_name="mt-auto shrink-0",
        ),
        class_name="w-64 bg-gradient-to-br from-blue-900 to-blue-700 h-screen sticky top-0 flex flex-col hidden md:flex shrink-0 shadow-2xl",
    )