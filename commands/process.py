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
    dry_run=False,
):
    summary = summary or {
        "companies_created": 0,
        "companies_updated": 0,
        "company_sync_unavailable": 0,
        "contacts_created": 0,
        "contacts_updated": 0,
        "opportunities_created": 0,
        "tasks_created": 0,
        "companies_would_upsert": 0,
        "contacts_would_upsert": 0,
        "opportunities_would_create": 0,
        "tasks_would_create": 0,
        "import_history_would_record": 0,
        "imported": 0,
        "skipped": 0,
        "people_checked": 0,
        "people_found": 0,
        "websites_checked": 0,
        "websites_reachable": 0,
        "average_website_quality_score": 0,
        "average_digital_maturity_score": 0,
        "failures": 0,
    }

    print()
    print("=" * 60)
    print("ELULA BIZHUB SYNCHRONIZATION")
    print("=" * 60)
    print(f"Mode                 : {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"Sync Enabled         : {'Yes' if enabled else 'No'}")
    print(f"Total Prospects      : {total_processed}")
    print(f"Limit Applied        : {limit if limit is not None else 'None'}")
    print(f"Prospects Checked    : {prospects_synced}")
    print(f"People Checked       : {summary.get('people_checked', 0)}")
    print(f"People Found         : {summary.get('people_found', 0)}")
    print(f"Websites Checked     : {summary.get('websites_checked', 0)}")
    print(f"Websites Reachable   : {summary.get('websites_reachable', 0)}")
    print(f"Avg Website Quality  : {summary.get('average_website_quality_score', 0)}")
    print(f"Avg Digital Maturity : {summary.get('average_digital_maturity_score', 0)}")

    if dry_run:
        print(f"Would Upsert Companies: {summary.get('companies_would_upsert', 0)}")
        print(f"Would Upsert Contacts: {summary.get('contacts_would_upsert', 0)}")
        print(f"Would Create Opps    : {summary.get('opportunities_would_create', 0)}")
        print(f"Would Create Tasks   : {summary.get('tasks_would_create', 0)}")
        print(f"Would Record History : {summary.get('import_history_would_record', 0)}")
    else:
        print(f"Imported             : {summary.get('imported', 0)}")
        print(f"Companies Created    : {summary.get('companies_created', 0)}")
        print(f"Companies Updated    : {summary.get('companies_updated', 0)}")
        print(f"Company Sync Skipped : {summary.get('company_sync_unavailable', 0)}")
        print(f"Contacts Created     : {summary.get('contacts_created', 0)}")
        print(f"Contacts Updated     : {summary.get('contacts_updated', 0)}")
        print(f"Opportunities Created: {summary.get('opportunities_created', 0)}")
        print(f"Tasks Created        : {summary.get('tasks_created', 0)}")

    print(f"Skipped              : {summary.get('skipped', 0)}")
    print(f"Failures             : {summary.get('failures', 0)}")


def _limited(prospects, limit):
    if limit is None:
        return prospects
    return prospects[:limit]


def _generate_intelligence_reports(prospects):
    from modules.google_business_intelligence import generate_business_intelligence_reports

    summary = generate_business_intelligence_reports(prospects)

    print()
    print("=" * 60)
    print("GOOGLE BUSINESS INTELLIGENCE")
    print("=" * 60)
    print(f"Records Analysed     : {summary['records']}")
    print(f"CSV Report           : {summary['csv_report']}")
    print(f"Excel Report         : {summary['xlsx_report']}")
    print(f"Client Reports       : {len(summary['client_reports'])}")


def run(industry, campaign, sync_to_ghl=False, limit=None, dry_run=False, intelligence=False):
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

            sync_prospect_list = _limited(prospects, limit)

            if intelligence:
                _generate_intelligence_reports(sync_prospect_list)

            summary = sync_prospects(
                sync_prospect_list,
                campaign_obj,
                dry_run=dry_run,
            )

            _print_ghl_sync_section(
                enabled=True,
                total_processed=len(prospects),
                limit=limit,
                prospects_synced=len(sync_prospect_list),
                summary=summary,
                dry_run=dry_run,
            )

            export_prospects(
                prospects,
                output_file,
            )

            processed = len(prospects)

        elif intelligence:
            prospects = prepare_prospects(
                csv_file,
                campaign_obj,
            )
            intelligence_prospect_list = _limited(prospects, limit)

            _generate_intelligence_reports(intelligence_prospect_list)

            export_prospects(
                prospects,
                output_file,
            )

            _print_ghl_sync_section(
                enabled=False,
                total_processed=len(prospects),
                limit=limit,
                prospects_synced=0,
                dry_run=dry_run,
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
                dry_run=dry_run,
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
