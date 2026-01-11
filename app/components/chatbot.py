import reflex as rx
from app.states.chatbot_state import ChatbotState


def message_bubble(message: dict) -> rx.Component:
    is_user = message["role"] == "user"
    return rx.el.div(
        rx.el.div(
            rx.el.p(message["content"], class_name="text-sm leading-relaxed"),
            rx.cond(
                message["sources"].length() > 0,
                rx.el.div(
                    rx.el.p(
                        "Sources:",
                        class_name="text-[10px] font-bold uppercase text-gray-400 mt-2 mb-1",
                    ),
                    rx.foreach(
                        message["sources"],
                        lambda source: rx.el.div(
                            rx.icon("file-text", class_name="h-3 w-3 mr-1 inline"),
                            rx.el.span(source["title"], class_name="text-xs"),
                            class_name="flex items-center text-blue-300",
                        ),
                    ),
                    class_name="mt-2 pt-2 border-t border-white/10",
                ),
            ),
            class_name=rx.cond(
                is_user,
                "bg-blue-600 text-white rounded-2xl rounded-tr-none px-4 py-3 max-w-[85%] shadow-sm",
                "bg-white text-gray-800 border border-gray-200 rounded-2xl rounded-tl-none px-4 py-3 max-w-[85%] shadow-sm",
            ),
        ),
        class_name=rx.cond(is_user, "flex justify-end mb-4", "flex justify-start mb-4"),
    )


def escalation_form() -> rx.Component:
    """Form for submitting a support ticket to human agent."""
    return rx.el.div(
        rx.el.div(
            rx.icon("headset", class_name="h-8 w-8 text-blue-600 mb-2"),
            rx.el.h4("Contact Support", class_name="font-semibold text-gray-900"),
            rx.el.p(
                "We noticed you might need human assistance. Create a ticket below.",
                class_name="text-xs text-gray-500 text-center mb-4",
            ),
            class_name="flex flex-col items-center pt-6 pb-2 px-6",
        ),
        rx.el.div(
            rx.el.label(
                "Your Email", class_name="block text-xs font-medium text-gray-700 mb-1"
            ),
            rx.el.input(
                placeholder="name@institution.edu.ph",
                on_change=ChatbotState.set_ticket_email,
                class_name="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 mb-3",
                default_value=ChatbotState.ticket_email,
            ),
            rx.el.label(
                "How can we help?",
                class_name="block text-xs font-medium text-gray-700 mb-1",
            ),
            rx.el.textarea(
                placeholder="Describe your issue...",
                on_change=ChatbotState.set_ticket_reason,
                class_name="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 mb-4 h-24 resize-none",
                default_value=ChatbotState.ticket_reason,
            ),
            rx.el.div(
                rx.el.button(
                    "Cancel",
                    on_click=ChatbotState.cancel_escalation,
                    class_name="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors",
                ),
                rx.el.button(
                    rx.cond(
                        ChatbotState.is_submitting_ticket,
                        rx.el.span("Sending...", class_name="animate-pulse"),
                        "Submit Ticket",
                    ),
                    on_click=ChatbotState.submit_support_ticket,
                    disabled=ChatbotState.is_submitting_ticket,
                    class_name="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors",
                ),
                class_name="flex justify-end gap-2",
            ),
            class_name="px-6 pb-6",
        ),
        class_name="bg-gray-50 h-full flex flex-col overflow-y-auto min-h-[300px]",
    )


def chatbot_component() -> rx.Component:
    return rx.el.div(
        rx.cond(
            ChatbotState.is_open,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            "CHED IR²D Assistant", class_name="font-semibold text-white"
                        ),
                        rx.el.button(
                            rx.icon(
                                "x", class_name="h-5 w-5 text-white/80 hover:text-white"
                            ),
                            on_click=ChatbotState.toggle_open,
                        ),
                        class_name="flex items-center justify-between p-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-t-xl",
                    ),
                    rx.el.div(
                        rx.cond(
                            ChatbotState.show_escalation_form,
                            escalation_form(),
                            rx.el.div(
                                rx.el.div(
                                    rx.foreach(ChatbotState.messages, message_bubble),
                                    rx.cond(
                                        ChatbotState.is_typing,
                                        rx.el.div(
                                            rx.el.div(
                                                rx.el.div(
                                                    class_name="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                                                ),
                                                rx.el.div(
                                                    class_name="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"
                                                ),
                                                rx.el.div(
                                                    class_name="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"
                                                ),
                                                class_name="flex space-x-1 p-2 bg-gray-100 rounded-xl w-fit",
                                            ),
                                            class_name="flex justify-start mb-4",
                                        ),
                                    ),
                                    class_name="flex-1 overflow-y-auto p-4 bg-gray-50 min-h-[300px] max-h-[400px] flex flex-col",
                                    id="chatbot-messages",
                                ),
                                rx.el.form(
                                    rx.el.div(
                                        rx.el.input(
                                            placeholder="Ask about rankings, guides...",
                                            name="input_value",
                                            class_name="flex-1 text-sm border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
                                            default_value=ChatbotState.input_value,
                                        ),
                                        rx.el.button(
                                            rx.icon("send", class_name="h-4 w-4"),
                                            type="submit",
                                            disabled=ChatbotState.is_typing,
                                            class_name="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50",
                                        ),
                                        class_name="flex gap-2 p-3 bg-white border-t border-gray-200",
                                    ),
                                    on_submit=ChatbotState.send_message,
                                    reset_on_submit=True,
                                ),
                                class_name="flex flex-col h-full",
                            ),
                        )
                    ),
                    class_name="w-80 md:w-96 bg-white rounded-xl shadow-2xl border border-gray-200 flex flex-col animate-in slide-in-from-bottom-5 duration-200 overflow-hidden mb-4",
                )
            ),
        ),
        rx.el.div(
            rx.cond(
                ~ChatbotState.is_open,
                rx.el.span(
                    class_name="absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75 animate-ping"
                ),
            ),
            rx.el.button(
                rx.cond(
                    ChatbotState.is_open,
                    rx.icon("chevron-down", class_name="h-8 w-8 text-white"),
                    rx.el.div(
                        rx.icon("bot", class_name="h-8 w-8 text-white"),
                        rx.icon(
                            "sparkles",
                            class_name="absolute -top-1 -right-1 h-4 w-4 text-yellow-300 animate-pulse",
                        ),
                        class_name="relative",
                    ),
                ),
                on_click=ChatbotState.toggle_open,
                class_name="relative h-16 w-16 bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-full shadow-xl shadow-blue-500/30 flex items-center justify-center transition-all duration-300 hover:scale-110 active:scale-95 border-2 border-white/20",
            ),
            class_name="relative group",
        ),
        class_name="fixed bottom-6 right-6 z-50 flex flex-col items-end",
    )