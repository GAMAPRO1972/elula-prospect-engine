"""
integrations/website/analyzer.py

Lightweight website intelligence analyzer.
"""

from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from requests import RequestException

from integrations.website.models import WebsiteIntelligence


TIMEOUT_SECONDS = (3.05, 5)
MAX_RESPONSE_CHARS = 1_000_000
OPTIONAL_PATHS = {
    "contact": ["/contact", "/contact-us"],
    "about": ["/about", "/about-us"],
    "team": ["/team"],
    "careers": ["/careers"],
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.meta_description = ""
        self.links: list[str] = []
        self.forms = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key.lower(): value or "" for key, value in attrs}

        if tag.lower() == "title":
            self._in_title = True

        if tag.lower() == "meta":
            name = attributes.get("name", "").lower()
            property_name = attributes.get("property", "").lower()
            if name == "description" or property_name == "og:description":
                self.meta_description = attributes.get("content", "").strip()

        if tag.lower() == "a" and attributes.get("href"):
            self.links.append(attributes["href"])

        if tag.lower() == "form":
            self.forms += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data.strip()


def normalize_website_url(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""

    if not text.startswith(("http://", "https://")):
        text = f"https://{text}"

    parsed = urlparse(text)
    if not parsed.netloc:
        return ""

    return text


def _fetch(session: requests.Session, url: str) -> tuple[str, str, int | None, bool]:
    try:
        response = session.get(
            url,
            timeout=TIMEOUT_SECONDS,
            allow_redirects=True,
            headers={
                "User-Agent": "ElulaProspectEngine/0.4 WebsiteIntelligence",
            },
        )
    except RequestException:
        return url, "", None, False

    text = response.text[:MAX_RESPONSE_CHARS]
    reachable = 200 <= response.status_code < 400

    return response.url, text, response.status_code, reachable


def _parse_html(html: str) -> PageParser:
    parser = PageParser()
    parser.feed(html)
    return parser


def _unique(values: list[str]) -> list[str]:
    seen = set()
    result = []

    for value in values:
        cleaned = value.strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)

    return result


def _extract_emails(text: str) -> list[str]:
    matches = re.findall(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        text,
    )
    return _unique([match.lower() for match in matches])


def _extract_phones(text: str) -> list[str]:
    matches = re.findall(
        r"(?:\+27|0)(?:[\s().-]*\d){9}",
        text,
    )
    return _unique([re.sub(r"\s+", " ", match).strip() for match in matches])


def _absolute_links(base_url: str, links: list[str]) -> list[str]:
    return _unique([urljoin(base_url, link) for link in links if link])


def _social_links(links: list[str]) -> list[str]:
    domains = [
        "facebook.com",
        "instagram.com",
        "linkedin.com",
        "twitter.com",
        "x.com",
        "youtube.com",
        "tiktok.com",
    ]

    return [
        link
        for link in links
        if any(domain in link.lower() for domain in domains)
    ]


def _has_live_chat(text: str) -> bool:
    indicators = [
        "intercom",
        "tawk.to",
        "crisp.chat",
        "livechatinc",
        "zendesk chat",
        "hubspot chat",
        "chat widget",
        "whatsapp-floating",
    ]
    lowered = text.lower()
    return any(indicator in lowered for indicator in indicators)


def _detect_cms(text: str) -> str:
    lowered = text.lower()

    if "wp-content" in lowered or "wp-includes" in lowered:
        return "WordPress"
    if "wixstatic.com" in lowered or "x-wix" in lowered:
        return "Wix"
    if "cdn.shopify.com" in lowered or "myshopify.com" in lowered:
        return "Shopify"
    if "squarespace.com" in lowered or "static1.squarespace.com" in lowered:
        return "Squarespace"
    if "webflow" in lowered:
        return "Webflow"

    return "Unknown"


def _same_domain(first_url: str, second_url: str) -> bool:
    first_host = urlparse(first_url).netloc.lower().removeprefix("www.")
    second_host = urlparse(second_url).netloc.lower().removeprefix("www.")
    return first_host == second_host


def _page_exists(session: requests.Session, base_url: str, paths: list[str]) -> bool:
    for path in paths:
        url = urljoin(base_url, path)
        final_url, _, status, reachable = _fetch(session, url)
        if reachable and status is not None and _same_domain(base_url, final_url):
            return True

    return False


def _score_quality(intelligence: WebsiteIntelligence) -> int:
    # Website quality is a simple operational readiness score:
    # reachable site, secure URL, useful metadata, enquiry paths, and contact data.
    score = 0
    if intelligence.is_reachable:
        score += 25
    if intelligence.uses_https:
        score += 15
    if intelligence.title:
        score += 10
    if intelligence.meta_description:
        score += 10
    if intelligence.has_contact_page:
        score += 15
    if intelligence.email_addresses or intelligence.phone_numbers:
        score += 15
    if intelligence.has_contact_form or intelligence.has_whatsapp_link:
        score += 10

    return min(score, 100)


