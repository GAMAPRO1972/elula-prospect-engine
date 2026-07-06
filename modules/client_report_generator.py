"""
modules/client_report_generator.py

Generates branded Elula Business Growth Assessment PDF reports.
"""

from __future__ import annotations

import html
import json
import re
import textwrap
from pathlib import Path
from typing import Any

from modules.sales_opportunity_engine import top_opportunity


REPORT_DIR = Path("reports") / "client_reports"
TEMPLATE_PATH = Path("templates") / "client_reports" / "elula_business_growth_assessment.html"
STYLES_PATH = Path("templates") / "client_reports" / "report_styles.css"
PUBLIC_DATA_MISSING = "Not available from public data"


def safe_filename(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", value or "company").strip("_")
    return text or "company"


def _display(value: Any) -> str:
    text = str(value or "").strip()
    if text in {"{}", "[]", "null", "None"}:
        text = ""
    return text if text else PUBLIC_DATA_MISSING


def _escape_pdf_text(value: Any) -> str:
    return str(value or "").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap_text(value: Any, width: int = 92) -> list[str]:
    return textwrap.wrap(_display(value), width=width) or [PUBLIC_DATA_MISSING]


def _wrap_lines(label: str, value: Any, width: int = 92) -> list[str]:
    text = f"{label}: {_display(value)}" if label else _display(value)
    return textwrap.wrap(text, width=width) or [PUBLIC_DATA_MISSING]


def _section(heading: str, body_lines: list[str]) -> list[str]:
    lines = ["", heading.upper()]
    lines.extend(body_lines or [PUBLIC_DATA_MISSING])
    return lines


def _paginate(lines: list[str], page_size: int = 56) -> list[list[str]]:
    pages = []
    current = []

    for line in lines:
        is_heading = line.isupper() and len(line) > 3
        if is_heading and len(current) >= page_size - 8:
            pages.append(current)
            current = []
        elif len(current) >= page_size and line:
            pages.append(current)
            current = []
        current.append(line)

    if current:
        pages.append(current)

    return pages


def _content_stream(lines: list[str], page_number: int, total_pages: int) -> bytes:
    stream_lines = [
        "BT",
        "/F1 10 Tf",
        "48 792 Td",
        "13 TL",
    ]

    all_lines = list(lines)
    all_lines.append("")
    all_lines.append(f"Page {page_number} of {total_pages}")

    first = True
    for line in all_lines:
        if not first:
            stream_lines.append("T*")
        first = False
        stream_lines.append(f"({_escape_pdf_text(line[:112])}) Tj")

    stream_lines.append("ET")
    return "\n".join(stream_lines).encode("latin-1", errors="replace")


def _write_simple_pdf(path: Path, lines: list[str]) -> None:
    pages = _paginate(lines)
    total_pages = len(pages)

    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")

    page_object_ids = []
    content_object_ids = []
    next_id = 3
    for _ in pages:
        page_object_ids.append(next_id)
        content_object_ids.append(next_id + 1)
        next_id += 2

    font_object_id = next_id
    kids = " ".join(f"{page_id} 0 R" for page_id in page_object_ids)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {total_pages} >>".encode("ascii"))

    for index, page_lines in enumerate(pages, start=1):
        page_id = page_object_ids[index - 1]
        content_id = content_object_ids[index - 1]
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                f"/Resources << /Font << /F1 {font_object_id} 0 R >> >> "
                f"/Contents {content_id} 0 R >>"
            ).encode("ascii")
        )
        stream = _content_stream(page_lines, index, total_pages)
        objects.append(
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )

    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    content = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(content))
        content.extend(f"{index} 0 obj\n".encode("ascii"))
        content.extend(obj)
        content.extend(b"\nendobj\n")

    xref_offset = len(content)
    content.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    content.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        content.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    content.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )

    path.write_bytes(content)


def _render_html(context: dict[str, Any]) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    styles = STYLES_PATH.read_text(encoding="utf-8") if STYLES_PATH.exists() else ""

    rendered = template.replace("{{ styles }}", styles)
    for key, value in context.items():
        rendered = rendered.replace("{{ " + key + " }}", html.escape(str(value or "")))

    return rendered


