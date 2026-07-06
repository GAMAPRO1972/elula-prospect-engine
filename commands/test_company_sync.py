"""
commands/test_company_sync.py

Fast diagnostic command for the Elula BizHub Business API payload.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from config.settings import settings
from integrations.ghl.api import GHLAPIError
from integrations.ghl.companies import companies
from modules.campaign_manager import load_campaign
from modules.ghl_sync import _build_company_payload


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
PREFERRED_CSV = OUTPUT_DIR / "results_processed.csv"


def _latest_output_csv() -> Path | None:
    if PREFERRED_CSV.exists():
        return PREFERRED_CSV

    csv_files = sorted(
        OUTPUT_DIR.glob("*.csv"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    return csv_files[0] if csv_files else None


def _load_sample_prospect() -> tuple[dict[str, Any], str]:
    csv_file = _latest_output_csv()
    if csv_file:
        with csv_file.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if str(row.get("company_name") or "").strip():
                    return dict(row), str(csv_file)

    return (
        {
            "company_name": "Elula Company Sync Test",
            "address": "Gauteng, South Africa",
            "phone": "+27100000000",
            "website": "https://elula.co.za",
            "email": "",
            "category": "Security service",
            "owner": "Company Sync Test",
            "primary_product": settings.default_primary_product,
            "secondary_products": "",
            "review_rating": "",
            "review_count": "",
            "opening_hours": "",
            "business_status": "",
            "opportunity_score": "",
            "opportunity_reasons": "Safe hardcoded sample for payload diagnostics",
        },
        "safe hardcoded sample",
    )


def _print_json(title: str, value: Any) -> None:
    print(title)
    print(json.dumps(value, indent=2, ensure_ascii=True, sort_keys=True))


def run() -> None:
    campaign = load_campaign("security", "gauteng")
    prospect, source = _load_sample_prospect()

    print()
    print("=" * 60)
    print("ELULA BIZHUB COMPANY SYNC TEST")
    print("=" * 60)
    print(f"Prospect Source      : {source}")
    _print_json("Prospect selected:", prospect)

    owner_id = str(prospect.get("owner") or "Company Sync Test").strip()
    payload = _build_company_payload(prospect, owner_id, campaign)

    try:
        response = companies.create_company(payload)
    except GHLAPIError as exc:
        print("API error:")
        print(str(exc))
        return

    _print_json("API response:", response)
