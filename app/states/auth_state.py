import reflex as rx
import asyncio


class AuthState(rx.State):
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    full_name: str = ""
    institution_name: str = ""
    is_sign_up: bool = False
    is_loading: bool = False
    error_message: str = ""

    @rx.event
    def toggle_auth_mode(self):
        """Toggle between Login and Sign Up modes."""
        self.is_sign_up = not self.is_sign_up
        self.error_message = ""
        self.reset_form()

    @rx.event
    def reset_form(self):
        """Clear all form fields."""
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        self.full_name = ""
        self.institution_name = ""

    @rx.event
    def set_email(self, value: str):
        self.email = value
        self.error_message = ""

    @rx.event
    def set_password(self, value: str):
        self.password = value
        self.error_message = ""

    @rx.event
    def set_confirm_password(self, value: str):
        self.confirm_password = value
        self.error_message = ""

    @rx.event
    def set_full_name(self, value: str):
        self.full_name = value

    @rx.event
    def set_institution_name(self, value: str):
        self.institution_name = value

    @rx.event(background=True)
    async def authenticate(self):
        """Handle form submission for both Login and Sign Up."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            if not self.email or not self.password:
                self.error_message = "Email and password are required."
                self.is_loading = False
                return
            if self.is_sign_up:
                if not self.full_name:
                    self.error_message = "Full Name is required."
                    self.is_loading = False
                    return
                if self.password != self.confirm_password:
                    self.error_message = "Passwords do not match."
                    self.is_loading = False
                    return
                if len(self.password) < 6:
                    self.error_message = "Password must be at least 6 characters."
                    self.is_loading = False
                    return
        await asyncio.sleep(1.5)
        async with self:
            self.is_loading = False
            if self.is_sign_up:
                yield rx.toast(
                    "Account created successfully! Please sign in.", duration=3000
                )
                self.is_sign_up = False
                self.reset_form()
            else:
                yield rx.toast(f"Welcome back, {self.email}!", duration=3000)
                yield rx.redirect("/hei-selection")

    @rx.event
    def google_login(self):
        """Placeholder for Google Login."""
        return rx.toast("Google Login integration coming in Phase 2", duration=3000)

    @rx.event
    def logout(self):
        """Sign out the user and redirect to landing page."""
        self.reset_form()
        self.is_sign_up = False
        return rx.redirect("/")