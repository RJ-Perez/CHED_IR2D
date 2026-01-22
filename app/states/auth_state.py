import reflex as rx
import asyncio
import base64
import json
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

    def _decode_jwt(self, token: str) -> dict:
        """Helper to decode JWT payload safely without external dependencies."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return {}
            payload = parts[1]
            padded = payload + "=" * (4 - len(payload) % 4)
            return json.loads(base64.urlsafe_b64decode(padded))
        except Exception as e:
            logging.exception(f"JWT decoding error: {e}")
            return {}

    @rx.var(cache=True)
    async def user_display_name(self) -> str:
        """Fetches the user's full name from the database based on session ID."""
        if self.authenticated_user_id is not None:
            async with rx.asession() as session:
                result = await session.execute(
                    text("SELECT first_name, last_name FROM users WHERE id = :id"),
                    {"id": self.authenticated_user_id},
                )
                row = result.first()
                if row:
                    return f"{row[0]} {row[1]}"
        if self.token_is_valid:
            return self.tokeninfo.get("name", "Google User")
        return "Guest User"

    @rx.var(cache=True)
    async def user_email_address(self) -> str:
        """Fetches the user's email from the database or OAuth info."""
        if self.authenticated_user_id is not None:
            async with rx.asession() as session:
                result = await session.execute(
                    text("SELECT email FROM users WHERE id = :id"),
                    {"id": self.authenticated_user_id},
                )
                row = result.first()
                if row:
                    return row[0]
        if self.token_is_valid:
            return self.tokeninfo.get("email", "")
        return ""

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

    def _validate_password(self, password: str) -> str | None:
        """Standard password security validation."""
        if len(password) < 8:
            return "Password must be at least 8 characters long."
        import re

        if not re.search("[a-z]", password):
            return "Password must contain at least one lowercase letter."
        if not re.search("[A-Z]", password):
            return "Password must contain at least one uppercase letter."
        if not re.search("[0-9]", password):
            return "Password must contain at least one digit."
        if not re.search('[!@#$%^&*(),.?":{}|<>]', password):
            return "Password must contain at least one special character."
        return None

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
                password_error = self._validate_password(self.password)
                if password_error:
                    self.error_message = password_error
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
    async def on_google_login(self, token_data: dict):
        """Triggered after Google sign-in. Directly decodes JWT to avoid timeouts."""
        credential = token_data.get("credential")
        if not credential:
            async with self:
                yield rx.toast(
                    "Authentication error: No credential received from Google.",
                    duration=5000,
                    position="top-center",
                )
            return
        user_info = self._decode_jwt(credential)
        user_email = user_info.get("email")
        google_id = user_info.get("sub")
        first_name = user_info.get("given_name", "")
        last_name = user_info.get("family_name", "")
        if not user_email or not google_id:
            logging.warning("Google login failed: Incomplete JWT payload.")
            async with self:
                self.error_message = (
                    "Google login failed: Required profile info missing from token."
                )
                yield rx.toast(self.error_message, duration=5000)
            return
        user_id = None
        try:
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
                            'HEI Administrator', 
                            'Google Verified', 
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
        except Exception as e:
            logging.exception(f"Database error during Google login sync: {e}")
            async with self:
                yield rx.toast(
                    "Database synchronization failed. Please contact support.",
                    duration=5000,
                )
            return
        if user_id:
            async with self:
                self.authenticated_user_id = user_id
                self.error_message = ""
                self.id_token_json = json.dumps(token_data)
                yield rx.toast(
                    f"Successfully signed in as {first_name}!", duration=3000
                )
                yield rx.redirect("/hei-selection")
        else:
            async with self:
                self.error_message = (
                    "Authentication failed during user profile synchronization."
                )
                yield rx.toast("Could not finalize your login session.", duration=5000)

    @rx.event
    def logout(self):
        """Sign out the user and redirect to landing page."""
        super().logout()
        self.authenticated_user_id = None
        self.reset_form()
        self.is_sign_up = False
        return rx.redirect("/")