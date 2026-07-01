"""
query_exporter.py

Exports campaign keywords into a queries.txt file
compatible with the Google Maps Scraper.
"""

from pathlib import Path

EXPORT_DIR = Path(__file__).resolve().parent.parent / "exports"


def export_queries(campaign):

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = EXPORT_DIR / "queries.txt"

    with open(output_file, "w", encoding="utf-8") as file:

        for keyword in campaign.keywords:
            file.write(keyword + "\n")

    return output_file