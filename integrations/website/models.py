"""
integrations/website/models.py

Data model for website intelligence gathered from prospect websites.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WebsiteIntelligence:
    website_url: str = ""
    final_url: str = ""
    is_reachable: bool = False
    http_status: int | None = None
    uses_https: bool = False
    title: str = ""
    meta_description: str = ""
    has_contact_page: bool = False
    has_about_page: bool = False
    has_careers_page: bool = False
    has_team_page: bool = False
    email_addresses: list[str] = field(default_factory=list)
    phone_numbers: list[str] = field(default_factory=list)
    social_links: list[str] = field(default_factory=list)
    has_whatsapp_link: bool = False
    has_contact_form: bool = False
    has_live_chat: bool = False
    has_google_analytics: bool = False
    has_google_tag_manager: bool = False
    has_meta_pixel: bool = False
    detected_cms: str = "Unknown"
    website_quality_score: int = 0
    digital_maturity_score: int = 0
    findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    source: str = "website_homepage"
    confidence: float = 0.0
