import reflex as rx
from typing import TypedDict, Optional
import asyncio
from sqlalchemy import text
import logging


class HEI(TypedDict):
    id: str
    name: str
    address: str
    type: str
    admin_name: str
    street: str
    city: str


class HEIState(rx.State):
    """Manages the selection and registration of Higher Education Institutions (HEIs).
    This state allows users to search for existing schools or register new ones into the system.
    """

    hei_database: list[HEI] = []
    search_results: list[HEI] = []
    search_query: str = ""
    _search_cache: dict[str, list[HEI]] = {}
    _search_cache_max_size: int = 50
    _search_version: int = 0
    _last_search_query: str = ""
    selected_hei_id: str = ""
    selected_hei: Optional[HEI] = None
    ranking_framework: str = ""
    is_registration_mode: bool = False
    is_searching: bool = False
    is_dropdown_open: bool = False
    reg_name: str = ""
    reg_street: str = ""
    reg_region: str = ""
    reg_city: str = ""
    reg_zip: str = ""
    reg_contact: str = ""
    reg_admin: str = ""
    is_loading: bool = False
    is_fetching: bool = False
    show_preliminary_notice: bool = False
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
            "Malolos",
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
        "Region IV-B (MIMAROPA)": ["Puerto Princesa", "Calapan"],
        "Region V (Bicol Region)": [
            "Legazpi",
            "Ligao",
            "Tabaco",
            "Iriga",
            "Naga City",
            "Masbate City",
            "Sorsogon City",
        ],
        "Region VI (Western Visayas)": [
            "Iloilo City",
            "Passi",
            "Bacolod",
            "Bago",
            "Cadiz",
            "Escalante",
            "Himamaylan",
            "Kabankalan",
            "La Carlota",
            "Sagay",
            "San Carlos City (Negros Occ.)",
            "Silay",
            "Sipalay",
            "Talisay",
            "Victorias",
            "Roxas City",
        ],
        "Region VII (Central Visayas)": [
            "Cebu City",
            "Mandaue",
            "Lapu-Lapu",
            "Bogo",
            "Carcar",
            "Danao",
            "Naga",
            "Talisay",
            "Toledo",
            "Tagbilaran",
            "Bais",
            "Bayawan",
            "Canlaon",
            "Dumaguete",
            "Guihulngan",
            "Tanjay",
        ],
        "Region VIII (Eastern Visayas)": [
            "Tacloban",
            "Ormoc",
            "Baybay",
            "Maasin",
            "Calbayog",
            "Catbalogan",
            "Borongan",
        ],
        "Region IX (Zamboanga Peninsula)": [
            "Zamboanga City",
            "Isabela City",
            "Dapitan",
            "Dipolog",
            "Pagadian",
        ],
        "Region X (Northern Mindanao)": [
            "Cagayan de Oro",
            "El Salvador",
            "Gingoog",
            "Iligan",
            "Malaybalay",
            "Valencia",
            "Oroquieta",
            "Ozamiz",
            "Tangub",
        ],
        "Region XI (Davao Region)": [
            "Davao City",
            "Panabo",
            "Samal",
            "Tagum",
            "Digos",
            "Mati",
        ],
        "Region XII (SOCCSKSARGEN)": [
            "General Santos",
            "Koronadal",
            "Kidapawan",
            "Tacurong",
        ],
        "Region XIII (Caraga)": [
            "Butuan",
            "Cabadbaran",
            "Bayugan",
            "Surigao City",
            "Bislig",
            "Tandag",
        ],
        "BARMM (Bangsamoro Autonomous Region in Muslim Mindanao)": [
            "Cotabato City",
            "Marawi",
            "Lamitan",
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
        sanitized_query = query.strip()
        self.search_query = sanitized_query
        if len(sanitized_query) >= 2:
            self.is_dropdown_open = True
            return HEIState.perform_search
        else:
            self.is_dropdown_open = False
            self.search_results = []
            self.is_searching = False

    @rx.event
    def clear_search(self):
        self.search_query = ""
        self.selected_hei = None
        self.selected_hei_id = ""
        self.search_results = []
        self.is_dropdown_open = False
        self.ranking_framework = ""

    @rx.event(background=True)
    async def perform_search(self):
        """Search institutions in the database based on query with caching and versioning."""
        async with self:
            sanitized_query = self.search_query.strip()
            if not sanitized_query or len(sanitized_query) < 2:
                self.is_searching = False
                self.search_results = []
                return
            if sanitized_query == self._last_search_query:
                return
            if sanitized_query in self._search_cache:
                self.search_results = self._search_cache[sanitized_query]
                self.is_searching = False
                self._last_search_query = sanitized_query
                return
            self.is_searching = True
            self._search_version += 1
            current_version = self._search_version
        query_text = f"%{sanitized_query}%"
        async with rx.asession() as session:
            try:
                result = await session.execute(
                    text("""
                        SELECT id, institution_name, street_address, city_municipality, 'Private', admin_name 
                        FROM institutions 
                        WHERE institution_name ILIKE :query 
                        ORDER BY institution_name ASC
                        LIMIT 8
                    """),
                    {"query": query_text},
                )
                rows = result.all()
                results = [
                    {
                        "id": str(row[0]),
                        "name": row[1],
                        "address": f"{row[2]}, {row[3]}",
                        "type": row[4],
                        "street": row[2],
                        "city": row[3],
                        "admin_name": row[5] if row[5] else "Not Assigned",
                    }
                    for row in rows
                ]
            except Exception as e:
                logging.exception(f"Search error: {e}")
                results = []
        async with self:
            if self._search_version == current_version:
                self.search_results = results
                self.is_searching = False
                self._last_search_query = sanitized_query
                self._search_cache[sanitized_query] = results
                if len(self._search_cache) > self._search_cache_max_size:
                    first_key = next(iter(self._search_cache))
                    self._search_cache.pop(first_key)

    @rx.event
    def set_is_dropdown_open(self, value: bool):
        self.is_dropdown_open = value

    @rx.event
    def select_hei(self, hei: HEI):
        """Optimistic UI update for instant selection feedback."""
        self.selected_hei = hei
        self.selected_hei_id = hei["id"]
        self.search_query = hei["name"]
        self.is_dropdown_open = False
        self.is_registration_mode = False
        if not self.ranking_framework:
            self.ranking_framework = "QS"

    @rx.event
    def deselect_hei(self):
        self.selected_hei = None
        self.selected_hei_id = ""
        self.search_query = ""
        self.ranking_framework = ""
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
        """Loads all institutions from the database. Kept for Institutions page."""
        async with self:
            self.is_fetching = True
        async with rx.asession() as session:
            result = await session.execute(
                text(
                    "SELECT id, institution_name, street_address, city_municipality, 'Private', admin_name FROM institutions ORDER BY institution_name ASC"
                )
            )
            rows = result.all()
            async with self:
                self.hei_database = [
                    {
                        "id": str(row[0]),
                        "name": row[1],
                        "address": f"{row[2]}, {row[3]}",
                        "type": row[4],
                        "street": row[2],
                        "city": row[3],
                        "admin_name": row[5] if row[5] else "Not Assigned",
                    }
                    for row in rows
                ]
                self.is_fetching = False

    @rx.event(background=True)
    async def submit_selection(self):
        """Batched state updates to minimize synchronization overhead during transition."""
        async with self:
            self.is_loading = True
            reg_mode = self.is_registration_mode
            reg_data = {
                "name": self.reg_name,
                "admin": self.reg_admin,
                "contact": self.reg_contact,
                "street": self.reg_street,
                "city": self.reg_city,
                "region": self.reg_region,
                "zip": self.reg_zip,
                "framework": self.ranking_framework,
            }
        if reg_mode:
            async with rx.asession() as session:
                result = await session.execute(
                    text("""
                    INSERT INTO institutions (
                        institution_name, admin_name, contact_number, 
                        street_address, city_municipality, region, 
                        zip_code, ranking_framework
                    )
                    VALUES (
                        :name, :admin, :contact, :street, :city, :region, :zip, :framework
                    )
                    RETURNING id, institution_name, street_address, city_municipality
                    """),
                    reg_data,
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
            self.show_preliminary_notice = True

    @rx.event
    def acknowledge_and_proceed(self):
        self.show_preliminary_notice = False
        hei_name = (
            self.reg_name if self.is_registration_mode else self.selected_hei["name"]
        )
        framework_full = (
            "QS Stars" if self.ranking_framework == "QS" else "Times Higher Education"
        )
        yield rx.toast(
            f"Setup complete for {hei_name} using {framework_full} framework.",
            duration=3000,
            position="top-center",
        )
        yield rx.redirect("/dashboard")