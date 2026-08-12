import asyncio
import json

from google import genai
from google.genai import types

from utils.config import GEMINI_API_KEY


MODEL_NAME = "gemini-3.6-flash"


# ============================================================
# Fact Checking Prompt
# ============================================================

def build_fact_check_prompt(
    original_resume: str,
    generated_resume: str,
) -> str:
    """
    Build a strict fact-validation prompt.

    The original resume is the source of truth.
    """

    return f"""
You are a strict resume fact-checking system.

Your job is NOT to improve the resume.

Your job is ONLY to determine whether the generated resume
contains factual claims that are unsupported by the original
resume.

============================================================
SOURCE OF TRUTH
============================================================

The ORIGINAL RESUME is the ONLY source of truth.

The GENERATED RESUME must not introduce unsupported facts.

A rewritten sentence is acceptable if it preserves the
meaning of information present in the original resume.

============================================================
CHECK THESE CAREFULLY
============================================================

Check for unsupported changes involving:

1. Company names
2. Job titles
3. Employment dates
4. Education
5. Degrees
6. GPA
7. Projects
8. Technologies
9. Frameworks
10. Programming languages
11. Responsibilities
12. Achievements
13. Patents
14. Publications
15. Metrics
16. Percentages
17. Accuracy values
18. Dataset sizes
19. Performance numbers
20. FPS
21. Latency
22. Years of experience
23. Quantified business impact
24. Certifications
25. Any other factual claim

============================================================
IMPORTANT RULES
============================================================

A claim is VALID if:

- It is explicitly supported by the original resume.
- OR it is a faithful paraphrase of something in the
  original resume.

A claim is INVALID if:

- It introduces a new technology.
- It introduces a new responsibility.
- It introduces a new project.
- It changes a metric.
- It changes a date.
- It changes a company.
- It changes a job title.
- It introduces a new achievement.
- It introduces unsupported experience.
- It exaggerates an existing claim.
- It converts an implied possibility into a factual claim
  that is not supported.

Do NOT mark a sentence invalid merely because its wording
is different.

============================================================
METRIC RULE
============================================================

Metrics require especially strict checking.

For example:

Original:
"Achieved 90% detection accuracy."

Generated:
"Achieved 95% detection accuracy."

INVALID.

Original:
"Achieved 90% detection accuracy."

Generated:
"Achieved 90% detection accuracy."

VALID.

Original:
"Reduced inference latency by 20%."

Generated:
"Improved inference latency by 20%."

VALID if the meaning remains equivalent.

============================================================
TECHNOLOGY RULE
============================================================

If the generated resume says:

"Built systems using Kubernetes."

but Kubernetes does not appear in the original resume:

INVALID.

Do NOT assume that the candidate knows a technology merely
because it appears in the job description.

============================================================
JOB DESCRIPTION IS NOT EVIDENCE
============================================================

The job description must NEVER be treated as evidence that
the candidate has a particular skill.

Only the ORIGINAL RESUME can establish candidate experience.

============================================================
ORIGINAL RESUME
============================================================

{original_resume}

============================================================
GENERATED RESUME
============================================================

{generated_resume}

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "valid": true,
    "issues": [],
    "checked": {{
        "companies": true,
        "job_titles": true,
        "dates": true,
        "education": true,
        "technologies": true,
        "projects": true,
        "achievements": true,
        "metrics": true,
        "experience_claims": true
    }}
}}

If there are unsupported claims:

{{
    "valid": false,
    "issues": [
        {{
            "type": "unsupported_metric",
            "generated_claim": "95% detection accuracy",
            "source_evidence": "90% detection accuracy",
            "explanation": "The generated resume changed the accuracy from 90% to 95%."
        }}
    ],
    "checked": {{
        "companies": true,
        "job_titles": true,
        "dates": true,
        "education": true,
        "technologies": true,
        "projects": true,
        "achievements": true,
        "metrics": false,
        "experience_claims": true
    }}
}}

Keep the issues concise.

Do not rewrite the resume.

Do not provide recommendations.

Only validate factual consistency.
"""


# ============================================================
# Fact Checker
# ============================================================

async def validate_resume_facts(
    original_resume: str,
    generated_resume: str,
) -> dict:
    """
    Validate the generated resume against the original resume.

    Returns a dictionary containing:

        valid
        issues
        checked
    """

    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set."
        )

    if not original_resume.strip():
        raise ValueError(
            "Original resume text is empty."
        )

    if not generated_resume.strip():
        raise ValueError(
            "Generated resume content is empty."
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    prompt = build_fact_check_prompt(
        original_resume=original_resume,
        generated_resume=generated_resume,
    )

    async def call_model():

        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        return response.text

    try:

        content = await call_model()

        if not content:
            raise ValueError(
                "Gemini returned an empty fact-check response."
            )

        try:

            result = json.loads(
                content
            )

        except json.JSONDecodeError:

            clean_content = (
                content
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            result = json.loads(
                clean_content
            )

        # ------------------------------------------
        # Basic response validation
        # ------------------------------------------

        if not isinstance(
            result,
            dict,
        ):
            raise ValueError(
                "Fact checker returned invalid JSON."
            )

        if "valid" not in result:
            raise ValueError(
                "Fact checker response is missing 'valid'."
            )

        if "issues" not in result:
            result["issues"] = []

        if "checked" not in result:
            result["checked"] = {}

        return result

    finally:

        # The current google-genai client may expose
        # different async cleanup behavior depending on
        # SDK version. We intentionally don't call
        # client.aclose() here because the model request
        # itself is executed synchronously inside a worker
        # thread.
        pass