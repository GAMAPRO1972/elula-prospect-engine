"""
main.py

Entry point for the Elula Prospect Engine.
"""

import argparse

from commands.process import run as process_command
from commands.run import run as run_command
from commands.execute import run as execute_command


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
            campaign=args.campaign
        )


if __name__ == "__main__":
    main()