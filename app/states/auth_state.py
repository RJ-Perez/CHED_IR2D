import reflex as rx
import asyncio
from reflex_google_auth import GoogleAuthState
from sqlalchemy import text
import logging
import bcrypt
import datetime


class AuthState(GoogleAuthState):
    """
    Manages the authentication flow for HEI administrators.
    Integrates with Google OAuth and standard email/password authentication.
    """

    email: str = ""
    password: str = ""
    confirm_password: str = ""
    first_name: str = ""
    last_name: str = ""
    institution_name: str = ""
    position: str = ""
    authenticated_user_id: int | None = None
    is_sign_up: bool = False
    is_loading: bool = False
    error_message: str = ""

    @rx.event
    def toggle_auth_mode(self):
        """
        Switches the UI between 'Sign In' and 'Sign Up' modes.
        Clears existing errors and form data to provide a clean state.
        """
        self.is_sign_up = not self.is_sign_up
        self.error_message = ""
        self.reset_form()

    @rx.event
    def reset_form(self):
        """Clear all form fields."""
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        self.first_name = ""
        self.last_name = ""
        self.institution_name = ""
        self.position = ""

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
    def set_first_name(self, value: str):
        self.first_name = value

    @rx.event
    def set_last_name(self, value: str):
        self.last_name = value

    @rx.event
    def set_institution_name(self, value: str):
        self.institution_name = value

    @rx.event
    def set_position(self, value: str):
        self.position = value

    @rx.event(background=True)
    async def authenticate(self):
        """Main entry point for email/password authentication.
        It handles validation, password hashing for new users, and credential verification for returning users.
        """
        async with self:
            self.is_loading = True
            self.error_message = ""
            if not self.email or not self.password:
                self.error_message = "Email and password are required."
                self.is_loading = False
                return
            if self.is_sign_up:
                if (
                    not self.first_name
                    or not self.last_name
                    or (not self.position)
                    or (not self.institution_name)
                ):
                    self.error_message = "All fields are required for sign up."
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
        async with rx.asession() as session:
            if self.is_sign_up:
                result = await session.execute(
                    text("SELECT id FROM users WHERE email = :email"),
                    {"email": self.email},
                )
                first_row = result.first()
                if first_row:
                    async with self:
                        self.error_message = (
                            "An account with this email already exists."
                        )
                        self.is_loading = False
                        return
                password_hash = bcrypt.hashpw(
                    self.password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8")
                await session.execute(
                    text("""
                    INSERT INTO users (first_name, last_name, position, institution_name, email, password_hash, auth_provider)
                    VALUES (:first_name, :last_name, :position, :institution_name, :email, :password_hash, 'email')
                    """),
                    {
                        "first_name": self.first_name,
                        "last_name": self.last_name,
                        "position": self.position,
                        "institution_name": self.institution_name,
                        "email": self.email,
                        "password_hash": password_hash,
                    },
                )
                await session.commit()
                async with self:
                    self.is_loading = False
                    self.is_sign_up = False
                    self.reset_form()
                    yield rx.toast(
                        "Account created successfully! Please sign in.", duration=3000
                    )
            else:
                result = await session.execute(
                    text(
                        "SELECT id, password_hash, first_name FROM users WHERE email = :email AND auth_provider = 'email'"
                    ),
                    {"email": self.email},
                )
                user = result.first()
                if not user or not bcrypt.checkpw(
                    self.password.encode("utf-8"), user[1].encode("utf-8")
                ):
                    async with self:
                        self.error_message = "Invalid email or password."
                        self.is_loading = False
                        return
                await session.execute(
                    text("UPDATE users SET last_login = :now WHERE id = :id"),
                    {
                        "now": datetime.datetime.now(datetime.timezone.utc),
                        "id": user[0],
                    },
                )
                await session.commit()
                async with self:
                    self.authenticated_user_id = user[0]
                    self.is_loading = False
                    yield rx.toast(f"Welcome back, {user[2]}!", duration=3000)
                    yield rx.redirect("/hei-selection")

    @rx.event(background=True)
    async def on_google_login(self):
        """Triggered after Google sign-in. Verifies user in database or creates new record."""
        async with self:
            if not self.token_is_valid:
                return
            user_email = self.tokeninfo.get("email")
            google_id = self.tokeninfo.get("sub")
            first_name = self.tokeninfo.get("given_name", "")
            last_name = self.tokeninfo.get("family_name", "")
        async with rx.asession() as asession:
            result = await asession.execute(
                text("""
                SELECT id, auth_provider 
                FROM users 
                WHERE google_id = :google_id OR email = :email
                """),
                {"google_id": google_id, "email": user_email},
            )
            user = result.first()
            now = datetime.datetime.now(datetime.timezone.utc)
            if user:
                user_id = user[0]
                await asession.execute(
                    text("""
                    UPDATE users 
                    SET google_id = :google_id, 
                        last_login = :now 
                    WHERE id = :id
                    """),
                    {"google_id": google_id, "now": now, "id": user_id},
                )
            else:
                insert_result = await asession.execute(
                    text("""
                    INSERT INTO users (
                        first_name, 
                        last_name, 
                        position, 
                        institution_name, 
                        email, 
                        google_id, 
                        auth_provider, 
                        last_login
                    )
                    VALUES (
                        :first_name, 
                        :last_name, 
                        '', 
                        '', 
                        :email, 
                        :google_id, 
                        'google', 
                        :now
                    )
                    RETURNING id
                    """),
                    {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": user_email,
                        "google_id": google_id,
                        "now": now,
                    },
                )
                new_user_row = insert_result.first()
                user_id = new_user_row[0] if new_user_row else None
            await asession.commit()
            async with self:
                if user_id:
                    self.authenticated_user_id = user_id
                    yield rx.toast(f"Logged in as {user_email}", duration=3000)
                    yield rx.redirect("/hei-selection")
                else:
                    self.error_message = "Authentication failed during database sync."
                    yield rx.toast(
                        "An error occurred. Please try again.", duration=3000
                    )

    @rx.event
    def logout(self):
        """Sign out the user and redirect to landing page."""
        super().logout()
        self.authenticated_user_id = None
        self.reset_form()
        self.is_sign_up = False
        return rx.redirect("/")