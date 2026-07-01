"""
commands/execute.py

Runs the complete Prospect Engine workflow.
"""

from commands.run import run as run_command
from commands.process import run as process_command


def run(industry, campaign):

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
    )

    print()
    print("=" * 60)
    print("Workflow completed successfully.")
    print("=" * 60)