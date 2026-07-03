"""
integrations/google_business/parser.py

Safe parsing helpers for Google Business Profile-like records.
"""

from __future__ import annotations

import json
from typing import Any

from integrations.google_business.models import GoogleBusinessProfile


def _text(value: Any) -> str:
    text = str(value or "").strip()
    if text in {"{}", "[]", "null", "None"}:
        return ""
    return text


def _first_value(record: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = _text(record.get(key))
        if value:
            return value
    return ""


def _format_address(value: Any) -> str:
    text = _text(value)
    if not text:
        return ""

    if not text.startswith("{"):
        return text

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return text

    if not isinstance(data, dict):
        return text

    parts = [
        data.get("street"),
        data.get("borough"),
        data.get("city"),
        data.get("postal_code"),
        data.get("state"),
        data.get("country"),
    ]

    return ", ".join(_text(part) for part in parts if _text(part))


def _float_or_none(value: Any) -> float | None:
    text = _text(value).replace(",", ".")
    if not text:
        return None

    try:
        return float(text)
    except ValueError:
        return None


def _int_or_none(value: Any) -> int | None:
    text = _text(value).replace(",", "")
    if not text:
        return None

    digits = "".join(character for character in text if character.isdigit())
    if not digits:
        return None

    return int(digits)


def parse_google_business_profile(record: dict[str, Any]) -> GoogleBusinessProfile:
    """
    Parse a prospect or raw scraper row into a safe profile model.
    """

    profile = GoogleBusinessProfile(
        company_name=_first_value(record, ["company_name", "title", "name"]),
        category=_first_value(record, ["category", "business_category", "type"]),
        rating=_float_or_none(
            _first_value(record, ["rating", "review_rating", "reviews_rating"])
        ),
        review_count=_int_or_none(
            _first_value(record, ["review_count", "reviews", "reviews_count"])
        ),
        phone=_first_value(record, ["phone", "phone_number", "telephone"]),
        website=_first_value(record, ["website", "url", "site"]),
        address=_format_address(
            _first_value(record, ["address", "complete_address", "full_address"])
        ),
        opening_hours=_first_value(
            record,
            ["opening_hours", "open_hours", "hours", "working_hours", "business_hours"],
        ),
        business_status=_first_value(
            record,
            ["business_status", "status", "place_status"],
        ),
    )

    if not profile.company_name:
        profile.warnings.append("Missing company name")
    if not profile.category:
        profile.warnings.append("Missing category")
    if profile.rating is None:
        profile.warnings.append("Missing rating")
    if profile.review_count is None:
        profile.warnings.append("Missing review count")
    if not profile.phone:
        profile.warnings.append("Missing phone")
    if not profile.website:
        profile.warnings.append("Missing website")
    if not profile.address:
        profile.warnings.append("Missing address")
    if not profile.opening_hours:
        profile.warnings.append("Missing opening hours")
    if not profile.business_status:
        profile.warnings.append("Missing business status")

    return profile
