import reflex as rx
from app.states.settings_state import SettingsState


def section_header(title: str, subtitle: str, icon: str) -> rx.Component:
    """Reusable section header with icon."""
    return rx.el.div(
        rx.icon(icon, class_name="h-5 w-5 text-blue-600 mr-2 mt-0.5"),
        rx.el.div(
            rx.el.h3(title, class_name="text-lg font-semibold text-gray-900"),
            rx.el.p(subtitle, class_name="text-sm text-gray-500 mt-1"),
        ),
        class_name="flex items-start mb-6",
    )


def setting_input(
    label: str,
    value: rx.Var,
    on_change: rx.event.EventType,
    type_: str = "text",
    placeholder: str = "",
    disabled: bool = False,
) -> rx.Component:
    """Standard styled input for settings forms."""
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-gray-700 mb-1"),
        rx.el.input(
            type=type_,
            default_value=value,
            on_change=on_change,
            placeholder=placeholder,
            disabled=disabled,
            class_name=rx.cond(
                disabled,
                "w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded-lg text-gray-500 cursor-not-allowed",
                "w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors",
            ),
        ),
        class_name="mb-4",
    )


def toggle_switch(
    label: str, checked: rx.Var, on_toggle: rx.event.EventType
) -> rx.Component:
    """Custom toggle switch using HTML checkbox."""
    return rx.el.label(
        rx.el.div(label, class_name="text-sm font-medium text-gray-700"),
        rx.el.div(
            rx.el.input(
                type="checkbox",
                checked=checked,
                on_change=on_toggle,
                class_name="sr-only peer",
            ),
            rx.el.div(
                class_name="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
            ),
            class_name="relative inline-flex items-center cursor-pointer",
        ),
        class_name="flex items-center justify-between py-3 border-b border-gray-100 last:border-0",
    )


def save_button(is_loading: rx.Var, on_click: rx.event.EventType) -> rx.Component:
    """Standard save button with loading state."""
    return rx.el.div(
        rx.el.button(
            rx.cond(
                is_loading,
                rx.el.span(
                    rx.el.span(
                        class_name="animate-spin inline-block h-4 w-4 border-2 border-white border-b-transparent rounded-full mr-2"
                    ),
                    "Saving...",
                    class_name="flex items-center",
                ),
                "Save Changes",
            ),
            on_click=on_click,
            disabled=is_loading,
            class_name="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-60 disabled:cursor-not-allowed transition-colors",
        ),
        class_name="flex justify-end pt-4",
    )


