"""
main.py

Entry point for the Elula Prospect Engine.
"""

import argparse

from commands.process import run as process_command
from commands.run import run as run_command
from commands.execute import run as execute_command
from commands.refresh_ghl_metadata import run as refresh_ghl_metadata_command


def main():

    parser = argparse.ArgumentParser(
        description="Elula Prospect Engine"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # -------------------------
    # Process Command
    # -------------------------

    process_parser = subparsers.add_parser(
        "process",
        help="Process CSV files into Elula BizHub import files."
    )

    process_parser.add_argument(
        "--industry",
        default="security",
        help="Industry folder under campaigns/"
    )

    process_parser.add_argument(
        "--campaign",
        default="gauteng",
        help="Campaign name"
    )

    # -------------------------
    # Run Command
    # -------------------------

    run_parser = subparsers.add_parser(
        "run",
        help="Run Google Maps scraper."
    )

    run_parser.add_argument(
        "--industry",
        default="security",
        help="Industry folder under campaigns/"
    )

    run_parser.add_argument(
        "--campaign",
        default="gauteng",
        help="Campaign name"
    )

    # -------------------------
    # Execute Command
    # -------------------------

    execute_parser = subparsers.add_parser(
        "execute",
        help="Run the complete Prospect Engine workflow."
    )

    execute_parser.add_argument(
        "--industry",
        default="security",
        help="Industry folder under campaigns/"
    )

    execute_parser.add_argument(
        "--campaign",
        default="gauteng",
        help="Campaign name"
    )

    execute_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit prospects synced to GoHighLevel after processing."
    )

    # -------------------------
    # Refresh GHL Metadata Command
    # -------------------------

    refresh_parser = subparsers.add_parser(
        "refresh-ghl-metadata",
        help="Fetch live GoHighLevel pipelines and stages into local metadata files."
    )

    refresh_parser.add_argument(
        "--pipeline",
        default="Security Prospecting",
        help="Pipeline name that must exist in the live GHL metadata."
    )

    refresh_parser.add_argument(
        "--company-id",
        default=None,
        help="GHL company ID used to fetch team users when it is not configured in .env."
    )

    args = parser.parse_args()

    # -------------------------
    # Execute Commands
    # -------------------------

    if args.command == "process":

        process_command(
            industry=args.industry,
            campaign=args.campaign
        )

    elif args.command == "run":

        run_command(
            industry=args.industry,
            campaign=args.campaign
        )

    elif args.command == "execute":

        execute_command(
            industry=args.industry,
            campaign=args.campaign,
            limit=args.limit
        )

    elif args.command == "refresh-ghl-metadata":

        refresh_ghl_metadata_command(
            pipeline=args.pipeline,
            company_id=args.company_id
        )


if __name__ == "__main__":
    main()
