"""
main.py

Entry point for the Elula Prospect Engine.
"""

import argparse

from commands.execute import run as execute_command
from commands.process import run as process_command
from commands.refresh_ghl_metadata import run as refresh_ghl_metadata_command
from commands.run import run as run_command


def main():
    parser = argparse.ArgumentParser(
        description="Elula Prospect Engine",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    process_parser = subparsers.add_parser(
        "process",
        help="Process CSV files into Elula BizHub import files.",
    )
    process_parser.add_argument(
        "--industry",
        default="security",
        help="Industry folder under campaigns/",
    )
    process_parser.add_argument(
        "--campaign",
        default="gauteng",
        help="Campaign name",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Run Google Maps scraper.",
    )
    run_parser.add_argument(
        "--industry",
        default="security",
        help="Industry folder under campaigns/",
    )
    run_parser.add_argument(
        "--campaign",
        default="gauteng",
        help="Campaign name",
    )

    execute_parser = subparsers.add_parser(
        "execute",
        help="Run the complete Prospect Engine workflow.",
    )
    execute_parser.add_argument(
        "--industry",
        default="security",
        help="Industry folder under campaigns/",
    )
    execute_parser.add_argument(
        "--campaign",
        default="gauteng",
        help="Campaign name",
    )
    execute_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit prospects checked after processing.",
    )
    execute_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without creating or updating Elula BizHub records.",
    )

    refresh_parser = subparsers.add_parser(
        "refresh-ghl-metadata",
        help="Fetch live Elula BizHub pipelines and stages into local metadata files.",
    )
    refresh_parser.add_argument(
        "--pipeline",
        default="Security Prospecting",
        help="Pipeline name that must exist in the live Elula BizHub metadata.",
    )
    refresh_parser.add_argument(
        "--company-id",
        default=None,
        help="Elula BizHub company ID used to fetch team users when it is not configured in .env.",
    )

    args = parser.parse_args()

    if args.command == "process":
        process_command(
            industry=args.industry,
            campaign=args.campaign,
        )

    elif args.command == "run":
        run_command(
            industry=args.industry,
            campaign=args.campaign,
        )

    elif args.command == "execute":
        execute_command(
            industry=args.industry,
            campaign=args.campaign,
            limit=args.limit,
            dry_run=args.dry_run,
        )

    elif args.command == "refresh-ghl-metadata":
        refresh_ghl_metadata_command(
            pipeline=args.pipeline,
            company_id=args.company_id,
        )


if __name__ == "__main__":
    main()