def _confidence(value: str) -> str:
    if value == "high":
        return "High Confidence"
    if value == "medium":
        return "Medium Confidence"
    return "Requires Discussion"


def _score_label(score: int | None) -> str:
    return "Unknown" if score is None else f"{score} / 100"


def _rating_score(rating: float | None, review_count: int | None) -> int | None:
    if rating is None and review_count is None:
        return None

    rating_component = round(((rating or 0) / 5) * 65) if rating is not None else 0
    review_component = min(review_count or 0, 100) * 35 // 100
    return min(100, rating_component + review_component)


def _digital_presence_score(intelligence) -> int:
    score = 0
    if intelligence.website:
        score += 40
    if intelligence.phone:
        score += 25
    if intelligence.address:
        score += 20
    if intelligence.opening_hours:
        score += 15
    return score


def _customer_trust_score(intelligence) -> int | None:
    if intelligence.rating is None and intelligence.review_count is None:
        return None

    score = 0
    if intelligence.rating is not None:
        score += round((intelligence.rating / 5) * 60)
    if intelligence.review_count is not None:
        score += min(intelligence.review_count, 100) * 30 // 100
    if intelligence.business_status:
        score += 10
    return min(100, score)


def _score_reason(intelligence, category: str) -> tuple[str, str]:
    if category == "Online Reputation":
        if intelligence.rating is None and intelligence.review_count is None:
            return (
                "No public rating or review volume was available for this assessment.",
                _confidence("discussion"),
            )
        return (
            f"The public profile shows a rating of {_display(intelligence.rating)} with {_display(intelligence.review_count)} reviews.",
            _confidence("high" if intelligence.rating is not None and intelligence.review_count is not None else "medium"),
        )

    if category == "Digital Presence":
        present = []
        missing = []
        for label, value in [
            ("website", intelligence.website),
            ("phone number", intelligence.phone),
            ("address", intelligence.address),
            ("opening hours", intelligence.opening_hours),
        ]:
            (present if value else missing).append(label)
        reason = f"Public information includes {', '.join(present)}."
        if missing:
            reason += f" Public information does not confirm {', '.join(missing)}."
        return reason, _confidence("high" if present and not missing else "medium")

    if category == "Customer Trust":
        if intelligence.rating is None and intelligence.review_count is None:
            return (
                "Customer trust cannot be estimated from reviews because no public review evidence was available.",
                _confidence("discussion"),
            )
        return (
            f"Trust indicators are based on the visible rating, review volume, and business status.",
            _confidence("high" if intelligence.rating is not None and intelligence.review_count is not None else "medium"),
        )

    if category == "Business Visibility":
        return (
            "Visibility is based on how complete and useful the public business profile appears to a prospective customer.",
            _confidence("medium"),
        )

    return (
        "Cannot be assessed from public information.",
        _confidence("discussion"),
    )


def _business_health_categories(intelligence) -> list[tuple[str, int | None, str, str]]:
    categories = [
        ("Online Reputation", _rating_score(intelligence.rating, intelligence.review_count)),
        ("Digital Presence", _digital_presence_score(intelligence)),
        ("Customer Trust", _customer_trust_score(intelligence)),
        ("Business Visibility", intelligence.profile_completeness_score),
        ("Sales Readiness", None),
    ]

    rows = []
    for name, score in categories:
        reason, confidence = _score_reason(intelligence, name)
        rows.append((name, score, reason, confidence))
    return rows


