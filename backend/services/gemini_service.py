import asyncio
import json

from google import genai
from google.genai import types

from models.resume_models import GeminiResumeOutput
from utils.config import GEMINI_API_KEY


MODEL_NAME = "gemini-3.6-flash"


async def generate_resume_content(
    prompt: str,
) -> GeminiResumeOutput:
    """
    Generate structured resume content using Gemini.
    """

    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set."
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    async def call_model():
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )

        return response.text

    content = await call_model()

    try:
        parsed_data = json.loads(content)

    except json.JSONDecodeError:
        clean_content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        parsed_data = json.loads(clean_content)

    return GeminiResumeOutput.model_validate(
        parsed_data
    )