def _score_digital_maturity(intelligence: WebsiteIntelligence) -> int:
    # Digital maturity measures how much trackable, automatable infrastructure exists.
    score = 0
    if intelligence.is_reachable:
        score += 20
    if intelligence.has_google_analytics:
        score += 15
    if intelligence.has_google_tag_manager:
        score += 20
    if intelligence.has_meta_pixel:
        score += 15
    if intelligence.social_links:
        score += 10
    if intelligence.has_live_chat:
        score += 10
    if intelligence.detected_cms != "Unknown":
        score += 10

    return min(score, 100)


def _build_findings(intelligence: WebsiteIntelligence) -> list[str]:
    findings = []

    if not intelligence.is_reachable:
        findings.append("Website is not reachable")
    if intelligence.is_reachable and not intelligence.has_contact_page:
        findings.append("No contact page detected")
    if intelligence.is_reachable and not intelligence.has_whatsapp_link:
        findings.append("No WhatsApp link detected")
    if (
        intelligence.is_reachable
        and not intelligence.has_google_analytics
        and not intelligence.has_google_tag_manager
        and not intelligence.has_meta_pixel
    ):
        findings.append("No analytics tracking detected")
    if intelligence.detected_cms != "Unknown":
        findings.append(f"Website appears to use {intelligence.detected_cms}")

    return findings


def _build_recommendations(intelligence: WebsiteIntelligence) -> list[str]:
    recommendations = []

    if not intelligence.is_reachable:
        recommendations.append("Discuss website reliability and missed enquiry capture")
        recommendations.append("Position Red XRay if website has public digital footprint")
        return recommendations

    if not intelligence.has_contact_page or not intelligence.has_contact_form:
        recommendations.append("Discuss missed enquiry capture")

    if not intelligence.has_whatsapp_link:
        recommendations.append("Position Elula BizHub for WhatsApp enquiry automation")

    if (
        not intelligence.has_google_analytics
        and not intelligence.has_google_tag_manager
        and not intelligence.has_meta_pixel
    ):
        recommendations.append("Position Elula BizHub for enquiry automation and reporting")

    recommendations.append("Position Red XRay if website has public digital footprint")

    return _unique(recommendations)


def analyze_website(website_url: str) -> WebsiteIntelligence:
    normalized_url = normalize_website_url(website_url)
    intelligence = WebsiteIntelligence(
        website_url=website_url or "",
        final_url=normalized_url,
        uses_https=normalized_url.startswith("https://"),
    )

    if not normalized_url:
        intelligence.findings = ["Website URL is missing or invalid"]
        intelligence.recommendations = ["Confirm website before outreach"]
        return intelligence

    session = requests.Session()
    final_url, homepage_html, status, reachable = _fetch(session, normalized_url)
    parser = _parse_html(homepage_html) if homepage_html else PageParser()
    links = _absolute_links(final_url, parser.links)
    text = unescape(homepage_html)
    lowered = text.lower()

    intelligence.final_url = final_url
    intelligence.is_reachable = reachable
    intelligence.http_status = status
    intelligence.uses_https = final_url.startswith("https://")
    intelligence.title = parser.title.strip()
    intelligence.meta_description = parser.meta_description.strip()
    intelligence.email_addresses = _extract_emails(text)
    intelligence.phone_numbers = _extract_phones(text)
    intelligence.social_links = _social_links(links)
    intelligence.has_whatsapp_link = "wa.me/" in lowered or "api.whatsapp.com" in lowered
    intelligence.has_contact_form = parser.forms > 0 and (
        "contact" in lowered
        or "enquiry" in lowered
        or "inquiry" in lowered
        or "message" in lowered
    )
    intelligence.has_live_chat = _has_live_chat(text)
    intelligence.has_google_analytics = "google-analytics.com" in lowered or "gtag(" in lowered
    intelligence.has_google_tag_manager = "googletagmanager.com" in lowered or "gtm-" in lowered
    intelligence.has_meta_pixel = "connect.facebook.net" in lowered or "fbq(" in lowered
    intelligence.detected_cms = _detect_cms(text)

    if reachable:
        intelligence.has_contact_page = _page_exists(session, final_url, OPTIONAL_PATHS["contact"])
        intelligence.has_about_page = _page_exists(session, final_url, OPTIONAL_PATHS["about"])
        intelligence.has_team_page = _page_exists(session, final_url, OPTIONAL_PATHS["team"])
        intelligence.has_careers_page = _page_exists(session, final_url, OPTIONAL_PATHS["careers"])

    intelligence.website_quality_score = _score_quality(intelligence)
    intelligence.digital_maturity_score = _score_digital_maturity(intelligence)
    intelligence.findings = _build_findings(intelligence)
    intelligence.recommendations = _build_recommendations(intelligence)
    intelligence.confidence = 0.8 if reachable else 0.2

    return intelligence
