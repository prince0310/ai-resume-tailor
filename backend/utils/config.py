import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()



# Gemini Configuration

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def validate_config() -> None:
    """
    Validate required backend configuration.
    """

    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set."
        )