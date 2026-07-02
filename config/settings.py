"""
config/settings.py

Central settings loader for the Elula Prospect Engine.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"

load_dotenv(PROJECT_ROOT / ".env")


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)

    if value in (None, ""):
        return default

    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer.") from exc


def _load_business_settings() -> dict[str, Any]:
    path = CONFIG_DIR / "settings.json"

    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


@dataclass(frozen=True)
class Settings:
    GHL_API_KEY: str
    GHL_LOCATION_ID: str
    GHL_BASE_URL: str
    GHL_API_VERSION: str
    GHL_TIMEOUT_SECONDS: int
    GHL_LOG_LEVEL: str

    country: str
    phone_country_code: str
    default_source: str
    default_status: str
    default_primary_product: str
    remove_duplicates: bool
    clean_phone_numbers: bool
    clean_websites: bool
    validate_emails: bool
    create_processing_report: bool
    output_filename: str

    max_retries: int
    retry_backoff: int
    log_file: str

    @property
    def ghl_api_key(self) -> str:
        return self.GHL_API_KEY

    @property
    def ghl_location_id(self) -> str:
        return self.GHL_LOCATION_ID

    @property
    def ghl_base_url(self) -> str:
        return self.GHL_BASE_URL

    @property
    def ghl_api_version(self) -> str:
        return self.GHL_API_VERSION

    @property
    def request_timeout(self) -> int:
        return self.GHL_TIMEOUT_SECONDS

    @property
    def connect_timeout(self) -> int:
        return self.GHL_TIMEOUT_SECONDS

    @property
    def log_level(self) -> str:
        return self.GHL_LOG_LEVEL


def load_settings() -> Settings:
    business = _load_business_settings()

    return Settings(
        GHL_API_KEY=os.getenv("GHL_API_KEY", ""),
        GHL_LOCATION_ID=os.getenv("GHL_LOCATION_ID", ""),
        GHL_BASE_URL=os.getenv(
            "GHL_BASE_URL",
            "https://services.leadconnectorhq.com",
        ),
        GHL_API_VERSION=os.getenv("GHL_API_VERSION", "2021-07-28"),
        GHL_TIMEOUT_SECONDS=_get_int("GHL_TIMEOUT_SECONDS", 30),
        GHL_LOG_LEVEL=os.getenv("GHL_LOG_LEVEL", "INFO"),
        country=business.get("country", "South Africa"),
        phone_country_code=business.get("phone_country_code", "+27"),
        default_source=business.get("default_source", "Google Maps"),
        default_status=business.get("default_status", "New"),
        default_primary_product=business.get(
            "default_primary_product",
            "Elula BizHub",
        ),
        remove_duplicates=business.get("remove_duplicates", True),
        clean_phone_numbers=business.get("clean_phone_numbers", True),
        clean_websites=business.get("clean_websites", True),
        validate_emails=business.get("validate_emails", True),
        create_processing_report=business.get("create_processing_report", True),
        output_filename=business.get("output_filename", "ElulaBizHub_Import.csv"),
        max_retries=_get_int("GHL_MAX_RETRIES", 3),
        retry_backoff=_get_int("GHL_RETRY_BACKOFF", 2),
        log_file=os.getenv("GHL_LOG_FILE", "logs/ghl.log"),
    )


def validate_ghl_settings() -> None:
    missing = []

    if not settings.GHL_API_KEY:
        missing.append("GHL_API_KEY")

    if not settings.GHL_LOCATION_ID:
        missing.append("GHL_LOCATION_ID")

    if missing:
        raise ValueError(
            "Missing required GoHighLevel environment variables: "
            + ", ".join(missing)
        )


settings = load_settings()