def _overall_reason(intelligence) -> str:
    positive = []
    limitation = []

    if intelligence.rating is not None:
        positive.append(f"a public rating of {_display(intelligence.rating)}")
    if intelligence.review_count is not None:
        positive.append(f"{_display(intelligence.review_count)} public reviews")
    if intelligence.website:
        positive.append("a visible website")
    if intelligence.phone:
        positive.append("a listed phone number")
    if intelligence.opening_hours:
        positive.append("published opening hours")

    for label, value in [
        ("business status", intelligence.business_status),
        ("opening hours", intelligence.opening_hours),
        ("website", intelligence.website),
        ("phone number", intelligence.phone),
    ]:
        if not value:
            limitation.append(label)

    if positive and limitation:
        return (
            f"The score reflects {', '.join(positive)}. It is limited by public information that does not confirm "
            f"{', '.join(limitation)}."
        )
    if positive:
        return f"The score reflects {', '.join(positive)}."
    return "The score is limited because the public profile does not provide enough evidence to assess the business confidently."


def _executive_summary(intelligence, opportunities: list) -> list[str]:
    strengths = []
    if intelligence.rating is not None and intelligence.rating >= 4.0:
        strengths.append("a positive public rating")
    if intelligence.review_count is not None and intelligence.review_count >= 25:
        strengths.append("meaningful review volume")
    if intelligence.website:
        strengths.append("a visible website")
    if intelligence.phone:
        strengths.append("clear public contact details")

    strength_text = ", ".join(strengths) if strengths else "some public business information"
    opportunity_text = (
        "Public information suggests specific improvement areas should be reviewed."
        if opportunities
        else "Public information does not show a major visible gap, so the discussion should test internal sales operations."
    )

    summary = (
        f"{intelligence.company_name or 'The business'} appears to have {strength_text}. "
        f"{opportunity_text} This assessment cannot confirm internal enquiry handling, follow-up speed, "
        "quotation management, sales performance reporting, or customer re-engagement without discussion. "
        "Its value is to turn public evidence into a clear agenda for a practical business improvement conversation."
    )
    return _wrap_text(summary[:900], width=92)


def _format_opening_hours(value: Any) -> str:
    text = str(value or "").strip()
    if not text or text in {"{}", "[]", "null", "None"}:
        return PUBLIC_DATA_MISSING

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return text.replace("\u202f", " ").replace("\u2013", "-")

    if not isinstance(data, dict):
        return text

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    parts = []
    for day in day_order:
        hours = data.get(day)
        if isinstance(hours, list):
            hours_text = ", ".join(str(item) for item in hours if str(item).strip())
        else:
            hours_text = str(hours or "").strip()
        if hours_text:
            parts.append(f"{day}: {hours_text}")

    return "; ".join(parts).replace("\u202f", " ").replace("\u2013", "-") or PUBLIC_DATA_MISSING


def _business_snapshot_lines(intelligence) -> list[str]:
    return (
        _wrap_lines("Company", intelligence.company_name)
        + _wrap_lines("Category", intelligence.category)
        + _wrap_lines("Phone", intelligence.phone)
        + _wrap_lines("Website", intelligence.website)
        + _wrap_lines("Address", intelligence.address)
        + _wrap_lines("Opening hours", _format_opening_hours(intelligence.opening_hours))
    )


def _strength_items(intelligence) -> list[dict[str, str]]:
    strengths = []

    if intelligence.rating is not None and intelligence.rating >= 4.0:
        strengths.append(
            {
                "observation": f"Positive Google review rating of {_display(intelligence.rating)}.",
                "impact": "A positive rating helps prospective customers feel more confident before they enquire.",
                "confidence": _confidence("high"),
            }
        )

    if intelligence.review_count is not None and intelligence.review_count >= 25:
        strengths.append(
            {
                "observation": f"Visible review base with {_display(intelligence.review_count)} public reviews.",
                "impact": "Review volume gives prospects more evidence when comparing providers.",
                "confidence": _confidence("high"),
            }
        )

    if intelligence.website:
        strengths.append(
            {
                "observation": "Public profile includes a website.",
                "impact": "A website gives prospects a place to validate services and submit or prepare enquiries.",
                "confidence": _confidence("high"),
            }
        )

    if intelligence.phone:
        strengths.append(
            {
                "observation": "Public profile includes a phone number.",
                "impact": "Clear contact details reduce friction for urgent or high-intent enquiries.",
                "confidence": _confidence("high"),
            }
        )

    if intelligence.opening_hours:
        strengths.append(
            {
                "observation": "Opening hours are publicly visible.",
                "impact": "Visible hours help customers understand when they can expect a response.",
                "confidence": _confidence("medium"),
            }
        )

    if not strengths:
        strengths.append(
            {
                "observation": "The business has some public profile information available.",
                "impact": "The available information provides a starting point for improving visibility and enquiry handling.",
                "confidence": _confidence("medium"),
            }
        )

    return strengths[:5]


