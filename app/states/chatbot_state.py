import reflex as rx
from typing import TypedDict
import os
import logging
import resend
import asyncio
import re
from app.rag.retrieval import retrieve_documents, format_context

try:
    from google import genai
    from google.genai import types

    GOOGLE_AI_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_AI_AVAILABLE = bool(GOOGLE_AI_API_KEY)
except ImportError as e:
    logging.exception(f"Google GenAI not installed: {e}")
    GOOGLE_AI_AVAILABLE = False
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
ESCALATION_KEYWORDS = [
    "speak to human",
    "contact support",
    "escalate",
    "talk to someone",
    "talk to a person",
    "human help",
    "agent",
    "support ticket",
]


class Source(TypedDict):
    title: str
    id: str


class Message(TypedDict):
    role: str
    content: str
    sources: list[Source]


class ChatbotState(rx.State):
    is_open: bool = False
    messages: list[Message] = [
        {
            "role": "assistant",
            "content": "Hello! I'm your IR²D Assistant. I can help you with app navigation, ranking frameworks, and data entry guides. What would you like to know?",
            "sources": [],
        }
    ]
    input_value: str = ""
    is_typing: bool = False
    show_escalation_form: bool = False
    ticket_email: str = ""
    ticket_reason: str = ""
    is_submitting_ticket: bool = False

    @rx.event
    def toggle_open(self):
        self.is_open = not self.is_open
        if not self.is_open:
            self.show_escalation_form = False

    @rx.event
    def set_input_value(self, value: str):
        self.input_value = value

    @rx.event
    def set_ticket_email(self, value: str):
        self.ticket_email = value

    @rx.event
    def set_ticket_reason(self, value: str):
        self.ticket_reason = value

    @rx.event
    def cancel_escalation(self):
        self.show_escalation_form = False
        self.ticket_reason = ""

    @rx.event(background=True)
    async def submit_support_ticket(self):
        async with self:
            if not self.ticket_email or not self.ticket_reason:
                yield rx.toast("Please provide both email and reason.", duration=3000)
                return
            self.is_submitting_ticket = True
        ticket_id = f"TKT-{os.urandom(2).hex().upper()}"
        try:
            if RESEND_API_KEY:
                resend.Emails.send(
                    {
                        "from": "onboarding@resend.dev",
                        "to": self.ticket_email,
                        "subject": f"[CHED IR²D] Support Ticket Received #{ticket_id}",
                        "html": f"<p>We received your request:</p><blockquote>{self.ticket_reason}</blockquote><p>Our team will get back to you shortly.</p>",
                    }
                )
            else:
                logging.info(
                    f"Mock Ticket Submitted: {ticket_id} | {self.ticket_email} | {self.ticket_reason}"
                )
            await asyncio.sleep(1.0)
            async with self:
                self.messages.append(
                    {
                        "role": "assistant",
                        "content": f"Support ticket #{ticket_id} has been created. A confirmation has been sent to {self.ticket_email}. Our team will contact you shortly.",
                        "sources": [],
                    }
                )
                self.show_escalation_form = False
                self.ticket_reason = ""
                self.is_submitting_ticket = False
                yield rx.toast("Support ticket submitted successfully!", duration=3000)
        except Exception as e:
            logging.exception(f"Error submitting ticket: {e}")
            async with self:
                self.is_submitting_ticket = False
                yield rx.toast(
                    "Failed to submit ticket. Please try again.", duration=3000
                )

    def _format_history(self, limit: int = 6) -> str:
        """Formats recent conversation history for the AI prompt."""
        history_parts = []
        for msg in self.messages[-limit:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_parts.append(f"{role}: {msg['content']}")
        return """
""".join(history_parts)

    @rx.event(background=True)
    async def send_message(self, form_data: dict):
        user_message = form_data.get("input_value") or self.input_value
        if not user_message.strip():
            return
        async with self:
            self.messages.append(
                {"role": "user", "content": user_message, "sources": []}
            )
            self.input_value = ""
            self.is_typing = True
        if any((keyword in user_message.lower() for keyword in ESCALATION_KEYWORDS)):
            async with self:
                self.is_typing = False
                self.show_escalation_form = True
                from app.states.auth_state import AuthState

                auth_state = await self.get_state(AuthState)
                if auth_state.email:
                    self.ticket_email = auth_state.email
                self.ticket_reason = user_message
            return
        retrieved_docs = retrieve_documents(user_message, top_k=3)
        context_text = format_context(retrieved_docs)
        sources_data = [
            {"title": doc["title"], "id": doc["id"]} for doc in retrieved_docs
        ]
        async with self:
            history_text = self._format_history()
        response_content = (
            "I apologize, but I cannot process your request at the moment."
        )
        if GOOGLE_AI_AVAILABLE:
            try:
                client = genai.Client(api_key=GOOGLE_AI_API_KEY)
                system_prompt = """
                You are a helpful AI support assistant for the CHED International Ranking Readiness Dashboard (IR²D).
                Use the provided context documentation to answer the user's question accurately.
                If the answer is not in the context, politely state that you don't have that information but can help with app features or general ranking queries.
                Keep answers concise, professional, and encouraging.
                Do not invent features that are not in the documentation.
                """
                full_prompt = f"Context information:\n{context_text}\n\nConversation History:\n{history_text}\n\nUser Question: {user_message}"
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = await client.aio.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=full_prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=system_prompt, temperature=0.3
                            ),
                        )
                        if response and response.text:
                            response_content = response.text
                            break
                    except Exception as e:
                        error_str = str(e)
                        is_retriable = (
                            "429" in error_str
                            or "RESOURCE_EXHAUSTED" in error_str
                            or "503" in error_str
                            or ("UNAVAILABLE" in error_str)
                        )
                        if is_retriable and attempt < max_retries - 1:
                            wait_time = 2.0 * 2**attempt
                            retry_match = re.search(
                                "retry in (\\d+(\\.\\d+)?)s", error_str
                            )
                            if retry_match:
                                wait_time = float(retry_match.group(1)) + 1.0
                            wait_time = min(wait_time, 60.0)
                            logging.warning(
                                f"Chatbot AI error (Rate limit or Unavailable). Retrying in {wait_time:.2f}s"
                            )
                            await asyncio.sleep(wait_time)
                        else:
                            logging.exception(f"Chatbot generation error: {e}")
                            break
            except Exception as e:
                logging.exception(f"Chatbot AI Error: {e}")
                response_content = "I'm having trouble connecting to the AI service right now. Please try again later."
        else:
            response_content = "AI service is not configured. Please check API keys."
        async with self:
            self.messages.append(
                {
                    "role": "assistant",
                    "content": response_content,
                    "sources": sources_data,
                }
            )
            self.is_typing = False