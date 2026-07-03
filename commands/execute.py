"""
commands/execute.py

Runs the complete Prospect Engine workflow.
"""

from commands.process import run as process_command
from commands.run import run as run_command
from modules.campaign_manager import load_campaign
from modules.file_manager import find_csv_files


def run(industry, campaign, limit=None, dry_run=False, intelligence=False):
    campaign_obj = load_campaign(
        industry,
        campaign,
    )
    sync_to_ghl = campaign_obj.config.get("sync_to_ghl") is True

    print()
    print("=" * 60)
    print("ELULA PROSPECT ENGINE")
    print("=" * 60)
    print("Starting execution...")
    if dry_run:
        print("DRY RUN: Elula BizHub writes and import history writes are disabled.")
    if intelligence:
        print("INTELLIGENCE: Google Business intelligence reports are enabled.")
    print()

    print("STEP 1 - Running Google Maps scraper")
    scraper_success = run_command(
        industry=industry,
        campaign=campaign,
    )

    local_csv_files = find_csv_files()

    if not scraper_success:
        print()
        print("SCRAPER STATUS: FAILED")
        if local_csv_files:
            print(
                "Processing will continue with "
                f"{len(local_csv_files)} existing local CSV file(s)."
            )
        else:
            print("No local CSV files are available. Processing will exit safely.")

    print()
    print("STEP 2 - Processing results")
    process_command(
        industry=industry,
        campaign=campaign,
        sync_to_ghl=sync_to_ghl,
        limit=limit,
        dry_run=dry_run,
        intelligence=intelligence,
    )

    print()
    print("=" * 60)
    if scraper_success:
        print("Workflow completed successfully.")
    elif local_csv_files:
        print("Workflow completed with scraper failure; existing local CSV files were processed.")
    else:
        print("Workflow completed with scraper failure; no local CSV files were processed.")
    if dry_run:
        print("DRY RUN completed: no Elula BizHub records or import history entries were written.")
    print("=" * 60)