def _strength_lines(intelligence) -> list[str]:
    lines = []
    for index, strength in enumerate(_strength_items(intelligence), start=1):
        lines.append(f"{index}. Observation: {strength['observation']}")
        lines.extend(_wrap_lines("   Business Impact", strength["impact"], width=88))
        lines.append(f"   Confidence: {strength['confidence']}")
    return lines


def _sorted_opportunities(opportunities: list) -> list:
    priority_order = {
        "High": 0,
        "Medium": 1,
        "Low": 2,
    }
    return sorted(
        opportunities,
        key=lambda opportunity: priority_order.get(opportunity.priority, 99),
    )


def _opportunity_confidence(priority: str) -> str:
    return _confidence("high" if priority == "High" else "medium")


def _recommended_discussion(opportunity_name: str) -> str:
    discussions = {
        "No website detected": "Discuss how prospects currently validate the business and submit website enquiries.",
        "Low review count": "Discuss whether satisfied customers are asked for reviews consistently.",
        "Poor public rating": "Discuss how customer feedback is monitored and escalated.",
        "Missing phone number": "Discuss the preferred enquiry channels and how inbound calls are tracked.",
        "Missing opening hours": "Discuss expected response times and whether public trading hours match operations.",
        "Weak profile completeness": "Discuss which public profile details should be corrected or expanded first.",
        "Incomplete digital presence": "Discuss where enquiries are captured and who owns follow-up.",
    }
    return discussions.get(
        opportunity_name,
        "Discuss whether this public finding affects enquiry conversion or sales follow-up.",
    )


def _opportunity_lines(opportunities: list) -> list[str]:
    lines = ["Opportunities Worth Exploring"]

    if not opportunities:
        lines.extend(
            _wrap_text(
                "Public information did not show a clear evidence-based external gap. The worthwhile opportunity is to confirm the internal sales process, because enquiry handling, follow-up speed, quotation management, and pipeline visibility cannot be assessed from public data.",
                width=92,
            )
        )
        lines.append("Confidence: Requires Discussion")
        lines.append("Recommended discussion: Review how new enquiries move from first contact to appointment.")
        return lines

    for index, opportunity in enumerate(_sorted_opportunities(opportunities)[:5], start=1):
        lines.append(f"{index}. Observation: {opportunity.opportunity_name}.")
        lines.extend(_wrap_lines("   Why this matters", opportunity.business_impact, width=88))
        lines.append(f"   Confidence: {_opportunity_confidence(opportunity.priority)}")
        lines.extend(_wrap_lines("   Recommended discussion", _recommended_discussion(opportunity.opportunity_name), width=88))

    return lines


def _discussion_questions(intelligence, opportunities: list) -> list[str]:
    questions = [
        "How are website enquiries managed from first contact to appointment?",
        "Who follows up missed calls and after-hours enquiries?",
        "How quickly are quotations answered?",
        "How do managers monitor sales pipeline performance?",
        "How are existing customers re-engaged?",
    ]

    opportunity_names = {opportunity.opportunity_name for opportunity in opportunities}
    if "Low review count" in opportunity_names or "Poor public rating" in opportunity_names:
        questions.append("How is customer feedback requested, tracked, and escalated?")
    if not intelligence.opening_hours or "Missing opening hours" in opportunity_names:
        questions.append("Do public trading hours match the actual response promise?")
    if not intelligence.website or "No website detected" in opportunity_names:
        questions.append("Where should prospects be sent when they want to validate services online?")
    if not intelligence.phone or "Missing phone number" in opportunity_names:
        questions.append("Which contact channels should be treated as primary sales channels?")

    return [f"- {question}" for question in questions[:8]]


