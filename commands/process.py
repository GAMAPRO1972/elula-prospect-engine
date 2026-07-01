"""
commands/process.py

Runs the Lead Processing Engine.
"""

from pathlib import Path

from modules.campaign_manager import load_campaign
from modules.process_leads import process_csv
from modules.file_manager import (
    find_csv_files,
    archive_file,
)


def run(industry, campaign):

    # Load the campaign definition
    campaign_obj = load_campaign(
        industry,
        campaign
    )

    # Find all CSV files waiting to be processed
    csv_files = find_csv_files()

    if not csv_files:
        print("No CSV files found.")
        return

    total_processed = 0

    # Process each CSV file
    for csv_file in csv_files:

        output_file = (
            Path("output") /
            f"{csv_file.stem}_processed.csv"
        )

        processed = process_csv(
            csv_file,
            output_file,
            campaign_obj
        )

        archive_file(csv_file)

        total_processed += processed

        print(f"✓ Processed: {csv_file.name}")

    print()
    print("=" * 60)
    print("ELULA PROSPECT ENGINE")
    print("=" * 60)
    print(f"Campaign           : {campaign_obj.name}")
    print(f"Files Processed    : {len(csv_files)}")
    print(f"Companies Processed: {total_processed}")