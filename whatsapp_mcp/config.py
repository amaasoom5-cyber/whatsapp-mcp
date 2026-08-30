"""
Configuration — loads WATI credentials from environment variables or .env file.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def get_config() -> dict:
    """Return configuration dict with all required WATI credentials."""

    token = os.getenv("WATI_API_TOKEN", "").strip()
    endpoint = os.getenv("WATI_API_ENDPOINT", "").strip().rstrip("/")

    # Makes it safe if the token was accidentally saved as "Bearer eyJ..."
    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    return {
        "wati_api_token": token,
        "wati_api_endpoint": endpoint,
    }


def validate_config(config: dict) -> None:
    """Raise ValueError if required WATI credentials are missing."""

    if not config["wati_api_token"]:
        raise ValueError(
            "WATI_API_TOKEN is required. "
            "Add it to your environment variables."
        )

    if not config["wati_api_endpoint"]:
        raise ValueError(
            "WATI_API_ENDPOINT is required. "
            "Example: https://eu-api.wati.io/1120364"
        )

    if not config["wati_api_endpoint"].startswith(("https://", "http://")):
        raise ValueError("WATI_API_ENDPOINT must be a valid URL.")
