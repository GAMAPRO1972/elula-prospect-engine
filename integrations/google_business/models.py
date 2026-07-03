"""
integrations/google_business/models.py

Data models for Google Business Profile intelligence.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GoogleBusinessProfile:
    company_name: str = ""
    category: str = ""
    rating: float | None = None
    review_count: int | None = None
    phone: str = ""
    website: str = ""
    address: str = ""
    opening_hours: str = ""
    business_status: str = ""
    source: str = "google_maps_scraper"
    warnings: list[str] = field(default_factory=list)
