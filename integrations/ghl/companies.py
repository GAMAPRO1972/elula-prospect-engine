"""
integrations/ghl/companies.py

Company management for Elula BizHub.

HighLevel exposes this CRM company record through the documented Business API.
The adapter keeps Elula terminology as Company because that is the B2B data
model used by Elula BizHub operators.
"""

from __future__ import annotations

import json
from typing import Any

from config.settings import settings
from integrations.ghl.api import GHLAPIError, ghl
from integrations.ghl.logger import logger


def _company_records(response: Any) -> list[dict[str, Any]]:
    if isinstance(response, dict):
        for key in ("companies", "businesses", "data", "items", "results"):
            records = response.get(key)
            if isinstance(records, list):
                return [item for item in records if isinstance(item, dict)]

        company = response.get("company") or response.get("business")
        if isinstance(company, dict):
            return [company]

    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]

    return []


def _company_id(record: dict[str, Any]) -> str | None:
    value = (
        record.get("id")
        or record.get("_id")
        or record.get("companyId")
        or record.get("businessId")
    )
    return str(value) if value else None


def _company_name(record: dict[str, Any]) -> str:
    return str(
        record.get("name")
        or record.get("companyName")
        or record.get("businessName")
        or ""
    ).strip()


def _extract_company(response: Any) -> dict[str, Any]:
    records = _company_records(response)
    if records:
        return records[0]

    if isinstance(response, dict) and _company_id(response):
        return response

    raise ValueError("Elula BizHub company response did not include a company record.")


def _exact_company_name_match(record: dict[str, Any], company_name: str) -> bool:
    return _company_name(record) == str(company_name or "").strip()


def _debug_payload_enabled() -> bool:
    return settings.log_level.upper() == "DEBUG"


def _business_payload(
    payload: dict[str, Any],
    *,
    include_location_id: bool = True,
) -> dict[str, Any]:
    business_payload = {
        "name": payload.get("name"),
    }

    if include_location_id:
        business_payload["locationId"] = (
            payload.get("locationId") or settings.ghl_location_id
        )

    for field in ("phone", "website"):
        if payload.get(field) not in ("", None):
            business_payload[field] = payload[field]

    return business_payload


class CompanyManager:
    """Creates, updates, and de-duplicates companies in Elula BizHub."""

    def __init__(self) -> None:
        self.client = ghl

    def find_company_by_name(self, company_name: str) -> dict[str, Any] | None:
        name = str(company_name or "").strip()
        if not name:
            return None

        response = self.client.get(
            "businesses/",
            params={
                "locationId": settings.ghl_location_id,
            },
        )

        for record in _company_records(response):
            if _exact_company_name_match(record, name):
                return record

        return None

    def create_company(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload = _business_payload(payload)
        existing_company = self.find_company_by_name(str(payload.get("name") or ""))
        if existing_company:
            company_id = _company_id(existing_company)
            if not company_id:
                raise ValueError("Existing Elula BizHub company is missing an id.")

            logger.info("Company already exists, updating instead: %s", company_id)
            return self.update_company(company_id, payload)

        logger.info("Creating company: %s", payload.get("name", "Unknown"))
        if _debug_payload_enabled():
            print("POST /businesses/ payload:")
            print(json.dumps(payload, indent=2, ensure_ascii=True, sort_keys=True))
        return self.client.post("businesses/", payload)

    def update_company(self, company_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        payload = _business_payload(payload, include_location_id=False)

        logger.info("Updating company: %s", company_id)
        return self.client.put(f"businesses/{company_id}", payload)

    def sync_company(self, payload: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        """
        Create or update an Elula BizHub company.

        Returns the company record and a boolean indicating whether it was newly
        created.
        """

        name = str(payload.get("name") or "").strip()
        if not name:
            raise ValueError("Company name is required to sync an Elula BizHub company.")

        existing_company = self.find_company_by_name(name)
        if existing_company:
            company_id = _company_id(existing_company)
            if not company_id:
                raise ValueError("Existing Elula BizHub company is missing an id.")

            response = self.update_company(company_id, payload)
            records = _company_records(response)
            return (records[0] if records else existing_company, False)

        response = self.create_company(payload)
        return _extract_company(response), True


companies = CompanyManager()
