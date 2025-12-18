import reflex as rx
import asyncio


class DashboardState(rx.State):
    academic_reputation: str = ""
    citations_per_faculty: str = ""
    employer_reputation: str = ""
    employment_outcomes: str = ""
    international_research_network: str = ""
    international_faculty_ratio: str = ""
    international_student_ratio: str = ""
    international_student_diversity: str = ""
    faculty_student_ratio: str = ""
    sustainability_metrics: str = ""
    uploaded_research_files: list[str] = []
    uploaded_employability_files: list[str] = []
    uploaded_global_engagement_files: list[str] = []
    uploaded_learning_experience_files: list[str] = []
    uploaded_sustainability_files: list[str] = []
    is_saving: bool = False

    @rx.var
    def progress(self) -> int:
        """Calculate completion progress based on filled fields."""
        fields = [
            self.academic_reputation,
            self.citations_per_faculty,
            self.employer_reputation,
            self.employment_outcomes,
            self.international_research_network,
            self.international_faculty_ratio,
            self.international_student_ratio,
            self.faculty_student_ratio,
            self.sustainability_metrics,
        ]
        filled_count = len([f for f in fields if f.strip() != ""])
        total_fields = 9
        return int(filled_count / total_fields * 100)

    @rx.event
    def set_academic_reputation(self, value: str):
        self.academic_reputation = value

    @rx.event
    def set_citations_per_faculty(self, value: str):
        self.citations_per_faculty = value

    @rx.event
    def set_employer_reputation(self, value: str):
        self.employer_reputation = value

    @rx.event
    def set_employment_outcomes(self, value: str):
        self.employment_outcomes = value

    @rx.event
    def set_international_research_network(self, value: str):
        self.international_research_network = value

    @rx.event
    def set_international_faculty_ratio(self, value: str):
        self.international_faculty_ratio = value

    @rx.event
    def set_international_student_ratio(self, value: str):
        self.international_student_ratio = value

    @rx.event
    def set_international_student_diversity(self, value: str):
        self.international_student_diversity = value

    @rx.event
    def set_faculty_student_ratio(self, value: str):
        self.faculty_student_ratio = value

    @rx.event
    def set_sustainability_metrics(self, value: str):
        self.sustainability_metrics = value

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

    @rx.event
    async def handle_global_engagement_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for Global Engagement section."""
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.name
            with outfile.open("wb") as file_object:
                file_object.write(upload_data)
            self.uploaded_global_engagement_files.append(file.name)

    @rx.event
    async def handle_learning_experience_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for Learning Experience section."""
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.name
            with outfile.open("wb") as file_object:
                file_object.write(upload_data)
            self.uploaded_learning_experience_files.append(file.name)

    @rx.event
    async def handle_sustainability_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for Sustainability section."""
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.name
            with outfile.open("wb") as file_object:
                file_object.write(upload_data)
            self.uploaded_sustainability_files.append(file.name)

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