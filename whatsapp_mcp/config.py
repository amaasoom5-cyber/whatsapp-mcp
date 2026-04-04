"""
Configuration — loads credentials from environment variables or .env file.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def get_config() -> dict:
    """Return configuration dict with all required credentials."""
    config = {
        "access_token": os.getenv("META_ACCESS_TOKEN", ""),
        "waba_id": os.getenv("META_WABA_ID", ""),
        "phone_number_id": os.getenv("META_PHONE_NUMBER_ID", ""),
        "app_id": os.getenv("META_APP_ID", ""),
        "api_version": os.getenv("META_API_VERSION", "v21.0"),
    }
    return config


def validate_config(config: dict) -> None:
    """Raise ValueError if required credentials are missing."""
    if not config["access_token"]:
        raise ValueError(
            "META_ACCESS_TOKEN is required. "
            "Get it from https://developers.facebook.com/apps/"
        )
    if not config["waba_id"]:
        raise ValueError(
            "META_WABA_ID is required. "
            "Find it in your WhatsApp Business Account settings."
        )
    if not config["phone_number_id"]:
        raise ValueError(
            "META_PHONE_NUMBER_ID is required. "
            "Find it in your WhatsApp Business Account phone numbers."
        )
