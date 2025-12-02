import reflex as rx
import asyncio


class DashboardState(rx.State):
    research_output: str = ""
    citations: str = ""
    grants: str = ""
    employment_rate: str = ""
    employer_reputation: str = ""
    uploaded_research_files: list[str] = []
    uploaded_employability_files: list[str] = []
    is_saving: bool = False

    @rx.var
    def progress(self) -> int:
        """Calculate completion progress based on filled fields."""
        fields = [
            self.research_output,
            self.citations,
            self.grants,
            self.employment_rate,
            self.employer_reputation,
        ]
        filled_count = len([f for f in fields if f.strip() != ""])
        total_fields = 5
        return int(filled_count / total_fields * 100)

    @rx.event
    def set_research_output(self, value: str):
        self.research_output = value

    @rx.event
    def set_citations(self, value: str):
        self.citations = value

    @rx.event
    def set_grants(self, value: str):
        self.grants = value

    @rx.event
    def set_employment_rate(self, value: str):
        self.employment_rate = value

    @rx.event
    def set_employer_reputation(self, value: str):
        self.employer_reputation = value

    @rx.event
    async def handle_research_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for Research section."""
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.name
            with outfile.open("wb") as file_object:
                file_object.write(upload_data)
            self.uploaded_research_files.append(file.name)

    @rx.event
    async def handle_employability_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for Employability section."""
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.name
            with outfile.open("wb") as file_object:
                file_object.write(upload_data)
            self.uploaded_employability_files.append(file.name)

    @rx.event(background=True)
    async def save_progress(self):
        """Simulate saving data to backend."""
        async with self:
            self.is_saving = True
        await asyncio.sleep(1.5)
        async with self:
            self.is_saving = False
            yield rx.toast(
                "Assessment data saved successfully.",
                duration=3000,
                position="bottom-right",
                close_button=True,
            )