import reflex as rx
from app.states.auth_state import AuthState
from app.states.hei_state import HEIState
from sqlalchemy import text
import asyncio
import logging
import bcrypt


class SettingsState(rx.State):
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    current_password: str = ""
    new_password: str = ""
    confirm_password: str = ""
    institution_name: str = ""
    institution_address: str = ""
    contact_number: str = ""
    admin_name: str = ""
    notify_assessment: bool = True
    notify_report: bool = True
    notify_announcements: bool = False
    notify_weekly: bool = False
    ranking_framework: str = ""
    is_saving_account: bool = False
    is_saving_profile: bool = False
    is_saving_framework: bool = False

    @rx.event(background=True)
    async def on_load(self):
        """Load settings from the database for the authenticated user."""
        async with self:
            auth = await self.get_state(AuthState)
            user_id = auth.authenticated_user_id
            hei = await self.get_state(HEIState)
            selected_inst_id = int(hei.selected_hei["id"]) if hei.selected_hei else None
        if user_id is None:
            return
        async with rx.asession() as session:
            user_result = await session.execute(
                text("SELECT first_name, last_name, email FROM users WHERE id = :uid"),
                {"uid": user_id},
            )
            user_row = user_result.first()
            if selected_inst_id:
                inst_result = await session.execute(
                    text("""
                        SELECT institution_name, street_address, city_municipality, contact_number, admin_name, ranking_framework
                        FROM institutions
                        WHERE id = :inst_id
                    """),
                    {"inst_id": selected_inst_id},
                )
                inst_row = inst_result.first()
            else:
                inst_row = None
            async with self:
                if user_row:
                    self.first_name = user_row[0]
                    self.last_name = user_row[1]
                    self.email = user_row[2]
                if inst_row:
                    self.institution_name = inst_row[0]
                    self.institution_address = f"{inst_row[1]}, {inst_row[2]}"
                    self.contact_number = inst_row[3] if inst_row[3] else ""
                    self.admin_name = inst_row[4] if inst_row[4] else ""
                    self.ranking_framework = inst_row[5] if inst_row[5] else "QS"

    @rx.event
    def set_first_name(self, value: str):
        self.first_name = value

    @rx.event
    def set_last_name(self, value: str):
        self.last_name = value

    @rx.event
    def set_current_password(self, value: str):
        self.current_password = value

    @rx.event
    def set_new_password(self, value: str):
        self.new_password = value

    @rx.event
    def set_confirm_password(self, value: str):
        self.confirm_password = value

    @rx.event
    def set_institution_name(self, value: str):
        self.institution_name = value

    @rx.event
    def set_institution_address(self, value: str):
        self.institution_address = value

    @rx.event
    def set_contact_number(self, value: str):
        self.contact_number = value

    @rx.event
    def set_admin_name(self, value: str):
        self.admin_name = value

    @rx.event
    def toggle_notify_assessment(self):
        self.notify_assessment = not self.notify_assessment

    @rx.event
    def toggle_notify_report(self):
        self.notify_report = not self.notify_report

    @rx.event
    def toggle_notify_announcements(self):
        self.notify_announcements = not self.notify_announcements

    @rx.event
    def toggle_notify_weekly(self):
        self.notify_weekly = not self.notify_weekly

    @rx.event
    def set_ranking_framework(self, value: str):
        self.ranking_framework = value

    @rx.event(background=True)
    async def save_account_settings(self):
        """Persist account changes to the users table."""
        async with self:
            self.is_saving_account = True
            auth = await self.get_state(AuthState)
            user_id = auth.authenticated_user_id
            first = self.first_name
            last = self.last_name
            current_pass = self.current_password
            new_pass = self.new_password
            confirm_pass = self.confirm_password
        if user_id is None:
            async with self:
                self.is_saving_account = False
            return
        async with rx.asession() as session:
            if new_pass:
                if new_pass != confirm_pass:
                    async with self:
                        self.is_saving_account = False
                    yield rx.toast.error("New passwords do not match.")
                    return
                user_check = await session.execute(
                    text("SELECT password_hash FROM users WHERE id = :uid"),
                    {"uid": user_id},
                )
                row = user_check.first()
                if (
                    not row
                    or not row[0]
                    or (
                        not bcrypt.checkpw(
                            current_pass.encode("utf-8"), row[0].encode("utf-8")
                        )
                    )
                ):
                    async with self:
                        self.is_saving_account = False
                    yield rx.toast.error("Incorrect current password.")
                    return
                new_hash = bcrypt.hashpw(
                    new_pass.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8")
                await session.execute(
                    text(
                        "UPDATE users SET first_name = :f, last_name = :l, password_hash = :h WHERE id = :uid"
                    ),
                    {"f": first, "l": last, "h": new_hash, "uid": user_id},
                )
            else:
                await session.execute(
                    text(
                        "UPDATE users SET first_name = :f, last_name = :l WHERE id = :uid"
                    ),
                    {"f": first, "l": last, "uid": user_id},
                )
            await session.commit()
        async with self:
            self.current_password = ""
            self.new_password = ""
            self.confirm_password = ""
            self.is_saving_account = False
            yield rx.toast("Account details synchronized.")

    @rx.event(background=True)
    async def save_institution_profile(self):
        """Persist institution profile changes to the institutions table."""
        async with self:
            self.is_saving_profile = True
            hei_state = await self.get_state(HEIState)
            if not hei_state.selected_hei:
                self.is_saving_profile = False
                yield rx.toast.error("No institution selected to update.")
                return
            inst_id = int(hei_state.selected_hei["id"])
            name = self.institution_name
            contact = self.contact_number
            admin = self.admin_name
        async with rx.asession() as session:
            await session.execute(
                text("""
                    UPDATE institutions 
                    SET institution_name = :name, contact_number = :contact, admin_name = :admin 
                    WHERE id = :id
                """),
                {"name": name, "contact": contact, "admin": admin, "id": inst_id},
            )
            await session.commit()
        async with self:
            self.is_saving_profile = False
            yield rx.toast("Institutional profile updated in master database.")

    @rx.event(background=True)
    async def save_framework_settings(self):
        """Update preferred ranking framework in the database."""
        async with self:
            self.is_saving_framework = True
            hei_state = await self.get_state(HEIState)
            if not hei_state.selected_hei:
                self.is_saving_framework = False
                return
            inst_id = int(hei_state.selected_hei["id"])
            framework = self.ranking_framework
        async with rx.asession() as session:
            await session.execute(
                text("UPDATE institutions SET ranking_framework = :f WHERE id = :id"),
                {"f": framework, "id": inst_id},
            )
            await session.commit()
        async with self:
            self.is_saving_framework = False
            yield rx.toast("Global ranking framework updated.")