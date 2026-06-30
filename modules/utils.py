from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_phone(value: Any, country_code: str = "+27") -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    digits = re.sub(r"\D", "", text)
    if not digits:
        return ""
    if digits.startswith("00"):
        digits = digits[2:]
    if digits.startswith("0"):
        digits = digits[1:]
    if not digits.startswith(country_code.replace("+", "")) and len(digits) == 9:
        digits = digits
    if len(digits) == 10:
        return f"{country_code}{digits}"
    if len(digits) == 9:
        return f"{country_code}{digits}"
    return f"{country_code}{digits}" if not digits.startswith(country_code.replace("+", "")) else f"+{digits}"


def normalize_website(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    if text.startswith(("http://", "https://")):
        return text
    return f"https://{text}"


def parse_optional_json(value: Any) -> Any:
    if value in (None, ""):
        return None
    if isinstance(value, (dict, list)):
        return value
    text = str(value).strip()
    if not text:
        return None
    if text.startswith("[") or text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    return text


def safe_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()

