import asyncio
import json
import os
import time
from typing import Optional

from prompts.resume_prompt import build_resume_prompt

from services.extraction_service import (
    extract_text,
    extract_urls,
)

from services.gemini_service import (
    generate_resume_content,
)

from services.fact_checker_service import (
    validate_resume_facts,
)

from services.pdf_service import (
    generate_pdf,
    render_resume_html,
)


# SSE MESSAGE

def create_sse_message(
    data: dict,
) -> str:
    """
    Convert a dictionary into a
    Server-Sent Events message.
    """

    return (
        f"data: {json.dumps(data)}\n\n"
    )


# RESUME DATA → TEXT

def resume_data_to_text(
    resume_data: dict,
) -> str:
    """
    Convert the structured Gemini resume output
    into plain text for fact validation.

    The fact checker compares this representation
    against the original resume text.
    """

    parts = []

    # Basic Information

    parts.append(
        f"Name: {resume_data.get('name', '')}"
    )

    parts.append(
        f"Phone: {resume_data.get('phone', '')}"
    )

    parts.append(
        f"Email: {resume_data.get('email', '')}"
    )

    parts.append(
        f"Summary: {resume_data.get('summary', '')}"
    )

    # Education

    for education in resume_data.get(
        "education",
        [],
    ):

        parts.append(
            "\nEducation:"
        )

        parts.append(
            f"School: "
            f"{education.get('school', '')}"
        )

        parts.append(
            f"Degree: "
            f"{education.get('degree', '')}"
        )

        parts.append(
            f"Dates: "
            f"{education.get('dates', '')}"
        )

        parts.append(
            f"GPA: "
            f"{education.get('gpa', '')}"
        )

    # Skills

    for skill_group in resume_data.get(
        "skills",
        [],
    ):

        category = skill_group.get(
            "category",
            "",
        )

        items = skill_group.get(
            "items",
            [],
        )

        parts.append(
            f"\nSkills - {category}: "
            + ", ".join(items)
        )

    # Experience

    for experience in resume_data.get(
        "experience",
        [],
    ):

        parts.append(
            "\nExperience:"
        )

        parts.append(
            f"Company: "
            f"{experience.get('company', '')}"
        )

        parts.append(
            f"Role: "
            f"{experience.get('role', '')}"
        )

        parts.append(
            f"Dates: "
            f"{experience.get('dates', '')}"
        )

        for point in experience.get(
            "points",
            [],
        ):

            parts.append(
                f"- {point}"
            )

    # Projects

    for project in resume_data.get(
        "projects",
        [],
    ):

        parts.append(
            "\nProject:"
        )

        parts.append(
            f"Name: "
            f"{project.get('name', '')}"
        )

        parts.append(
            f"Dates: "
            f"{project.get('dates', '')}"
        )

        for point in project.get(
            "points",
            [],
        ):

            parts.append(
                f"- {point}"
            )

    # Achievements

    for achievement in resume_data.get(
        "achievements",
        [],
    ):

        parts.append(
            f"\nAchievement: "
            f"{achievement}"
        )

    return "\n".join(parts)


# CORRECTION PROMPT

def build_fact_correction_prompt(
    original_resume: str,
    jd: str,
    generated_resume: dict,
    validation_result: dict,
) -> str:
    """
    Build a correction prompt after the fact checker
    detects unsupported claims.

    The correction is limited to fixing factual issues.
    """

    issues = validation_result.get(
        "issues",
        [],
    )

    return f"""
You are correcting a tailored resume.

The ORIGINAL RESUME is the only source of truth.

The generated resume contains one or more factual
claims that were identified as unsupported.

Your task is to correct ONLY those factual problems.

DO NOT:
- invent information
- add new technologies
- add new companies
- add new projects
- add new metrics
- change dates
- change job titles
- add experience from the job description
- create achievements
- create certifications

You MAY:
- rewrite wording
- remove unsupported claims
- restore the original factual value
- keep JD-relevant information when it is supported
- improve clarity without changing facts


ORIGINAL RESUME

{original_resume}


JOB DESCRIPTION


{jd}

CURRENT GENERATED RESUME

{json.dumps(generated_resume, indent=2)}

FACT CHECK ISSUES

{json.dumps(issues, indent=2)}

OUTPUT

Return ONLY valid JSON.

Return the exact same resume schema as the current
generated resume.

Do not return markdown.

Do not explain your changes.

The corrected resume must contain ONLY information
supported by the original resume.
"""


# GENERATION PIPELINE

