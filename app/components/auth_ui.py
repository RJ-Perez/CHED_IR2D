import reflex as rx
import os
from app.states.auth_state import AuthState
from reflex_google_auth import google_login, google_oauth_provider, set_client_id
from app.components.design_system import ds_card, ds_input, ds_button

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
set_client_id(GOOGLE_CLIENT_ID)


def auth_form() -> rx.Component:
    """Main Authentication Form Component using Design System for UI consistency."""
    return rx.el.div(
        rx.cond(
            AuthState.is_loading | AuthState.is_redirecting,
            rx.el.div(
                rx.el.div(
                    class_name="h-full w-full bg-gradient-to-r from-blue-600 via-indigo-500 to-blue-600 animate-slide-progress"
                ),
                class_name="absolute top-0 left-0 w-full h-1 overflow-hidden rounded-t-2xl z-[60]",
            ),
        ),
        rx.cond(
            AuthState.is_redirecting,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            class_name="h-3 w-3 bg-blue-600 rounded-full animate-pulse-dot"
                        ),
                        rx.el.div(
                            class_name="h-3 w-3 bg-blue-600 rounded-full animate-pulse-dot delay-200"
                        ),
                        rx.el.div(
                            class_name="h-3 w-3 bg-blue-600 rounded-full animate-pulse-dot delay-400"
                        ),
                        class_name="flex items-center justify-center gap-2 mb-6",
                    ),
                    rx.el.h3(
                        "Authentication Successful",
                        class_name="text-xl font-bold text-gray-900 mb-2",
                    ),
                    rx.el.p(
                        "Redirecting to institutional selection...",
                        class_name="text-gray-600 animate-pulse",
                    ),
                    class_name="text-center",
                ),
                class_name="fixed inset-0 bg-white/90 backdrop-blur-md z-[100] flex items-center justify-center animate-in fade-in duration-300",
            ),
        ),
        ds_card(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.image(
                            src="https://chedcar.com/wp-content/uploads/2020/09/Commission_on_Higher_Education_CHEd.svg_.png",
                            class_name="h-12 w-12 object-contain",
                        ),
                        class_name="bg-white rounded-lg p-1.5 shadow-sm mx-auto mb-4 w-fit border border-gray-100",
                    ),
                    rx.el.h2(
                        rx.cond(
                            AuthState.is_sign_up, "Create Admin Account", "Sign In"
                        ),
                        class_name="text-2xl font-bold text-center text-gray-900",
                    ),
                    rx.el.p(
                        "CHED IR²D Strategic Management Portal",
                        class_name="text-center text-sm text-gray-500 mb-8",
                    ),
                    class_name="mb-6",
                ),
                rx.el.div(
                    rx.cond(
                        AuthState.is_sign_up,
                        rx.el.div(
                            rx.el.div(
                                ds_input(
                                    label="First Name",
                                    placeholder="First Name",
                                    value=AuthState.first_name,
                                    on_change=AuthState.set_first_name,
                                ),
                                ds_input(
                                    label="Last Name",
                                    placeholder="Last Name",
                                    value=AuthState.last_name,
                                    on_change=AuthState.set_last_name,
                                ),
                                class_name="grid grid-cols-2 gap-4",
                            ),
                            ds_input(
                                label="Institution Name",
                                placeholder="Full Institution Name",
                                value=AuthState.institution_name,
                                on_change=AuthState.set_institution_name,
                            ),
                            ds_input(
                                label="Current Position",
                                placeholder="e.g. Quality Assurance Director",
                                value=AuthState.position,
                                on_change=AuthState.set_position,
                            ),
                            class_name="space-y-4 mb-4",
                        ),
                    ),
                    ds_input(
                        label="Email Address",
                        type="email",
                        placeholder="name@institution.edu.ph",
                        value=AuthState.email,
                        on_change=AuthState.set_email,
                        icon="mail",
                    ),
                    ds_input(
                        label="Password",
                        type="password",
                        placeholder="••••••••",
                        value=AuthState.password,
                        on_change=AuthState.set_password,
                        icon="lock",
                    ),
                    rx.cond(
                        AuthState.is_sign_up,
                        ds_input(
                            label="Confirm Password",
                            type="password",
                            placeholder="••••••••",
                            value=AuthState.confirm_password,
                            on_change=AuthState.set_confirm_password,
                            icon="check-circle",
                        ),
                    ),
                    rx.cond(
                        AuthState.error_message != "",
                        rx.el.div(
                            rx.icon("wheat", class_name="h-4 w-4 mr-2"),
                            rx.el.span(AuthState.error_message),
                            class_name="p-3 bg-red-50 text-red-600 rounded-xl text-xs font-semibold flex items-center mb-4",
                        ),
                    ),
                    ds_button(
                        label=rx.cond(
                            AuthState.is_sign_up, "Create Account", "Sign In"
                        ),
                        on_click=AuthState.authenticate,
                        loading=AuthState.is_loading,
                        icon="",
                        class_name="w-full mt-6",
                    ),
                    class_name="space-y-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(class_name="w-full border-t border-gray-200"),
                            class_name="absolute inset-0 flex items-center",
                        ),
                        rx.el.div(
                            rx.el.span(
                                "Or continue with",
                                class_name="bg-white px-2 text-gray-500 font-bold tracking-widest",
                            ),
                            class_name="relative flex justify-center text-xs uppercase",
                        ),
                        class_name="relative",
                    ),
                    class_name="my-8",
                ),
                rx.el.div(
                    google_oauth_provider(
                        google_login(on_success=AuthState.on_google_login),
                        client_id=GOOGLE_CLIENT_ID,
                    ),
                    class_name="flex justify-center",
                ),
                rx.el.div(
                    rx.el.p(
                        rx.cond(
                            AuthState.is_sign_up,
                            "Already have an account? ",
                            "Need an institutional account? ",
                        ),
                        rx.el.button(
                            rx.cond(AuthState.is_sign_up, "Sign In", "Create one here"),
                            on_click=AuthState.toggle_auth_mode,
                            class_name="text-blue-600 font-bold hover:underline",
                        ),
                        class_name="text-center text-sm text-gray-500 mt-8",
                    )
                ),
                class_name="w-full",
            ),
            padding="p-8",
            class_name="max-w-md mx-auto w-full",
        ),
        forgot_password_modal(),
        class_name="relative w-full",
    )


