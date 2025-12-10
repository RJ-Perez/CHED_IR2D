import reflex as rx
from app.states.hei_state import HEIState, HEI
import asyncio


class InstitutionsState(rx.State):
    search_query: str = ""
    delete_confirm_id: str = ""
    delete_confirm_name: str = ""
    show_delete_modal: bool = False

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
    def confirm_delete(self, hei_id: str, hei_name: str):
        """Open delete confirmation modal."""
        self.delete_confirm_id = hei_id
        self.delete_confirm_name = hei_name
        self.show_delete_modal = True

    @rx.event
    def cancel_delete(self):
        """Close delete confirmation modal."""
        self.show_delete_modal = False
        self.delete_confirm_id = ""
        self.delete_confirm_name = ""

    @rx.event(background=True)
    async def delete_institution(self):
        """Delete institution from database."""
        # Capture ids inside a mutable context to avoid ImmutableStateError.
        async with self:
            if not self.delete_confirm_id:
                return
            hei_id = self.delete_confirm_id
            hei_name = self.delete_confirm_name
        
        # Get HEI state and remove institution
        hei_state = await self.get_state(HEIState)
        async with hei_state:
            hei_state.hei_database = [
                h for h in hei_state.hei_database if h["id"] != hei_id
            ]
            # Clear selection if deleted institution was selected
            if hei_state.selected_hei and hei_state.selected_hei["id"] == hei_id:
                hei_state.selected_hei = None
        
        # Also remove from reports if exists
        try:
            from app.states.reports_state import ReportsState
            reports_state = await self.get_state(ReportsState)
            async with reports_state:
                reports_state.reports = [
                    r for r in reports_state.reports if r["id"] != hei_id
                ]
        except Exception:
            pass  # Reports state might not be available
        
        # Close modal and show success message
        async with self:
            self.show_delete_modal = False
            self.delete_confirm_id = ""
            self.delete_confirm_name = ""
        
        yield rx.toast(
            f"Institution '{hei_name}' has been deleted successfully.",
            duration=3000,
            position="top-center",
        )