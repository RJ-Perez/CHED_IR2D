import reflex as rx
from app.states.auth_state import AuthState
from reflex_google_auth import google_login, google_oauth_provider


def input_field(
    label: str,
    placeholder: str,
    type_: str,
    value: str,
    on_change: rx.event.EventType,
    icon: str = "type",
) -> rx.Component:
    """Reusable input field component with label and icon."""
    return rx.el.div(
        rx.el.label(
            label, class_name="block text-sm font-semibold text-gray-700 mb-1.5"
        ),
        rx.el.div(
            rx.icon(
                icon,
                class_name="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5",
            ),
            rx.el.input(
                type=type_,
                placeholder=placeholder,
                on_change=on_change,
                class_name="w-full pl-10 pr-4 py-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none transition-all duration-200 text-gray-900 placeholder-gray-400",
                default_value=value,
            ),
            class_name="relative",
        ),
        class_name="w-full",
    )


def auth_form() -> rx.Component:
    """Main Authentication Form Component."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                rx.cond(
                    AuthState.is_sign_up,
                    "Create your account",
                    "Sign in to your account",
                ),
                class_name="text-2xl font-bold text-gray-900 tracking-tight",
            ),
            rx.el.p(
                rx.cond(
                    AuthState.is_sign_up,
                    "Get started with your HEI ranking assessment",
                    "Access your dashboard and tracking tools",
                ),
                class_name="mt-2 text-sm text-gray-600",
            ),
            class_name="mb-8 text-center",
        ),
        rx.cond(
            AuthState.error_message != "",
            rx.el.div(
                rx.icon("badge_alert", class_name="h-5 w-5 text-red-500 mr-2"),
                rx.el.span(
                    AuthState.error_message,
                    class_name="text-sm text-red-700 font-medium",
                ),
                class_name="mb-6 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center animate-in fade-in slide-in-from-top-2",
            ),
        ),
        rx.el.div(
            rx.cond(
                AuthState.is_sign_up,
                rx.el.div(
                    rx.el.div(
                        input_field(
                            "First Name",
                            "Juan",
                            "text",
                            AuthState.first_name,
                            AuthState.set_first_name,
                            "user",
                        ),
                        input_field(
                            "Last Name",
                            "Dela Cruz",
                            "text",
                            AuthState.last_name,
                            AuthState.set_last_name,
                            "user",
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
                    ),
                    input_field(
                        "Position",
                        "VP for Academic Affairs",
                        "text",
                        AuthState.position,
                        AuthState.set_position,
                        "briefcase",
                    ),
                    input_field(
                        "Institution Name",
                        "University of the Philippines",
                        "text",
                        AuthState.institution_name,
                        AuthState.set_institution_name,
                        "building-2",
                    ),
                    class_name="space-y-4 animate-in fade-in slide-in-from-top-4",
                ),
            ),
            rx.el.div(
                input_field(
                    "Email Address",
                    "admin@university.edu.ph",
                    "email",
                    AuthState.email,
                    AuthState.set_email,
                    "mail",
                ),
                class_name="mt-4",
            ),
            rx.el.div(
                input_field(
                    "Password",
                    "••••••••",
                    "password",
                    AuthState.password,
                    AuthState.set_password,
                    "lock",
                ),
                class_name="mt-4",
            ),
            rx.cond(
                AuthState.is_sign_up,
                rx.el.div(
                    input_field(
                        "Confirm Password",
                        "••••••••",
                        "password",
                        AuthState.confirm_password,
                        AuthState.set_confirm_password,
                        "lock",
                    ),
                    class_name="mt-4 animate-in fade-in slide-in-from-top-4",
                ),
            ),
            class_name="space-y-4",
        ),
        rx.cond(
            ~AuthState.is_sign_up,
            rx.el.div(
                rx.el.a(
                    "Forgot your password?",
                    href="#",
                    class_name="text-sm font-medium text-blue-600 hover:text-blue-500",
                ),
                class_name="flex justify-end mt-2",
            ),
        ),
        rx.el.button(
            rx.cond(
                AuthState.is_sign_up,
                rx.el.div(
                    rx.el.div(
                        class_name="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"
                    ),
                    "Processing...",
                    class_name="flex items-center justify-center",
                ),
                rx.cond(AuthState.is_sign_up, "Create Account", "Sign In"),
            ),
            on_click=AuthState.authenticate,
            disabled=AuthState.is_loading,
            class_name=rx.cond(
                AuthState.is_loading,
                "mt-8 w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-400 cursor-not-allowed",
                "mt-8 w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-700 hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-600 transition-colors duration-200",
            ),
        ),
        rx.el.div(
            rx.el.div(class_name="flex-1 h-px bg-gray-200"),
            rx.el.span(
                "or", class_name="px-3 text-xs text-gray-400 uppercase font-bold"
            ),
            rx.el.div(class_name="h-px flex-1 bg-gray-200"),
            class_name="flex items-center my-6",
        ),
        google_oauth_provider(
            rx.el.div(
                google_login(on_success=lambda token: AuthState.on_google_login(token)),
                class_name="w-full flex justify-center",
            )
        ),
        rx.el.div(
            rx.cond(
                AuthState.is_sign_up,
                "Already have an account? ",
                "Don't have an account? ",
            ),
            rx.el.button(
                rx.cond(AuthState.is_sign_up, "Sign in", "Sign up"),
                on_click=AuthState.toggle_auth_mode,
                class_name="font-semibold text-blue-700 hover:text-blue-500 focus:outline-none transition-colors",
            ),
            class_name="mt-6 text-center text-sm text-gray-600",
        ),
        class_name="w-full max-w-md mx-auto bg-white p-8 rounded-2xl shadow-sm border border-gray-100",
    )