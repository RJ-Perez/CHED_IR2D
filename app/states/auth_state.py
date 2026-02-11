import reflex as rx
import asyncio
import base64
import json
from reflex_google_auth import GoogleAuthState
from sqlalchemy import text
import logging
import bcrypt
import datetime
import secrets
import os

try:
    import resend
    from resend.exceptions import ResendError
except ImportError:
    resend = None

    class ResendError(Exception):
        pass


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
    is_redirecting: bool = False
    error_message: str = ""
    forgot_password_email: str = ""
    show_forgot_password: bool = False
    reset_token: str = ""
    new_password: str = ""
    confirm_new_password: str = ""
    reset_success: bool = False
    reset_error_message: str = ""
    is_sending_reset: bool = False
    is_resetting_password: bool = False

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
    def toggle_forgot_password(self):
        """Toggles the forgot password modal visibility."""
        self.show_forgot_password = not self.show_forgot_password
        self.forgot_password_email = ""
        self.reset_success = False
        self.error_message = ""

    @rx.event
    def set_forgot_password_email(self, value: str):
        self.forgot_password_email = value

    @rx.event
    def set_new_password(self, value: str):
        self.new_password = value

    @rx.event
    def set_confirm_new_password(self, value: str):
        self.confirm_new_password = value

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
                    self.is_redirecting = True
                    yield rx.toast(f"Welcome back, {user[2]}!", duration=3000)
                    yield rx.redirect("/hei-selection")

    @rx.event(background=True)
    async def on_google_login(self, token_data: dict):
        """Triggered after Google sign-in. Decodes JWT and syncs user with the database.
        Includes extensive logging for debugging production OAuth failures.
        """
        credential = token_data.get("credential")
        if not credential:
            logging.error(
                f"OAuth Failure: No credential in token_data. Keys present: {list(token_data.keys())}"
            )
            async with self:
                yield rx.toast(
                    "Authentication error: Google did not return valid identity credentials.",
                    duration=5000,
                    position="top-center",
                )
            return
        user_info = self._decode_jwt(credential)
        if not user_info:
            logging.error("OAuth Failure: Decoded user_info is empty or invalid.")
            async with self:
                yield rx.toast(
                    "Authentication error: Failed to verify identity token.",
                    duration=5000,
                )
            return
        user_email = user_info.get("email")
        google_id = user_info.get("sub")
        first_name = user_info.get("given_name", "")
        last_name = user_info.get("family_name", "")
        if not user_email or not google_id:
            logging.warning(
                f"OAuth Failure: Incomplete JWT payload. Email: {bool(user_email)}, ID: {bool(google_id)}"
            )
            async with self:
                self.error_message = (
                    "Google login failed: Profile info missing from token."
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
                    logging.info(
                        f"OAuth Sync: Updating existing user ID {user_id} (email: {user_email})"
                    )
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
                    logging.info(
                        f"OAuth Sync: Registering new Google user (email: {user_email})"
                    )
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
            logging.exception(f"OAuth Failure: Database synchronization error: {e}")
            async with self:
                yield rx.toast(
                    "Security sync failed. The database could not be reached.",
                    duration=5000,
                )
            return
        if user_id:
            async with self:
                self.authenticated_user_id = user_id
                self.error_message = ""
                self.is_redirecting = True
                self.id_token_json = json.dumps(token_data)
            yield rx.toast(f"Welcome to IR²D, {first_name}!", duration=3000)
            yield rx.redirect("/hei-selection")
        else:
            logging.error(
                "OAuth Failure: Sync process finished without a valid user_id."
            )
            async with self:
                self.error_message = (
                    "Authentication failed during profile synchronization."
                )
            yield rx.toast("Final security handshake failed.", duration=5000)

    @rx.event(background=True)
    async def request_password_reset(self):
        """Generates a reset token and sends an email to the user."""
        async with self:
            self.is_sending_reset = True
            self.error_message = ""
            if not self.forgot_password_email:
                self.error_message = "Please enter your email address."
                self.is_sending_reset = False
                return
        resend_api_key = os.getenv("RESEND_API_KEY")
        if not resend_api_key:
            async with self:
                self.error_message = (
                    "Email service is not configured. Please contact support."
                )
                self.is_sending_reset = False
            return
        if resend:
            resend.api_key = resend_api_key
        async with rx.asession() as session:
            result = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": self.forgot_password_email},
            )
            user = result.first()
            if user:
                user_id = user[0]
                token = secrets.token_urlsafe(32)
                expires_at = datetime.datetime.now(
                    datetime.timezone.utc
                ) + datetime.timedelta(hours=1)
                await session.execute(
                    text("""
                    INSERT INTO password_reset_tokens (user_id, token, expires_at)
                    VALUES (:user_id, :token, :expires_at)
                    """),
                    {"user_id": user_id, "token": token, "expires_at": expires_at},
                )
                await session.commit()
                reset_link = f"{self.router.page.host}/reset-password?token={token}"
                email_html = f'''\n                <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">\n                    <h2 style="color: #1e40af;">Password Reset Request</h2>\n                    <p>We received a request to reset your password for the CHED IR²D Portal.</p>\n                    <p>Click the button below to reset it. This link will expire in 1 hour.</p>\n                    <a href="{reset_link}" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 16px 0;">Reset Password</a>\n                    <p style="color: #64748b; font-size: 14px;">If you didn't request this, you can safely ignore this email.</p>\n                    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">\n                    <p style="color: #94a3b8; font-size: 12px;">CHED IR²D Strategic Management Portal</p>\n                </div>\n                '''
                try:
                    resend.Emails.send(
                        {
                            "from": "CHED IR²D <onboarding@resend.dev>",
                            "to": self.forgot_password_email,
                            "subject": "Reset Your Password - CHED IR²D",
                            "html": email_html,
                        }
                    )
                    async with self:
                        self.reset_success = True
                except Exception as e:
                    error_str = str(e).lower()
                    error_type = type(e).__name__.lower()
                    logging.exception(f"Email delivery error: {e}")
                    async with self:
                        if (
                            "resend" in error_type
                            or "restricted to the account owner" in error_str
                            or "verify a domain" in error_str
                            or ("testing emails" in error_str)
                        ):
                            self.error_message = "The email service is currently in Test Mode or unverified. Reset links can only be sent to the registered account owner. Please contact the system administrator to verify the domain."
                        else:
                            self.error_message = "The system encountered a technical issue sending the email. Please try again later or contact support."
            else:
                async with self:
                    self.reset_success = True
        async with self:
            self.is_sending_reset = False

    @rx.event(background=True)
    async def validate_reset_token(self):
        """Validates the reset token on page load."""
        token = self.router.page.params.get("token")
        async with self:
            self.reset_token = token
            self.reset_error_message = ""
        if not token:
            async with self:
                self.reset_error_message = "Invalid or missing reset token."
            return
        async with rx.asession() as session:
            result = await session.execute(
                text("""
                SELECT id, expires_at, used 
                FROM password_reset_tokens 
                WHERE token = :token
                """),
                {"token": token},
            )
            row = result.first()
            if not row:
                async with self:
                    self.reset_error_message = "Invalid reset token."
                return
            expires_at = row[1]
            used = row[2]
            if used:
                async with self:
                    self.reset_error_message = "This reset token has already been used."
                return
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=datetime.timezone.utc)
            if datetime.datetime.now(datetime.timezone.utc) > expires_at:
                async with self:
                    self.reset_error_message = "This reset token has expired."
                return

    @rx.event(background=True)
    async def reset_password(self):
        """Resets the user's password using the valid token."""
        async with self:
            self.is_resetting_password = True
            self.reset_error_message = ""
            if self.new_password != self.confirm_new_password:
                self.reset_error_message = "Passwords do not match."
                self.is_resetting_password = False
                return
            validation_error = self._validate_password(self.new_password)
            if validation_error:
                self.reset_error_message = validation_error
                self.is_resetting_password = False
                return
        async with rx.asession() as session:
            token_res = await session.execute(
                text(
                    "SELECT user_id FROM password_reset_tokens WHERE token = :token AND used = FALSE"
                ),
                {"token": self.reset_token},
            )
            row = token_res.first()
            if not row:
                async with self:
                    self.reset_error_message = "Invalid or expired token."
                    self.is_resetting_password = False
                return
            user_id = row[0]
            password_hash = bcrypt.hashpw(
                self.new_password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            await session.execute(
                text("UPDATE users SET password_hash = :hash WHERE id = :id"),
                {"hash": password_hash, "id": user_id},
            )
            await session.execute(
                text(
                    "UPDATE password_reset_tokens SET used = TRUE WHERE token = :token"
                ),
                {"token": self.reset_token},
            )
            await session.commit()
        async with self:
            self.is_resetting_password = False
            yield rx.toast(
                "Password reset successfully! Please sign in.", duration=3000
            )
            yield rx.redirect("/")

    @rx.event
    def logout(self):
        """Sign out the user and redirect to landing page."""
        super().logout()
        self.authenticated_user_id = None
        self.reset_form()
        self.is_sign_up = False
        return rx.redirect("/")