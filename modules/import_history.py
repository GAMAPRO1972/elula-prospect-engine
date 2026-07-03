"""
modules/import_history.py

Persistent import history ledger for production-safe Elula BizHub sync.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
IMPORT_HISTORY_PATH = DATA_DIR / "import_history.json"
LEDGER_VERSION = 1


def _blank_ledger() -> dict[str, Any]:
    return {
        "version": LEDGER_VERSION,
        "imports": {},
    }


def _normalise_website(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""

    if "://" not in text:
        text = f"https://{text}"

    parsed = urlparse(text)
    host = parsed.netloc or parsed.path
    host = host.split("@")[-1].split(":")[0]
    host = host.removeprefix("www.").strip(".")

    return host


def _normalise_phone(value: Any) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if not digits:
        return ""

    if digits.startswith("00"):
        digits = digits[2:]

    if digits.startswith("0") and len(digits) == 10:
        digits = "27" + digits[1:]

    return digits


def _normalise_company_name(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""

    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    words = [
        word
        for word in text.split()
        if word not in {"pty", "ltd", "limited", "cc", "inc", "co", "company"}
    ]

    return " ".join(words)


def build_match_key(prospect: dict[str, Any]) -> tuple[str, str, str]:
    """
    Build the stable import key using website, then phone, then company name.
    """

    website = _normalise_website(prospect.get("website"))
    if website:
        return ("website", website, f"website:{website}")

    phone = _normalise_phone(prospect.get("phone"))
    if phone:
        return ("phone", phone, f"phone:{phone}")

    company_name = _normalise_company_name(prospect.get("company_name"))
    if company_name:
        return ("company_name", company_name, f"company_name:{company_name}")

    raise ValueError("Prospect has no website, phone, or company name for import history matching.")


def load_import_history() -> dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not IMPORT_HISTORY_PATH.exists() or IMPORT_HISTORY_PATH.stat().st_size == 0:
        ledger = _blank_ledger()
        save_import_history(ledger)
        return ledger

    with IMPORT_HISTORY_PATH.open("r", encoding="utf-8") as file:
        ledger = json.load(file)

    if not isinstance(ledger, dict):
        raise ValueError("Import history ledger must contain a JSON object.")

    imports = ledger.setdefault("imports", {})
    if not isinstance(imports, dict):
        raise ValueError("Import history ledger 'imports' value must be a JSON object.")

    ledger["version"] = ledger.get("version") or LEDGER_VERSION

    return ledger


def save_import_history(ledger: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    temp_path = IMPORT_HISTORY_PATH.with_suffix(".tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(ledger, file, indent=2, sort_keys=True)
        file.write("\n")

    temp_path.replace(IMPORT_HISTORY_PATH)


def find_import(ledger: dict[str, Any], match_key: str) -> dict[str, Any] | None:
    record = ledger.get("imports", {}).get(match_key)
    return record if isinstance(record, dict) else None


def record_import(
    ledger: dict[str, Any],
    prospect: dict[str, Any],
    campaign,
    match_type: str,
    match_value: str,
    match_key: str,
    contact_id: str,
    opportunity_id: str,
    task_id: str | None,
) -> dict[str, Any]:
    imports = ledger.setdefault("imports", {})

    record = {
        "match_type": match_type,
        "match_value": match_value,
        "company_name": prospect.get("company_name", ""),
        "website": prospect.get("website", ""),
        "phone": prospect.get("phone", ""),
        "email": prospect.get("email", ""),
        "campaign_id": campaign.config.get("campaign_id", ""),
        "campaign_name": campaign.config.get("campaign_name", getattr(campaign, "name", "")),
        "industry": campaign.config.get("industry", ""),
        "pipeline": campaign.config.get("pipeline", ""),
        "contact_id": contact_id,
        "opportunity_id": opportunity_id,
        "task_id": task_id,
        "imported_at": datetime.now(timezone.utc).isoformat(),
    }

    imports[match_key] = record
    save_import_history(ledger)

    return record
