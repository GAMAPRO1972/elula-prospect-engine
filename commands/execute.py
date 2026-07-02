"""
commands/execute.py

Runs the complete Prospect Engine workflow.
"""

from commands.run import run as run_command
from commands.process import run as process_command
from modules.campaign_manager import load_campaign


def run(industry, campaign, limit=None):
    campaign_obj = load_campaign(
        industry,
        campaign
    )
    sync_to_ghl = campaign_obj.config.get("sync_to_ghl") is True

    print()
    print("=" * 60)
    print("ELULA PROSPECT ENGINE")
    print("=" * 60)
    print("Starting execution...")
    print()

    print("STEP 1 - Running Google Maps scraper")
    run_command(
        industry=industry,
        campaign=campaign,
    )

    print()
    print("STEP 2 - Processing results")
    process_command(
        industry=industry,
        campaign=campaign,
        sync_to_ghl=sync_to_ghl,
        limit=limit,
    )

    print()
    print("=" * 60)
    print("Workflow completed successfully.")
    print("=" * 60)
