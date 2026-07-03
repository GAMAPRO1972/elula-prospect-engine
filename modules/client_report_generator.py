"""
modules/client_report_generator.py

Generates branded Elula Business Growth Assessment PDF reports.
"""

from __future__ import annotations

import html
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


def _opportunity_lines(opportunities: list) -> list[str]:
    if not opportunities:
        return [
            "No major improvement opportunity was identified from the available public data.",
            "This does not mean there is no opportunity; it means the public data reviewed did not provide enough evidence.",
        ]

    lines = []
    for opportunity in _sorted_opportunities(opportunities)[:5]:
        lines.append(f"- {opportunity.opportunity_name} ({opportunity.priority})")
        lines.extend(_wrap_lines("  Business impact", opportunity.business_impact, width=88))
        lines.extend(_wrap_lines("  Evidence-based recommendation", opportunity.recommended_elula_service, width=88))

    return lines


def _solution_lines(top) -> list[str]:
    if not top:
        return [
            "No primary Elula solution is recommended from the available public data.",
            "A short discovery call can confirm whether there are operational or sales-process gaps not visible online.",
        ]

    return [
        f"Primary recommendation: {top.recommended_elula_service}",
        "Why this may help:",
        *textwrap.wrap(
            "The recommendation is based only on the public information available in this assessment and should be confirmed in a discovery conversation.",
            width=92,
        ),
    ]


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
            "profile_summary": f"Profile completeness score: {intelligence.profile_completeness_score}/100",
            "digital_summary": f"Website: {_display(intelligence.website)}",
            "top_opportunity": top.opportunity_name if top else "No major opportunity identified",
            "recommended_service": top.recommended_elula_service if top else PUBLIC_DATA_MISSING,
        }
    )

    lines = [
        "ELULA BUSINESS GROWTH ASSESSMENT",
        f"Business: {company_name}",
        "Prepared by: Elula Business Dynamics",
        f"Generated: {generated_timestamp}",
        "",
        "This assessment is based on available public information. It is intended as a practical",
        "conversation starter for improving enquiry capture, digital presence, and sales readiness.",
    ]

    lines.extend(
        _section(
            "Executive Summary",
            textwrap.wrap(
                "Based on available public information, the assessment highlights practical improvement areas that may support better customer enquiries and follow-up. It does not make assumptions about internal operations or private business performance.",
                width=92,
            ),
        )
    )

    lines.extend(
        _section(
            "Business Snapshot",
            _wrap_lines("Company", company_name)
            + _wrap_lines("Category", intelligence.category)
            + _wrap_lines("Phone", intelligence.phone)
            + _wrap_lines("Website", intelligence.website)
            + _wrap_lines("Address", intelligence.address),
        )
    )

    lines.extend(
        _section(
            "Google Business Profile Assessment",
            _wrap_lines("Profile completeness score", f"{intelligence.profile_completeness_score}/100")
            + _wrap_lines("Google rating", intelligence.rating if intelligence.rating is not None else PUBLIC_DATA_MISSING)
            + _wrap_lines("Review count", intelligence.review_count if intelligence.review_count is not None else PUBLIC_DATA_MISSING)
            + _wrap_lines("Opening hours", intelligence.opening_hours)
            + _wrap_lines("Business status", intelligence.business_status),
        )
    )

    lines.extend(
        _section(
            "Digital Presence Assessment",
            _wrap_lines("Website", intelligence.website)
            + _wrap_lines("Primary contact number", intelligence.phone)
            + textwrap.wrap(
                "Digital presence is assessed only from public profile and website fields available to this report.",
                width=92,
            ),
        )
    )

    lines.extend(
        _section(
            "Key Opportunities",
            _opportunity_lines(opportunities),
        )
    )

    lines.extend(
        _section(
            "Recommended Next Steps",
            [
                "1. Confirm the public business profile details are accurate.",
                "2. Prioritise missing contact or enquiry-capture information.",
                "3. Review whether follow-up automation can improve response speed.",
                "4. Use a short discovery call to confirm which improvements are commercially useful.",
            ],
        )
    )

    lines.extend(
        _section(
            "How Elula Can Help",
            _solution_lines(top),
        )
    )

    _write_simple_pdf(
        path=pdf_path,
        lines=lines,
    )

    return pdf_path
