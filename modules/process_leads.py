"""
modules/process_leads.py

Processes raw Google Maps scraper CSV files into
Elula BizHub import files.
"""

from pathlib import Path
import csv

from modules.cleaner import clean_row
from modules.deduplicator import deduplicate
from modules.assignment_engine import assign_lead
from modules.opportunity_scoring import calculate_score


FIELDNAMES = [
    "company_name",
    "address",
    "phone",
    "website",
    "email",
    "category",
    "owner",
    "primary_product",
    "secondary_products",
    "review_rating",
    "review_count",
    "opportunity_score",
    "opportunity_reasons",
]


def build_prospect(row, campaign):
    """
    Convert a cleaned row into an Elula Prospect.
    """

    assignment = assign_lead(campaign)

    prospect = {
        "company_name": row.get("title", "").strip(),
        "address": row.get("complete_address", "").strip(),
        "phone": row.get("phone", "").strip(),
        "website": row.get("website", "").strip(),
        "email": row.get("emails", "").strip(),
        "category": row.get("category", "").strip(),
        "review_rating": row.get("review_rating", "").strip(),
        "review_count": row.get("review_count", "").strip(),
        "owner": assignment["owner"],
        "primary_product": assignment["primary_product"],
        "secondary_products": ", ".join(
            assignment["secondary_products"]
        ),
    }

    score, reasons = calculate_score(prospect)

    prospect["opportunity_score"] = score
    prospect["opportunity_reasons"] = ", ".join(reasons)

    return prospect


def prepare_prospects(input_file: Path, campaign):
    """
    Clean, deduplicate, score and assign raw Google Maps CSV rows.
    """

    prospects = []

    print(f"\nProcessing: {input_file.name}")

    with open(
        input_file,
        newline="",
        encoding="utf-8-sig"
    ) as csvfile:

        reader = csv.DictReader(csvfile)

        for row in reader:

            row = clean_row(row)

            prospect = build_prospect(
                row,
                campaign
            )

            prospects.append(prospect)

    raw_count = len(prospects)

    prospects = deduplicate(prospects)

    duplicate_count = raw_count - len(prospects)

    print(f"Raw Prospects:          {raw_count}")
    print(f"Duplicates Removed:    {duplicate_count}")
    print(f"Final Prospects:       {len(prospects)}")

    return prospects


def export_prospects(prospects, output_file: Path):
    """
    Export processed prospects to the standard CSV output.
    """

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        writer = csv.DictWriter(
            csvfile,
            fieldnames=FIELDNAMES
        )

        writer.writeheader()
        writer.writerows(prospects)

    print(f"Output File: {output_file}")


def process_csv(input_file: Path, output_file: Path, campaign):
    """
    Process a raw Google Maps CSV file into the standard CSV output.
    """

    prospects = prepare_prospects(input_file, campaign)
    export_prospects(prospects, output_file)

    return len(prospects)
