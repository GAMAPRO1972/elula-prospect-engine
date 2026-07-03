"""
commands/process.py

Runs the Lead Processing Engine.
"""

from pathlib import Path

from modules.campaign_manager import load_campaign
from modules.file_manager import archive_file, find_csv_files
from modules.process_leads import export_prospects, prepare_prospects, process_csv


def _print_ghl_sync_section(
    enabled,
    total_processed,
    limit,
    prospects_synced,
    summary=None,
):
    summary = summary or {
        "contacts_created": 0,
        "contacts_updated": 0,
        "opportunities_created": 0,
        "tasks_created": 0,
        "imported": 0,
        "skipped": 0,
        "people_checked": 0,
        "people_found": 0,
        "failures": 0,
    }

    print()
    print("=" * 60)
    print("ELULA BIZHUB SYNCHRONIZATION")
    print("=" * 60)
    print(f"Sync Enabled         : {'Yes' if enabled else 'No'}")
    print(f"Total Prospects      : {total_processed}")
    print(f"Limit Applied        : {limit if limit is not None else 'None'}")
    print(f"Prospects Checked    : {prospects_synced}")
    print(f"People Checked       : {summary.get('people_checked', 0)}")
    print(f"People Found         : {summary.get('people_found', 0)}")
    print(f"Imported             : {summary.get('imported', 0)}")
    print(f"Skipped              : {summary.get('skipped', 0)}")
    print(f"Contacts Created     : {summary.get('contacts_created', 0)}")
    print(f"Contacts Updated     : {summary.get('contacts_updated', 0)}")
    print(f"Opportunities Created: {summary.get('opportunities_created', 0)}")
    print(f"Tasks Created        : {summary.get('tasks_created', 0)}")
    print(f"Failures             : {summary.get('failures', 0)}")


def run(industry, campaign, sync_to_ghl=False, limit=None):
    if limit is not None and limit < 1:
        raise ValueError("--limit must be greater than zero.")

    campaign_obj = load_campaign(
        industry,
        campaign,
    )

    csv_files = find_csv_files()

    if not csv_files:
        print("No CSV files found.")
        return

    total_processed = 0

    for csv_file in csv_files:
        output_file = (
            Path("output")
            / f"{csv_file.stem}_processed.csv"
        )

        if sync_to_ghl:
            from modules.ghl_sync import sync_prospects

            prospects = prepare_prospects(
                csv_file,
                campaign_obj,
            )

            sync_prospect_list = prospects
            if limit is not None:
                sync_prospect_list = prospects[:limit]

            summary = sync_prospects(
                sync_prospect_list,
                campaign_obj,
            )

            _print_ghl_sync_section(
                enabled=True,
                total_processed=len(prospects),
                limit=limit,
                prospects_synced=len(sync_prospect_list),
                summary=summary,
            )

            export_prospects(
                prospects,
                output_file,
            )

            processed = len(prospects)

        else:
            processed = process_csv(
                csv_file,
                output_file,
                campaign_obj,
            )

            _print_ghl_sync_section(
                enabled=False,
                total_processed=processed,
                limit=limit,
                prospects_synced=0,
            )

        archive_file(csv_file)

        total_processed += processed

        print(f"Processed: {csv_file.name}")

    print()
    print("=" * 60)
    print("ELULA PROSPECT ENGINE")
    print("=" * 60)
    print(f"Campaign           : {campaign_obj.name}")
    print(f"Files Processed    : {len(csv_files)}")
    print(f"Companies Processed: {total_processed}")
