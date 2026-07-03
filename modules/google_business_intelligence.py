"""
modules/google_business_intelligence.py

Generates Google Business Profile intelligence and internal reports.
"""

from __future__ import annotations

import csv
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from integrations.google_business.client import GoogleBusinessClient
from modules.client_report_generator import generate_client_report
from modules.sales_opportunity_engine import SalesOpportunity, identify_sales_opportunities, top_opportunity


REPORTS_DIR = Path("reports")
CSV_REPORT_PATH = REPORTS_DIR / "business_intelligence_report.csv"
XLSX_REPORT_PATH = REPORTS_DIR / "business_intelligence_report.xlsx"


@dataclass
class BusinessIntelligenceResult:
    company_name: str = ""
    category: str = ""
    rating: float | None = None
    review_count: int | None = None
    phone: str = ""
    website: str = ""
    address: str = ""
    opening_hours: str = ""
    business_status: str = ""
    profile_completeness_score: int = 0
    opportunity_score: int = 0
    intelligence_timestamp: str = ""
    warnings: list[str] = field(default_factory=list)
    opportunities: list[SalesOpportunity] = field(default_factory=list)
    owner: str = ""
    primary_product: str = ""


def _score_profile_completeness(profile) -> int:
    fields = [
        profile.company_name,
        profile.category,
        profile.rating is not None,
        profile.review_count is not None,
        profile.phone,
        profile.website,
        profile.address,
        profile.opening_hours,
        profile.business_status,
    ]
    completed = sum(1 for field in fields if bool(field))
    return round((completed / len(fields)) * 100)


def _score_opportunity(opportunities: list[SalesOpportunity], completeness_score: int) -> int:
    if not opportunities:
        return 0

    score = max(0, 100 - completeness_score)
    for opportunity in opportunities:
        if opportunity.priority == "High":
            score += 20
        elif opportunity.priority == "Medium":
            score += 10
        elif opportunity.priority == "Low":
            score += 5
    return min(score, 100)


def generate_google_business_intelligence(prospect: dict[str, Any]) -> BusinessIntelligenceResult:
    client = GoogleBusinessClient()
    profile = client.build_profile(prospect)
    completeness_score = _score_profile_completeness(profile)
    opportunities = identify_sales_opportunities(profile, completeness_score)

    return BusinessIntelligenceResult(
        company_name=profile.company_name,
        category=profile.category,
        rating=profile.rating,
        review_count=profile.review_count,
        phone=profile.phone,
        website=profile.website,
        address=profile.address,
        opening_hours=profile.opening_hours,
        business_status=profile.business_status,
        profile_completeness_score=completeness_score,
        opportunity_score=_score_opportunity(opportunities, completeness_score),
        intelligence_timestamp=datetime.now(timezone.utc).isoformat(),
        warnings=profile.warnings,
        opportunities=opportunities,
        owner=prospect.get("owner", ""),
        primary_product=prospect.get("primary_product", ""),
    )


def _report_rows(results: list[BusinessIntelligenceResult]) -> list[dict[str, Any]]:
    rows = []
    for result in results:
        top = top_opportunity(result.opportunities)
        rows.append(
            {
                "company_name": result.company_name,
                "phone": result.phone,
                "website": result.website,
                "address": result.address,
                "category": result.category,
                "rating": result.rating if result.rating is not None else "",
                "review_count": result.review_count if result.review_count is not None else "",
                "profile_completeness_score": result.profile_completeness_score,
                "opportunity_score": result.opportunity_score,
                "top_opportunity": top.opportunity_name if top else "No major opportunity identified",
                "recommended_primary_service": top.recommended_elula_service if top else "",
                "assigned_owner": result.owner,
                "primary_product": result.primary_product,
                "generated_timestamp": result.intelligence_timestamp,
            }
        )
    return rows


def _write_csv(rows: list[dict[str, Any]]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else [
        "company_name",
        "phone",
        "website",
        "address",
        "category",
        "rating",
        "review_count",
        "profile_completeness_score",
        "opportunity_score",
        "top_opportunity",
        "recommended_primary_service",
        "assigned_owner",
        "primary_product",
        "generated_timestamp",
    ]

    with CSV_REPORT_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def _sheet_xml(rows: list[dict[str, Any]]) -> str:
    headers = list(rows[0].keys()) if rows else [
        "company_name",
        "phone",
        "website",
        "address",
        "category",
        "rating",
        "review_count",
        "profile_completeness_score",
        "opportunity_score",
        "top_opportunity",
        "recommended_primary_service",
        "assigned_owner",
        "primary_product",
        "generated_timestamp",
    ]
    data_rows = [headers] + [[row.get(header, "") for header in headers] for row in rows]
    sheet_rows = []
    for row_index, row in enumerate(data_rows, start=1):
        cells = []
        for column_index, value in enumerate(row, start=1):
            cell_ref = f"{_column_name(column_index)}{row_index}"
            cells.append(
                f'<c r="{cell_ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
            )
        sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')

    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(sheet_rows)}</sheetData>'
        '</worksheet>'
    )


def _write_xlsx(rows: list[dict[str, Any]]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(XLSX_REPORT_PATH, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '</Types>',
        )
        archive.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>',
        )
        archive.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Business Intelligence" sheetId="1" r:id="rId1"/></sheets>'
            '</workbook>',
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>',
        )
        archive.writestr("xl/worksheets/sheet1.xml", _sheet_xml(rows))


def generate_business_intelligence_reports(prospects: list[dict[str, Any]]) -> dict[str, Any]:
    results = [generate_google_business_intelligence(prospect) for prospect in prospects]
    rows = _report_rows(results)

    _write_csv(rows)
    _write_xlsx(rows)

    pdf_paths = [
        generate_client_report(result, result.opportunities, result.intelligence_timestamp)
        for result in results
    ]

    return {
        "records": len(results),
        "csv_report": str(CSV_REPORT_PATH),
        "xlsx_report": str(XLSX_REPORT_PATH),
        "client_reports": [str(path) for path in pdf_paths],
    }
