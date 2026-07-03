"""
integrations/google_business/client.py

Safe local client boundary for Google Business Profile intelligence.
"""

from __future__ import annotations

from typing import Any

from integrations.google_business.models import GoogleBusinessProfile
from integrations.google_business.parser import parse_google_business_profile


class GoogleBusinessClient:
    """
    Local-only Google Business intelligence client.

    This class intentionally does not call paid or external APIs. It adapts
    available scraper or prospect fields into a profile model.
    """

    def build_profile(self, prospect: dict[str, Any]) -> GoogleBusinessProfile:
        return parse_google_business_profile(prospect)