def forgot_password_modal() -> rx.Component:
    """Modal for requesting a password reset."""
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 bg-black/50 z-[100] animate-in fade-in duration-200"
            ),
            rx.radix.primitives.dialog.content(
                rx.el.div(
                    rx.el.h3(
                        "Reset Password",
                        class_name="text-lg font-bold text-gray-900 mb-2",
                    ),
                    rx.cond(
                        AuthState.reset_success,
                        rx.el.div(
                            rx.icon(
                                "mail-check",
                                class_name="h-12 w-12 text-green-500 mx-auto mb-4",
                            ),
                            rx.el.p(
                                "Check your email for a reset link. The link will expire in 1 hour.",
                                class_name="text-center text-gray-600 mb-6",
                            ),
                            rx.el.button(
                                "Close",
                                on_click=AuthState.toggle_forgot_password,
                                class_name="w-full py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-bold transition-colors",
                            ),
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Enter your email address and we'll send you a link to reset your password.",
                                class_name="text-sm text-gray-500 mb-4",
                            ),
                            ds_input(
                                label="Email Address",
                                type="email",
                                placeholder="name@institution.edu.ph",
                                value=AuthState.forgot_password_email,
                                on_change=AuthState.set_forgot_password_email,
                                icon="mail",
                            ),
                            rx.cond(
                                AuthState.error_message != "",
                                rx.el.div(
                                    rx.icon("circle-alert", class_name="h-4 w-4 mr-2"),
                                    rx.el.span(AuthState.error_message),
                                    class_name="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-xs font-semibold flex items-center",
                                ),
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "Cancel",
                                    on_click=AuthState.toggle_forgot_password,
                                    class_name="px-4 py-2 text-sm font-bold text-gray-500 hover:text-gray-700 transition-colors",
                                ),
                                ds_button(
                                    label="Send Reset Link",
                                    on_click=AuthState.request_password_reset,
                                    loading=AuthState.is_sending_reset,
                                    class_name="ml-2",
                                ),
                                class_name="flex justify-end items-center mt-6",
                            ),
                        ),
                    ),
                    class_name="bg-white p-6 rounded-2xl shadow-xl w-full max-w-sm",
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-[101] outline-none",
            ),
        ),
        open=AuthState.show_forgot_password,
        on_open_change=AuthState.toggle_forgot_password,
    )