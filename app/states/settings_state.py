import reflex as rx
from app.states.auth_state import AuthState
from app.states.hei_state import HEIState
import asyncio


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

    @rx.event
    async def on_load(self):
        """Load initial settings from Auth and HEI states."""
        auth = await self.get_state(AuthState)
        hei = await self.get_state(HEIState)
        self.first_name = auth.first_name or "Juan"
        self.last_name = auth.last_name or "Dela Cruz"
        self.email = auth.email or "admin@university.edu.ph"
        if hei.selected_hei:
            self.institution_name = hei.selected_hei["name"]
            self.institution_address = hei.selected_hei["address"]
        elif hei.reg_name:
            self.institution_name = hei.reg_name
            self.institution_address = hei.reg_address
        else:
            self.institution_name = (
                auth.institution_name or "University of the Philippines"
            )
            self.institution_address = "Diliman, Quezon City"
        self.contact_number = hei.reg_contact or "+63 2 8123 4567"
        self.admin_name = hei.reg_admin or f"{self.first_name} {self.last_name}"
        self.ranking_framework = hei.ranking_framework or "QS"

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
        async with self:
            self.is_saving_account = True
        await asyncio.sleep(1.0)
        async with self:
            if self.new_password and self.new_password != self.confirm_password:
                self.is_saving_account = False
                yield rx.toast("New passwords do not match.", duration=3000)
        async with self:
            auth = await self.get_state(AuthState)
            auth.first_name = self.first_name
            auth.last_name = self.last_name
            self.current_password = ""
            self.new_password = ""
            self.confirm_password = ""
            self.is_saving_account = False
            yield rx.toast("Account settings saved successfully.", duration=3000)

    @rx.event(background=True)
    async def save_institution_profile(self):
        async with self:
            self.is_saving_profile = True
        await asyncio.sleep(1.0)
        async with self:
            hei = await self.get_state(HEIState)
            hei.reg_name = self.institution_name
            hei.reg_address = self.institution_address
            hei.reg_contact = self.contact_number
            hei.reg_admin = self.admin_name
            self.is_saving_profile = False
            yield rx.toast("Institution profile updated.", duration=3000)

    @rx.event(background=True)
    async def save_framework_settings(self):
        async with self:
            self.is_saving_framework = True
        await asyncio.sleep(1.5)
        async with self:
            hei = await self.get_state(HEIState)
            hei.ranking_framework = self.ranking_framework
            self.is_saving_framework = False
            yield rx.toast("Ranking framework preferences updated.", duration=3000)