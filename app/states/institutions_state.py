import reflex as rx
from app.states.hei_state import HEIState, HEI
import asyncio
import logging
from sqlalchemy import text


class InstitutionsState(rx.State):
    search_query: str = ""
    delete_confirm_id: str = ""
    delete_confirm_name: str = ""
    show_delete_modal: bool = False
    show_view_modal: bool = False
    show_edit_modal: bool = False
    show_register_modal: bool = False
    selected_hei_data: HEI = {
        "id": "",
        "name": "",
        "address": "",
        "type": "",
        "admin_name": "",
        "street": "",
        "city": "",
    }
    edit_name: str = ""
    edit_street: str = ""
    edit_city: str = ""
    edit_admin: str = ""
    is_saving_edit: bool = False
    new_name: str = ""
    new_street: str = ""
    new_region: str = ""
    new_city: str = ""
    new_zip: str = ""
    new_contact: str = ""
    new_admin: str = ""
    is_registering: bool = False
    regions_map: dict[str, list[str]] = {
        "NCR (National Capital Region)": [
            "Manila",
            "Quezon City",
            "Caloocan",
            "Las Piñas",
            "Makati",
            "Malabon",
            "Mandaluyong",
            "Marikina",
            "Muntinlupa",
            "Navotas",
            "Parañaque",
            "Pasay",
            "Pasig",
            "San Juan",
            "Taguig",
            "Valenzuela",
            "Pateros",
        ],
        "CAR (Cordillera Administrative Region)": [
            "Baguio City",
            "Tabuk",
            "Bangued",
            "Lagawe",
            "Bontoc",
            "La Trinidad",
            "Luna",
        ],
        "Region I (Ilocos Region)": [
            "Laoag",
            "Batac",
            "Vigan",
            "Candon",
            "San Fernando City (La Union)",
            "Alaminos",
            "Dagupan",
            "San Carlos",
            "Urdaneta",
        ],
        "Region II (Cagayan Valley)": ["Tuguegarao", "Cauayan", "Ilagan", "Santiago"],
        "Region III (Central Luzon)": [
            "Angeles",
            "Mabalacat",
            "San Fernando City (Pampanga)",
            "Olongapo",
            "Balanga",
            "Bulacan",
            "Meycauayan",
            "San Jose del Monte",
            "Cabanatuan",
            "Gapan",
            "Muñoz",
            "Palayan",
            "San Jose City",
            "Tarlac City",
        ],
        "Region IV-A (CALABARZON)": [
            "Antipolo",
            "Bacoor",
            "Imus",
            "Dasmariñas",
            "Cavite City",
            "General Trias",
            "Tagaytay",
            "Trece Martires",
            "Biñan",
            "Cabuyao",
            "Calamba",
            "San Pedro",
            "Santa Rosa",
            "Batangas City",
            "Lipa",
            "Tanauan",
            "Lucena",
            "Tayabas",
        ],
    }

    @rx.var(cache=True)
    def regions(self) -> list[str]:
        return list(self.regions_map.keys())

    @rx.var(cache=True)
    def available_register_cities(self) -> list[str]:
        return self.regions_map.get(self.new_region, [])

    @rx.var(cache=True)
    def is_register_form_valid(self) -> bool:
        return all(
            [
                bool(self.new_name.strip()),
                bool(self.new_street.strip()),
                bool(self.new_region),
                bool(self.new_city),
                bool(self.new_zip.strip()),
                bool(self.new_contact.strip()),
                bool(self.new_admin.strip()),
            ]
        )

    @rx.event
    def set_new_region(self, value: str):
        self.new_region = value
        self.new_city = ""

    @rx.event
    def open_register_modal(self):
        self.show_register_modal = True
        self.new_name = ""
        self.new_street = ""
        self.new_region = ""
        self.new_city = ""
        self.new_zip = ""
        self.new_contact = ""
        self.new_admin = ""

    @rx.event
    def close_register_modal(self):
        self.show_register_modal = False

    @rx.event(background=True)
    async def register_new_institution(self):
        async with self:
            self.is_registering = True
            name = self.new_name
            street = self.new_street
            city = self.new_city
            region = self.new_region
            zip_code = self.new_zip
            contact = self.new_contact
            admin = self.new_admin
        async with rx.asession() as session:
            await session.execute(
                text("""
                    INSERT INTO institutions (
                        institution_name, 
                        admin_name, 
                        contact_number, 
                        street_address, 
                        city_municipality, 
                        region, 
                        zip_code, 
                        ranking_framework
                    )
                    VALUES (
                        :name, 
                        :admin, 
                        :contact, 
                        :street, 
                        :city, 
                        :region, 
                        :zip, 
                        'QS'
                    )
                """),
                {
                    "name": name,
                    "admin": admin,
                    "contact": contact,
                    "street": street,
                    "city": city,
                    "region": region,
                    "zip": zip_code,
                },
            )
            await session.commit()
        async with self:
            self.is_registering = False
            self.show_register_modal = False
            yield rx.toast("New institution registered successfully!")
            hei_state = await self.get_state(HEIState)
            yield HEIState.fetch_institutions

    @rx.var(cache=True)
    async def stats(self) -> dict[str, int]:
        """Calculate statistics based on the HEI database."""
        hei_state = await self.get_state(HEIState)
        total = len(hei_state.hei_database)
        return {"total": total}

    @rx.var(cache=True)
    async def filtered_heis(self) -> list[HEI]:
        """Filter HEIs based on search query (Name, Address, or ID)."""
        hei_state = await self.get_state(HEIState)
        if not self.search_query:
            return hei_state.hei_database
        query = self.search_query.lower()
        return [
            h
            for h in hei_state.hei_database
            if query in h["name"].lower()
            or query in h["address"].lower()
            or query in str(h["id"]).lower()
        ]

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query

    @rx.event
    async def view_details(self, hei_id: str):
        hei_state = await self.get_state(HEIState)
        hei = next((h for h in hei_state.hei_database if h["id"] == hei_id), None)
        if hei:
            self.selected_hei_data = hei
            self.show_view_modal = True

    @rx.event
    async def edit_institution(self, hei_id: str):
        hei_state = await self.get_state(HEIState)
        hei = next((h for h in hei_state.hei_database if h["id"] == hei_id), None)
        if hei:
            self.selected_hei_data = hei
            self.edit_name = hei["name"]
            self.edit_street = hei["street"]
            self.edit_city = hei["city"]
            self.edit_admin = hei["admin_name"]
            self.show_edit_modal = True

    @rx.event
    def close_modals(self):
        self.show_view_modal = False
        self.show_edit_modal = False

    @rx.event(background=True)
    async def save_institution_edit(self):
        async with self:
            self.is_saving_edit = True
            hei_id = self.selected_hei_data["id"]
            name = self.edit_name
            street = self.edit_street
            city = self.edit_city
            admin = self.edit_admin
        from sqlalchemy import text

        async with rx.asession() as session:
            await session.execute(
                text("""
                    UPDATE institutions 
                    SET institution_name = :name, 
                        street_address = :street, 
                        city_municipality = :city, 
                        admin_name = :admin 
                    WHERE id = :id
                """),
                {
                    "name": name,
                    "street": street,
                    "city": city,
                    "admin": admin,
                    "id": int(hei_id),
                },
            )
            await session.commit()
        async with self:
            self.is_saving_edit = False
            self.show_edit_modal = False
            yield rx.toast("Institution updated successfully.")
            hei_state = await self.get_state(HEIState)
            yield HEIState.fetch_institutions

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
        """Delete institution from database and update local state."""
        async with self:
            if not self.delete_confirm_id:
                return
            hei_id = self.delete_confirm_id
            hei_name = self.delete_confirm_name
        from sqlalchemy import text

        async with rx.asession() as session:
            await session.execute(
                text("DELETE FROM institution_scores WHERE institution_id = :id"),
                {"id": int(hei_id)},
            )
            await session.execute(
                text("DELETE FROM institutions WHERE id = :id"), {"id": int(hei_id)}
            )
            await session.commit()
        async with self:
            hei_state = await self.get_state(HEIState)
            hei_state.hei_database = [
                h for h in hei_state.hei_database if h["id"] != hei_id
            ]
            if hei_state.selected_hei and hei_state.selected_hei["id"] == hei_id:
                hei_state.selected_hei = None
            try:
                from app.states.reports_state import ReportsState

                reports_state = await self.get_state(ReportsState)
                reports_state.reports = [
                    r for r in reports_state.reports if r["id"] != hei_id
                ]
            except Exception as e:
                logging.exception(f"Error updating reports state after deletion: {e}")
            self.show_delete_modal = False
            self.delete_confirm_id = ""
            self.delete_confirm_name = ""
            yield rx.toast(
                f"Institution '{hei_name}' has been deleted from the database.",
                duration=3000,
                position="top-center",
            )