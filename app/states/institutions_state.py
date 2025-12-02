import reflex as rx
from app.states.hei_state import HEIState, HEI
import asyncio


class InstitutionsState(rx.State):
    search_query: str = ""

    @rx.var
    async def stats(self) -> dict[str, int]:
        """Calculate statistics based on the HEI database."""
        hei_state = await self.get_state(HEIState)
        total = len(hei_state.hei_database)
        return {
            "total": total,
            "active": int(total * 0.65),
            "pending": int(total * 0.35),
        }

    @rx.var
    async def filtered_heis(self) -> list[HEI]:
        """Filter HEIs based on search query."""
        hei_state = await self.get_state(HEIState)
        if not self.search_query:
            return hei_state.hei_database
        query = self.search_query.lower()
        return [
            h
            for h in hei_state.hei_database
            if query in h["name"].lower() or query in h["address"].lower()
        ]

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query

    @rx.event
    def view_details(self, hei_id: str):
        return rx.toast(f"Viewing details for institution ID: {hei_id}")

    @rx.event
    def edit_institution(self, hei_id: str):
        return rx.toast(f"Editing institution ID: {hei_id}")

    @rx.event
    def delete_institution(self, hei_id: str):
        return rx.toast(f"Delete action triggered for ID: {hei_id} (Demo only)")