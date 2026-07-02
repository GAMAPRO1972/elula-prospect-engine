"""
tools/test_ghl_connection.py

Read-only GoHighLevel connectivity check.
"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings
from integrations.ghl.api import GHLAPIError, ghl


def _check_config() -> None:
    missing = []

    if not settings.ghl_api_key:
        missing.append("GHL_API_KEY")

    if not settings.ghl_location_id:
        missing.append("GHL_LOCATION_ID")

    if not settings.ghl_api_version:
        missing.append("GHL_API_VERSION")

    if missing:
        raise RuntimeError(
            "Missing required environment values: "
            + ", ".join(missing)
        )


def main() -> int:
    print("GoHighLevel Connection Test")
    print("=" * 40)
    print(f"Base URL   : {settings.ghl_base_url}")
    print(f"Version    : {settings.ghl_api_version}")
    print(f"Location ID: {settings.ghl_location_id}")

    try:
        _check_config()
        response = ghl.get(f"locations/{settings.ghl_location_id}")

    except (RuntimeError, GHLAPIError) as exc:
        print()
        print("Status     : FAILED")
        print(f"Reason     : {exc}")
        return 1

    location = response.get("location", response) if isinstance(response, dict) else {}
    location_name = location.get("name") or location.get("businessName") or "Verified"

    print()
    print("Status     : PASSED")
    print(f"Location   : {location_name}")
    print("Auth       : PASSED")
    print("Connectivity: PASSED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