def _next_step_lines(opportunities: list) -> list[str]:
    lines = [
        "1. Validate the public findings with the business owner or sales manager.",
        "   Why: Public information can show visibility gaps, but it cannot confirm internal operations.",
        "2. Review enquiry handling from call, website, WhatsApp, and form submission.",
        "   Why: Response speed and ownership usually determine whether interest becomes an appointment.",
        "3. Assess the sales process from first enquiry to quotation and follow-up.",
        "   Why: A clear process reduces lost leads and makes performance measurable.",
        "4. Identify automation opportunities that remove manual follow-up gaps.",
        "   Why: Automation is useful only where it improves consistency, tracking, or response time.",
        "5. Prioritise quick wins before larger system changes.",
        "   Why: The fastest improvements should prove value before adding complexity.",
    ]

    top = top_opportunity(opportunities)
    if top:
        lines.extend(
            [
                "",
                f"Possible Elula Solution: {top.recommended_elula_service}",
                "Why supported: This is linked to a specific public evidence indicator in the assessment and should be confirmed during discovery.",
            ]
        )

    return lines


def _business_health_lines(intelligence) -> list[str]:
    lines = [
        f"Overall Business Health: {_score_label(intelligence.profile_completeness_score)}",
        "Why this score?",
    ]
    lines.extend(_wrap_text(_overall_reason(intelligence), width=92))
    lines.append("")

    for category, score, reason, confidence in _business_health_categories(intelligence):
        lines.append(category)
        lines.append(f"Score: {_score_label(score)}")
        lines.extend(_wrap_lines("Reason", reason, width=88))
        lines.append(f"Confidence: {confidence}")
        lines.append("")

    return lines


def _methodology_lines() -> list[str]:
    return _wrap_text(
        "This assessment is based solely on publicly available information including Google Business Profile data, publicly accessible websites and other publicly available business information. It does not assess internal systems, financial performance or confidential operational information. Its purpose is to provide an independent starting point for a business improvement discussion.",
        width=92,
    )


def generate_client_report(intelligence, opportunities: list, generated_timestamp: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    company_name = intelligence.company_name or "Unknown Company"
    filename = f"{safe_filename(company_name)}_Elula_Business_Growth_Assessment.pdf"
    pdf_path = REPORT_DIR / filename
    top = top_opportunity(opportunities)

    _render_html(
        {
            "company_name": company_name,
            "generated_timestamp": generated_timestamp,
            "profile_summary": f"Overall Business Health: {intelligence.profile_completeness_score}/100",
            "digital_summary": f"Website: {_display(intelligence.website)}",
            "top_opportunity": top.opportunity_name if top else "Internal sales process requires discussion",
            "recommended_service": top.recommended_elula_service if top else PUBLIC_DATA_MISSING,
        }
    )

    lines = [
        "ELULA BUSINESS GROWTH ASSESSMENT",
        f"Business: {company_name}",
        "Prepared by: Elula Business Dynamics",
        f"Generated: {generated_timestamp}",
        "",
        "This report translates public business information into an executive discussion agenda.",
    ]

    lines.extend(_section("Executive Summary", _executive_summary(intelligence, opportunities)))
    lines.extend(_section("Business Snapshot", _business_snapshot_lines(intelligence)))
    lines.extend(_section("Business Health Score", _business_health_lines(intelligence)))
    lines.extend(_section("Business Strengths", _strength_lines(intelligence)))
    lines.extend(_section("Business Opportunities", _opportunity_lines(opportunities)))
    lines.extend(_section("Questions Worth Discussing", _discussion_questions(intelligence, opportunities)))
    lines.extend(_section("Recommended Next Steps", _next_step_lines(opportunities)))
    lines.extend(_section("Assessment Methodology", _methodology_lines()))

    _write_simple_pdf(
        path=pdf_path,
        lines=lines,
    )

    return pdf_path
