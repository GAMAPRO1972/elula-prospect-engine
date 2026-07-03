"""
integrations/website/service.py

Service layer for prospect website intelligence.
"""

from __future__ import annotations

from typing import Any

from integrations.website.analyzer import analyze_website
from integrations.website.models import WebsiteIntelligence


class WebsiteIntelligenceService:
    """Analyzes one prospect website and returns sales-useful intelligence."""

    def analyze_prospect(self, prospect: dict[str, Any]) -> WebsiteIntelligence:
        website = prospect.get("website", "")
        return analyze_website(website)
