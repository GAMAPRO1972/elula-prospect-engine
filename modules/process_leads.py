"""
process_leads.py

Processes raw Google Maps scraper CSV files into
Elula BizHub import files.
"""

from pathlib import Path
import csv

from modules.assignment_engine import assign_lead
from modules.opportunity_scoring import calculate_score
from modules.cleaner import clean_row


def build_prospect(row, campaign):
    """
    Convert a cleaned CSV row into an Elula prospect.
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


def process_csv(input_file: Path, output_file: Path, campaign):
    """
    Process a raw Google Maps CSV into an Elula BizHub import file.
    """

    prospects = []

    with open(input_file, newline="", encoding="utf-8-sig") as csvfile:

        reader = csv.DictReader(csvfile)

        for row in reader:

            row = clean_row(row)

            prospect = build_prospect(
                row,
                campaign
            )

            prospects.append(prospect)

    fieldnames = [
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
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(prospects)

    return len(prospects)