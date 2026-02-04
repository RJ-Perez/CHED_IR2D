import reflex as rx
from typing import TypedDict
from sqlalchemy import text
import logging
from app.states.hei_state import HEIState


class Notification(TypedDict):
    id: int
    status: str
    reviewer_name: str
    comments: str
    is_read: bool


class NotificationState(rx.State):
    """Manages unread notifications for HEI review status updates from CHED."""

    notifications: list[Notification] = []
    show_notifications: bool = False
    read_notification_ids: list[int] = []

    @rx.var(cache=True)
    def unread_count(self) -> int:
        return len(
            [n for n in self.notifications if n["id"] not in self.read_notification_ids]
        )

    @rx.event
    def toggle_notifications(self):
        """
        Toggles the visibility of the notification dropdown.
        When opened, it marks all current notifications as read by adding their IDs
        to the read_notification_ids list, effectively clearing the red badge.
        """
        self.show_notifications = not self.show_notifications
        if self.show_notifications:
            for n in self.notifications:
                if n["id"] not in self.read_notification_ids:
                    self.read_notification_ids.append(n["id"])

    @rx.event(background=True)
    async def fetch_notifications(self):
        """Queries the institution_reviews table for status updates related to the selected HEI."""
        async with self:
            hei_state = await self.get_state(HEIState)
            if not hei_state.selected_hei:
                return
            inst_id = int(hei_state.selected_hei["id"])
        async with rx.asession() as session:
            result = await session.execute(
                text("""
                SELECT id, status, reviewer_name, comments
                FROM institution_reviews
                WHERE institution_id = :inst_id
                ORDER BY id DESC
                LIMIT 10
                """),
                {"inst_id": inst_id},
            )
            rows = result.all()
            async with self:
                self.notifications = [
                    {
                        "id": row[0],
                        "status": row[1],
                        "reviewer_name": row[2] if row[2] else "CHED Reviewer",
                        "comments": row[3] if row[3] else "No feedback provided.",
                        "is_read": row[0] in self.read_notification_ids,
                    }
                    for row in rows
                ]