def account_settings_section() -> rx.Component:
    return rx.el.div(
        section_header(
            "Account Settings", "Manage your personal account information.", "user"
        ),
        rx.el.div(
            setting_input(
                "Full Name",
                SettingsState.full_name,
                SettingsState.set_full_name,
                placeholder="Your Full Name",
            ),
            setting_input(
                "Email Address",
                SettingsState.email,
                rx.noop,
                disabled=True,
                type_="email",
            ),
            rx.el.div(class_name="h-px bg-gray-100 my-6"),
            rx.el.h4(
                "Change Password", class_name="text-sm font-semibold text-gray-900 mb-4"
            ),
            setting_input(
                "Current Password",
                SettingsState.current_password,
                SettingsState.set_current_password,
                type_="password",
                placeholder="••••••••",
            ),
            rx.el.div(
                setting_input(
                    "New Password",
                    SettingsState.new_password,
                    SettingsState.set_new_password,
                    type_="password",
                    placeholder="••••••••",
                ),
                setting_input(
                    "Confirm New Password",
                    SettingsState.confirm_password,
                    SettingsState.set_confirm_password,
                    type_="password",
                    placeholder="••••••••",
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
            ),
            save_button(
                SettingsState.is_saving_account, SettingsState.save_account_settings
            ),
            class_name="space-y-1",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def institution_profile_section() -> rx.Component:
    return rx.el.div(
        section_header(
            "Institution Profile",
            "Update your Higher Education Institution details.",
            "building-2",
        ),
        setting_input(
            "Institution Name",
            SettingsState.institution_name,
            SettingsState.set_institution_name,
        ),
        setting_input(
            "Official Address",
            SettingsState.institution_address,
            SettingsState.set_institution_address,
        ),
        rx.el.div(
            setting_input(
                "Contact Number",
                SettingsState.contact_number,
                SettingsState.set_contact_number,
                placeholder="+63...",
            ),
            setting_input(
                "Administrator Name",
                SettingsState.admin_name,
                SettingsState.set_admin_name,
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
        ),
        save_button(
            SettingsState.is_saving_profile, SettingsState.save_institution_profile
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def notifications_section() -> rx.Component:
    return rx.el.div(
        section_header(
            "Notification Preferences",
            "Control how and when you receive updates.",
            "bell",
        ),
        rx.el.div(
            toggle_switch(
                "Assessment Updates",
                SettingsState.notify_assessment,
                SettingsState.toggle_notify_assessment,
            ),
            toggle_switch(
                "Report Generation Alerts",
                SettingsState.notify_report,
                SettingsState.toggle_notify_report,
            ),
            toggle_switch(
                "System Announcements",
                SettingsState.notify_announcements,
                SettingsState.toggle_notify_announcements,
            ),
            toggle_switch(
                "Weekly Progress Summary",
                SettingsState.notify_weekly,
                SettingsState.toggle_notify_weekly,
            ),
            class_name="flex flex-col",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def assessment_preferences_section() -> rx.Component:
    return rx.el.div(
        section_header(
            "Assessment Framework", "Configure your primary ranking system.", "award"
        ),
        rx.el.div(
            rx.el.div(
                rx.icon(
                    "flag_triangle_right",
                    class_name="h-5 w-5 text-amber-600 mr-3 mt-0.5",
                ),
                rx.el.div(
                    rx.el.p(
                        "Changing your ranking framework will alter the data entry requirements and scoring metrics.",
                        class_name="text-sm text-amber-800 font-medium",
                    ),
                    rx.el.p(
                        "Existing data may not be fully compatible with the new framework.",
                        class_name="text-xs text-amber-600 mt-1",
                    ),
                ),
                class_name="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-start mb-6",
            ),
            rx.el.div(
                rx.el.label(
                    rx.el.input(
                        type="radio",
                        name="framework",
                        checked=SettingsState.ranking_framework == "QS",
                        on_change=lambda: SettingsState.set_ranking_framework("QS"),
                        class_name="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500",
                    ),
                    rx.el.span(
                        "QS World University Rankings",
                        class_name="ml-3 block text-sm font-medium text-gray-700",
                    ),
                    class_name="flex items-center p-4 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50",
                ),
                rx.el.label(
                    rx.el.input(
                        type="radio",
                        name="framework",
                        checked=SettingsState.ranking_framework == "THE",
                        on_change=lambda: SettingsState.set_ranking_framework("THE"),
                        class_name="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500",
                    ),
                    rx.el.span(
                        "Times Higher Education (THE)",
                        class_name="ml-3 block text-sm font-medium text-gray-700",
                    ),
                    class_name="flex items-center p-4 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50",
                ),
                class_name="space-y-3 mb-6",
            ),
            save_button(
                SettingsState.is_saving_framework, SettingsState.save_framework_settings
            ),
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def settings_content() -> rx.Component:
    """Main settings page layout."""
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Settings & Preferences", class_name="text-2xl font-bold text-gray-900"
            ),
            rx.el.p(
                "Manage your account settings, institution profile, and system preferences.",
                class_name="text-gray-600 mt-1",
            ),
            class_name="mb-8",
        ),
        rx.el.div(
            rx.el.div(
                account_settings_section(),
                notifications_section(),
                class_name="space-y-6",
            ),
            rx.el.div(
                institution_profile_section(),
                assessment_preferences_section(),
                class_name="space-y-6",
            ),
            class_name="grid grid-cols-1 xl:grid-cols-2 gap-6",
        ),
        class_name="max-w-7xl mx-auto",
    )