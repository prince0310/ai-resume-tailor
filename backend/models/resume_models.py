from pydantic import BaseModel, Field


class GeminiResumeOutput(BaseModel):
    name: str = Field(description="Full Name")

    phone: str = Field(description="Phone Number")

    email: str = Field(description="Email Address")

    portfolio: str = Field(
        description="Portfolio Website URL"
    )

    linkedin: str = Field(
        description="LinkedIn URL"
    )

    github: str = Field(
        description="GitHub URL"
    )

    summary: str = Field(
        description="Concise professional summary"
    )

    education: list[dict] = Field(
        description="List with school, degree, dates, gpa"
    )

    skills: list[dict] = Field(
        description="List with category and items (strings)"
    )

    experience: list[dict] = Field(
        description=(
            "List of dicts with: "
            "company, role, dates, points (list)"
        )
    )

    projects: list[dict] = Field(
        description=(
            "List of dicts with: "
            "name, dates, points (list)"
        )
    )

    achievements: list[str] = Field(
        description="List of specific achievements or awards"
    )