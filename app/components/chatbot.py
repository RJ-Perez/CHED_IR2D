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
                            rx.icon(
                                "file-text",
                                class_name="h-3 w-3 mr-1 inline stroke-blue-400",
                            ),
                            rx.el.span(
                                source["title"], class_name="text-xs text-blue-300"
                            ),
                            class_name="flex items-center",
                        ),
                    ),
                    class_name="mt-2 pt-2 border-t border-white/10",
                ),
            ),
            class_name=rx.cond(
                is_user,
                "bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-2xl rounded-tr-none px-4 py-3 max-w-[85%] shadow-md border border-blue-400/30",
                "bg-white/90 backdrop-blur-md text-gray-800 border border-blue-100 rounded-2xl rounded-tl-none px-4 py-3 max-w-[85%] shadow-sm",
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
                        rx.el.div(
                            rx.icon(
                                "cpu",
                                class_name="h-5 w-5 stroke-blue-200 mr-2 animate-pulse",
                            ),
                            rx.el.h3(
                                "IR²D CYBER-CORE",
                                class_name="font-bold text-white tracking-widest text-sm",
                            ),
                            class_name="flex items-center",
                        ),
                        rx.el.button(
                            rx.icon(
                                "x",
                                class_name="h-5 w-5 stroke-white/80 hover:stroke-white transition-transform hover:rotate-90",
                            ),
                            on_click=ChatbotState.toggle_open,
                        ),
                        rx.el.div(
                            class_name="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-blue-400/50"
                        ),
                        rx.el.div(
                            class_name="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-blue-400/50"
                        ),
                        class_name="relative flex items-center justify-between p-4 bg-gradient-to-r from-blue-900 via-indigo-900 to-blue-900 rounded-t-2xl border-b border-blue-500/30",
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
                                                    class_name="w-1.5 h-1.5 bg-blue-500 rounded-sm animate-pulse"
                                                ),
                                                rx.el.div(
                                                    class_name="w-1.5 h-1.5 bg-blue-400 rounded-sm animate-pulse delay-100"
                                                ),
                                                rx.el.div(
                                                    class_name="w-1.5 h-1.5 bg-blue-300 rounded-sm animate-pulse delay-200"
                                                ),
                                                class_name="flex space-x-1.5 p-2 bg-blue-50 border border-blue-100 rounded-md w-fit",
                                            ),
                                            class_name="flex justify-start mb-4",
                                        ),
                                    ),
                                    class_name="flex-1 overflow-y-auto p-4 bg-[radial-gradient(circle_at_top,_var(--tw-gradient-stops))] from-blue-50/50 via-white to-white min-h-[350px] max-h-[450px] flex flex-col",
                                    id="chatbot-messages",
                                ),
                                rx.el.form(
                                    rx.el.div(
                                        rx.el.input(
                                            placeholder="Type instruction...",
                                            name="input_value",
                                            class_name="flex-1 text-sm bg-gray-50/50 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all",
                                            default_value=ChatbotState.input_value,
                                        ),
                                        rx.el.button(
                                            rx.icon(
                                                "zap", class_name="h-4 w-4 stroke-white"
                                            ),
                                            type="submit",
                                            disabled=ChatbotState.is_typing,
                                            class_name="p-2.5 bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-xl hover:shadow-lg hover:shadow-blue-500/40 disabled:opacity-50 transition-all active:scale-90",
                                        ),
                                        class_name="flex gap-2 p-4 bg-white/80 backdrop-blur-md border-t border-gray-100",
                                    ),
                                    on_submit=ChatbotState.send_message,
                                    reset_on_submit=True,
                                ),
                                class_name="flex flex-col h-full",
                            ),
                        )
                    ),
                    class_name="w-85 md:w-96 bg-white rounded-2xl shadow-[0_20px_50px_rgba(37,99,235,0.15)] border border-blue-200/50 flex flex-col animate-in slide-in-from-bottom-8 duration-300 overflow-hidden mb-6",
                )
            ),
        ),
        rx.el.div(
            rx.cond(
                ~ChatbotState.is_open,
                rx.el.div(
                    rx.el.span(
                        class_name="absolute -inset-2 rounded-full bg-blue-400/20 animate-ping"
                    ),
                    rx.el.span(
                        class_name="absolute -inset-4 rounded-full bg-indigo-400/10 animate-ping delay-300"
                    ),
                    class_name="absolute inset-0",
                ),
            ),
            rx.el.button(
                rx.cond(
                    ChatbotState.is_open,
                    rx.icon("chevron-down", class_name="h-8 w-8 stroke-white"),
                    rx.el.div(
                        rx.icon("cpu", class_name="h-8 w-8 stroke-white"),
                        rx.el.div(
                            rx.icon("sparkles", class_name="h-4 w-4 stroke-yellow-300"),
                            class_name="absolute -top-1 -right-1 animate-bounce",
                        ),
                        class_name="relative",
                    ),
                ),
                on_click=ChatbotState.toggle_open,
                class_name="relative h-18 w-18 bg-gradient-to-tr from-blue-700 via-indigo-600 to-blue-500 text-white rounded-full shadow-[0_0_20px_rgba(37,99,235,0.4)] flex items-center justify-center transition-all duration-500 hover:scale-110 hover:rotate-12 active:scale-90 border-4 border-white/20 overflow-hidden",
            ),
            class_name="relative group",
        ),
        class_name="fixed bottom-8 right-8 z-50 flex flex-col items-end",
    )