import reflex as rx
from typing import TypedDict, Optional
import asyncio
from sqlalchemy import text
import logging


class HEI(TypedDict):
    id: str
    name: str
    address: str


class HEIState(rx.State):
    hei_database: list[HEI] = []
    search_query: str = ""
    selected_hei: Optional[HEI] = None
    ranking_framework: str = ""
    is_registration_mode: bool = False
    reg_name: str = ""
    reg_street: str = ""
    reg_region: str = ""
    reg_city: str = ""
    reg_zip: str = ""
    reg_contact: str = ""
    reg_admin: str = ""
    is_loading: bool = False
    regions_map: dict[str, list[str]] = {
        "NCR": [
            "Quezon City",
            "Manila",
            "Makati",
            "Pasig",
            "Taguig",
            "Parañaque",
            "Las Piñas",
            "Mandaluyong",
            "San Juan",
            "Marikina",
            "Pasay",
            "Caloocan",
            "Malabon",
            "Navotas",
            "Valenzuela",
            "Muntinlupa",
            "Pateros",
        ],
        "Region IV-A": ["Cavite", "Laguna", "Batangas", "Rizal", "Quezon"],
        "Region III": [
            "Bulacan",
            "Pampanga",
            "Tarlac",
            "Nueva Ecija",
            "Zambales",
            "Bataan",
            "Aurora",
        ],
    }

    @rx.var
    def regions(self) -> list[str]:
        return list(self.regions_map.keys())

    @rx.var
    def available_cities(self) -> list[str]:
        return self.regions_map.get(self.reg_region, [])

    @rx.var
    def reg_address(self) -> str:
        """Combines address components into a single string."""
        parts = [self.reg_street, self.reg_city, self.reg_region, self.reg_zip]
        return ", ".join([p for p in parts if p])

    @rx.var
    def filtered_heis(self) -> list[HEI]:
        if not self.search_query:
            return []
        query = self.search_query.lower()
        return [h for h in self.hei_database if query in h["name"].lower()]

    @rx.var
    def is_form_valid(self) -> bool:
        if self.is_registration_mode:
            return (
                bool(self.reg_name)
                and bool(self.reg_street)
                and bool(self.reg_region)
                and bool(self.reg_city)
                and bool(self.reg_zip)
                and bool(self.reg_contact)
                and bool(self.reg_admin)
                and bool(self.ranking_framework)
            )
        return bool(self.selected_hei) and bool(self.ranking_framework)

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query
        if self.selected_hei and self.selected_hei["name"] != query:
            self.selected_hei = None

    @rx.event
    def select_hei(self, hei: HEI):
        self.selected_hei = hei
        self.search_query = hei["name"]
        self.is_registration_mode = False

    @rx.event
    def set_ranking_framework(self, framework: str):
        self.ranking_framework = framework

    @rx.event
    def toggle_registration_mode(self):
        self.is_registration_mode = not self.is_registration_mode
        self.selected_hei = None
        self.search_query = ""
        self.ranking_framework = ""

    @rx.event
    def set_reg_name(self, value: str):
        self.reg_name = value

    @rx.event
    def set_reg_street(self, value: str):
        self.reg_street = value

    @rx.event
    def set_reg_region(self, value: str):
        self.reg_region = value
        self.reg_city = ""

    @rx.event
    def set_reg_city(self, value: str):
        self.reg_city = value

    @rx.event
    def set_reg_zip(self, value: str):
        self.reg_zip = value[:4]

    @rx.event
    def set_reg_contact(self, value: str):
        self.reg_contact = value

    @rx.event
    def set_reg_admin(self, value: str):
        self.reg_admin = value

    @rx.event(background=True)
    async def fetch_institutions(self):
        """Loads all institutions from the database."""
        async with rx.asession() as session:
            result = await session.execute(
                text(
                    "SELECT id, institution_name, street_address, city_municipality FROM institutions ORDER BY institution_name ASC"
                )
            )
            rows = result.all()
            async with self:
                self.hei_database = [
                    {
                        "id": str(row[0]),
                        "name": row[1],
                        "address": f"{row[2]}, {row[3]}",
                    }
                    for row in rows
                ]

    @rx.event(background=True)
    async def submit_selection(self):
        async with self:
            self.is_loading = True
        if self.is_registration_mode:
            async with rx.asession() as session:
                result = await session.execute(
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
                        :framework
                    )
                    RETURNING id, institution_name, street_address, city_municipality
                    """),
                    {
                        "name": self.reg_name,
                        "admin": self.reg_admin,
                        "contact": self.reg_contact,
                        "street": self.reg_street,
                        "city": self.reg_city,
                        "region": self.reg_region,
                        "zip": self.reg_zip,
                        "framework": self.ranking_framework,
                    },
                )
                new_hei = result.first()
                await session.commit()
                if new_hei:
                    async with self:
                        self.selected_hei = {
                            "id": str(new_hei[0]),
                            "name": new_hei[1],
                            "address": f"{new_hei[2]}, {new_hei[3]}",
                        }
        async with self:
            self.is_loading = False
            hei_name = (
                self.reg_name
                if self.is_registration_mode
                else self.selected_hei["name"]
            )
            framework_full = (
                "QS Stars"
                if self.ranking_framework == "QS"
                else "Times Higher Education"
            )
            yield rx.toast(
                f"Setup complete for {hei_name} using {framework_full} framework.",
                duration=3000,
                position="top-center",
            )
            yield rx.redirect("/dashboard")