from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from modules.utils import (
    clean_text,
    load_json,
    normalize_phone,
    normalize_website,
    parse_optional_json,
    safe_float,
)

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "settings.json"
DEFAULT_INPUT_DIR = BASE_DIR / "input"
DEFAULT_OUTPUT_DIR = BASE_DIR / "output"
DEFAULT_REPORT_DIR = BASE_DIR / "reports"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process scraped prospect data into an importable CSV")
    parser.add_argument("--input", type=Path, help="Path to a CSV file or directory of CSV files")
    parser.add_argument("--output", type=Path, help="Destination CSV file")
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of rows to process (0 = all)")
    return parser.parse_args()


def discover_input_files(path: Path | None) -> list[Path]:
    if path is not None:
        if path.is_file():
            return [path]
        if path.is_dir():
            return sorted(path.glob("*.csv"))

    if DEFAULT_INPUT_DIR.exists():
        return sorted(DEFAULT_INPUT_DIR.glob("*.csv"))
    return []


def build_prospect(row: dict[str, Any], settings: dict[str, Any]) -> dict[str, Any]:
    title = clean_text(row.get("title") or row.get("name") or row.get("company_name"))
    address = clean_text(row.get("complete_address") or row.get("address"))
    phone = normalize_phone(row.get("phone"), settings.get("phone_country_code", "+27"))
    website = normalize_website(row.get("website"))
    emails = parse_optional_json(row.get("emails"))
    if isinstance(emails, list):
        email = next((clean_text(item) for item in emails if clean_text(item)), "")
    else:
        email = clean_text(emails)

    notes_parts: list[str] = []
    category = clean_text(row.get("category"))
    if category:
        notes_parts.append(f"Category: {category}")
    description = clean_text(row.get("descriptions") or row.get("about"))
    if description:
        notes_parts.append(description)

    return {
        "input_id": clean_text(row.get("input_id")),
        "company_name": title,
        "address": address,
        "phone": phone,
        "website": website,
        "email": email,
        "category": category,
        "source": clean_text(settings.get("default_source", "Google Maps")),
        "status": clean_text(settings.get("default_status", "New")),
        "primary_product": clean_text(settings.get("default_primary_product", "Elula BizHub")),
        "country": clean_text(settings.get("country", "South Africa")),
        "latitude": safe_float(row.get("latitude")),
        "longitude": safe_float(row.get("longitude")),
        "review_count": clean_text(row.get("review_count")),
        "review_rating": clean_text(row.get("review_rating")),
        "notes": " | ".join(part for part in notes_parts if part),
    }


def write_output_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "input_id",
        "company_name",
        "address",
        "phone",
        "website",
        "email",
        "category",
        "source",
        "status",
        "primary_product",
        "country",
        "latitude",
        "longitude",
        "review_count",
        "review_rating",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_report(path: Path, input_path: Path, output_path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_file": str(input_path),
        "output_file": str(output_path),
        "processed_rows": len(rows),
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)


def process_inputs(input_files: list[Path], output_path: Path, limit: int, settings: dict[str, Any]) -> list[dict[str, Any]]:
    all_rows: list[dict[str, Any]] = []
    for input_path in input_files:
        with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for index, row in enumerate(reader, start=1):
                if limit and len(all_rows) >= limit:
                    break
                prospect = build_prospect(row, settings)
                all_rows.append(prospect)
            if limit and len(all_rows) >= limit:
                break

    write_output_csv(output_path, all_rows)
    report_path = DEFAULT_REPORT_DIR / f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_processing_report.json"
    write_report(report_path, input_files[0] if input_files else Path("<none>"), output_path, all_rows)
    return all_rows


def main() -> int:
    args = parse_args()
    settings = load_json(CONFIG_PATH)
    input_files = discover_input_files(args.input)
    if not input_files:
        print("No input CSV files were found.", file=sys.stderr)
        return 1

    output_path = args.output or DEFAULT_OUTPUT_DIR / settings.get("output_filename", "ElulaBizHub_Import.csv")
    rows = process_inputs(input_files, output_path, args.limit, settings)
    print(f"Processed {len(rows)} prospects")
    print(f"Output written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