async def generation_pipeline(
    file_path: str,
    jd: str,
    target_role: Optional[str] = None,
    github_url: Optional[str] = None,
    linkedin_url: Optional[str] = None,
):
    """
    Complete resume generation pipeline.

    Flow:

        1. Validate input
        2. Extract resume text
        3. Extract original resume URLs
        4. Build Gemini prompt
        5. Generate tailored resume
        6. Fact-check generated resume
        7. Correct once if validation fails
        8. Restore original contact URLs
        9. Render existing HTML template
        10. Generate one-page PDF
        11. Return download URL
    """

    try:

        #  VALIDATE INPUT

        yield create_sse_message({
            "step": "Validating Input",
            "progress": 10,
        })

        await asyncio.sleep(0.5)

        if not os.path.exists(
            file_path
        ):

            yield create_sse_message({
                "error": (
                    "Uploaded resume file "
                    "was not found."
                )
            })

            return

        if not jd or not jd.strip():

            yield create_sse_message({
                "error": (
                    "Job description is required."
                )
            })

            return

        # — EXTRACT RESUME TEXT

        yield create_sse_message({
            "step": "Extracting Resume Text",
            "progress": 25,
        })

        resume_text = extract_text(
            file_path
        )

        if not resume_text.strip():

            yield create_sse_message({
                "error": (
                    "Could not extract text "
                    "from the uploaded resume."
                )
            })

            return

        #  EXTRACT ORIGINAL URLS


        original_urls = extract_urls(
            file_path
        )


        # ANALYZE JD / BUILD PROMPT

        yield create_sse_message({
            "step": (
                "Analyzing Job Description"
            ),
            "progress": 40,
        })

        prompt = build_resume_prompt(
            resume_text=resume_text,
            jd=jd,
            target_role=target_role,
            github_url=github_url,
            linkedin_url=linkedin_url,
        )

        # ====================================================
        # STEP 5 — GENERATE TAILORED RESUME
        # ====================================================

        yield create_sse_message({
            "step": (
                "Generating Tailored Resume Content"
            ),
            "progress": 75,
        })

        resume_data = (
            await generate_resume_content(
                prompt
            )
        )

        parsed_data = (
            resume_data.model_dump()
        )

        # ====================================================
        # STEP 6 — FACT CHECK
        # ====================================================

        yield create_sse_message({
            "step": (
                "Validating Resume Facts"
            ),
            "progress": 82,
        })

        generated_resume_text = (
            resume_data_to_text(
                parsed_data
            )
        )

        fact_check = (
            await validate_resume_facts(
                original_resume=resume_text,
                generated_resume=generated_resume_text,
            )
        )

        # STEP 7 — ONE CORRECTION RETRY

        if not fact_check.get(
            "valid",
            False,
        ):




            yield create_sse_message({
                "step": (
                    "Correcting Unsupported Claims"
                ),
                "progress": 86,
            })

            correction_prompt = (
                build_fact_correction_prompt(
                    original_resume=resume_text,
                    jd=jd,
                    generated_resume=parsed_data,
                    validation_result=fact_check,
                )
            )

            corrected_resume = (
                await generate_resume_content(
                    correction_prompt
                )
            )

            parsed_data = (
                corrected_resume.model_dump()
            )

            # ------------------------------------------------
            # Validate corrected resume
            # ------------------------------------------------

            corrected_resume_text = (
                resume_data_to_text(
                    parsed_data
                )
            )

            second_fact_check = (
                await validate_resume_facts(
                    original_resume=resume_text,
                    generated_resume=corrected_resume_text,
                )
            )




        

            # If still invalid, stop the pipeline.

            if not second_fact_check.get(
                "valid",
                False,
            ):

                yield create_sse_message({
                    "error": (
                        "The generated resume "
                        "contains unsupported factual "
                        "claims and could not be "
                        "validated safely."
                    ),
                    "validation_issues": (
                        second_fact_check.get(
                            "issues",
                            [],
                        )
                    ),
                })

                return

        # ====================================================
        # STEP 8 — RESTORE ORIGINAL URLS
        # ====================================================

        #
        # The uploaded resume is the source of truth
        # for contact links.
        #
        # Gemini is never trusted to modify them.
        #

        parsed_data["github"] = (
            original_urls.get(
                "github",
                "",
            )
        )

        parsed_data["linkedin"] = (
            original_urls.get(
                "linkedin",
                "",
            )
        )

        parsed_data["portfolio"] = (
            original_urls.get(
                "portfolio",
                "",
            )
        )

        
        # RENDER HTML
    

        yield create_sse_message({
            "step": (
                "Formatting Professional PDF"
            ),
            "progress": 90,
        })

        html_content = (
            render_resume_html(
                parsed_data
            )
        )

        if not html_content or not html_content.strip():

            yield create_sse_message({
                "error": (
                    "Generated resume HTML is empty."
                )
            })

            return

        # ====================================================
        # STEP 10 — GENERATE PDF
        # ====================================================

        output_filename = (
            "tailored_resume_"
            f"{int(time.time())}.pdf"
        )

        output_path = (
            await generate_pdf(
                html_content=html_content,
                output_filename=output_filename,
            )
        )

        # ====================================================
        # STEP 11 — VERIFY PDF
        # ====================================================

        if not os.path.exists(
            output_path
        ):

            yield create_sse_message({
                "error": (
                    "PDF generation failed."
                )
            })

            return

        # ====================================================
        # STEP 12 — FINISHED
        # ====================================================

        yield create_sse_message({
            "step": "Finished",
            "progress": 100,
            "download_url": (
                f"/api/download/"
                f"{output_filename}"
            ),
        })

    except Exception as e:

        yield create_sse_message({
            "error": str(e)
        })