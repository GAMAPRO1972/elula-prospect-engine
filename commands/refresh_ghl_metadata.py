"""
commands/refresh_ghl_metadata.py

Refreshes local GoHighLevel metadata from the live API.
"""

from integrations.ghl.api import GHLAPIError
from integrations.ghl.metadata import refresh_pipeline_metadata


def run(pipeline=None, company_id=None):
    print()
    print("=" * 60)
    print("GHL METADATA REFRESH")
    print("=" * 60)

    try:
        summary = refresh_pipeline_metadata(
            required_pipeline=pipeline,
            company_id=company_id,
        )
    except GHLAPIError as exc:
        print("Status             : FAILED")
        print(f"Reason             : {exc}")
        print("Required action    : Enable pipeline/opportunity and user/team read scopes for the configured GHL API token.")
        raise SystemExit(1) from exc
    except ValueError as exc:
        print("Status             : FAILED")
        print(f"Reason             : {exc}")
        raise SystemExit(1) from exc

    print(f"Pipelines refreshed: {summary['pipelines']}")
    print(f"Stages refreshed   : {summary['stages']}")
    print(f"Owners refreshed   : {summary['owners']}")
    print("Files updated      : integrations/ghl/pipelines.json, integrations/ghl/stages.json, integrations/ghl/owners.json")
