"""
modules/ghl_sync.py

Orchestrates Elula BizHub synchronisation for processed prospects.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config.settings import settings
from integrations.ghl.api import GHLAPIError, ghl
from integrations.ghl.companies import companies
from integrations.ghl.importer import importer
from integrations.ghl.logger import logger
from integrations.ghl.opportunities import opportunities
from integrations.ghl.tasks import GHLTasks
from integrations.people.service import PeopleEnrichmentService
from integrations.website.service import WebsiteIntelligenceService
from modules.import_history import (
    build_match_key,
    find_import,
    load_import_history,
    record_import,
)


GHL_DIR = Path(__file__).resolve().parent.parent / "integrations" / "ghl"


@dataclass
class SyncSummary:
    companies_created: int = 0
    companies_updated: int = 0
    company_sync_unavailable: int = 0
    contacts_created: int = 0
    contacts_updated: int = 0
    opportunities_created: int = 0
    tasks_created: int = 0
    companies_would_upsert: int = 0
    contacts_would_upsert: int = 0
    opportunities_would_create: int = 0
    tasks_would_create: int = 0
    import_history_would_record: int = 0
    imported: int = 0
    skipped: int = 0
    people_checked: int = 0
    people_found: int = 0
    websites_checked: int = 0
    websites_reachable: int = 0
    website_quality_score_total: int = 0
    digital_maturity_score_total: int = 0
    failures: int = 0
    dry_run: bool = False

    def as_dict(self) -> dict[str, int | float | bool]:
        average_website_quality = 0
        average_digital_maturity = 0

        if self.websites_checked:
            average_website_quality = round(
                self.website_quality_score_total / self.websites_checked,
                2,
            )
            average_digital_maturity = round(
                self.digital_maturity_score_total / self.websites_checked,
                2,
            )

        return {
            "companies_created": self.companies_created,
            "companies_updated": self.companies_updated,
            "company_sync_unavailable": self.company_sync_unavailable,
            "contacts_created": self.contacts_created,
            "contacts_updated": self.contacts_updated,
            "opportunities_created": self.opportunities_created,
            "tasks_created": self.tasks_created,
            "companies_would_upsert": self.companies_would_upsert,
            "contacts_would_upsert": self.contacts_would_upsert,
            "opportunities_would_create": self.opportunities_would_create,
            "tasks_would_create": self.tasks_would_create,
            "import_history_would_record": self.import_history_would_record,
            "imported": self.imported,
            "skipped": self.skipped,
            "people_checked": self.people_checked,
            "people_found": self.people_found,
            "websites_checked": self.websites_checked,
            "websites_reachable": self.websites_reachable,
            "average_website_quality_score": average_website_quality,
            "average_digital_maturity_score": average_digital_maturity,
            "failures": self.failures,
            "dry_run": self.dry_run,
        }


def _load_metadata(filename: str) -> Any:
    path = GHL_DIR / filename

    if not path.exists() or path.stat().st_size == 0:
        return {}

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _normalise(value: Any) -> str:
    return str(value or "").strip().lower()


def _iter_records(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]

    if isinstance(data, dict):
        records = []
        for key, value in data.items():
            if isinstance(value, dict):
                record = dict(value)
                record.setdefault("name", key)
                records.append(record)
        return records

    return []


def _resolve_by_name(data: Any, name: str, label: str) -> dict[str, Any]:
    for record in _iter_records(data):
        names = [
            record.get("name"),
            record.get("label"),
            record.get("display_name"),
            record.get("displayName"),
        ]

        if _normalise(name) in {_normalise(item) for item in names}:
            return record

    raise ValueError(f"GHL {label} metadata not found for '{name}'.")


def _owner_match_values(record: dict[str, Any]) -> set[str]:
    values = {
        record.get("name"),
        record.get("full_name"),
        record.get("fullName"),
        record.get("email"),
        record.get("label"),
        record.get("display_name"),
        record.get("displayName"),
    }

    first_name = record.get("first_name") or record.get("firstName")
    if first_name:
        values.add(first_name)

    return {_normalise(value) for value in values if _normalise(value)}


def _owner_display_name(record: dict[str, Any]) -> str:
    return (
        record.get("name")
        or record.get("full_name")
        or record.get("fullName")
        or record.get("email")
        or "Unnamed owner"
    )


def _resolve_owner(data: Any, owner_name: str) -> dict[str, Any]:
    records = _iter_records(data)
    requested = _normalise(owner_name)

    for record in records:
        if requested in _owner_match_values(record):
            return record

    available = sorted(
        {
            _owner_display_name(record)
            for record in records
            if _owner_display_name(record)
        }
    )
    available_text = ", ".join(available) if available else "none"

    raise ValueError(
        f"GHL owner metadata not found for '{owner_name}'. "
        f"Available owners: {available_text}."
    )


def _resolve_stage(stages_data: Any, pipeline_id: str, campaign) -> dict[str, Any]:
    stage_name = (
        campaign.config.get("stage")
        or campaign.config.get("pipeline_stage")
        or campaign.config.get("opportunity_stage")
    )

    if stage_name:
        return _resolve_by_name(stages_data, stage_name, "stage")

    for record in _iter_records(stages_data):
        is_default = bool(record.get("default") or record.get("is_default"))
        same_pipeline = (
            record.get("pipeline_id") == pipeline_id
            or record.get("pipelineId") == pipeline_id
        )

        if is_default and (
            same_pipeline
            or not record.get("pipeline_id")
            and not record.get("pipelineId")
        ):
            return record

    pipeline_stages = [
        record
        for record in _iter_records(stages_data)
        if record.get("pipeline_id") == pipeline_id
        or record.get("pipelineId") == pipeline_id
    ]

    if pipeline_stages:
        return sorted(
            pipeline_stages,
            key=lambda record: (
                record.get("position")
                if isinstance(record.get("position"), int)
                else 0
            ),
        )[0]

    raise ValueError("GHL stage metadata not found. Add a campaign stage or default stage.")


def _record_id(record: dict[str, Any], label: str) -> str:
    record_id = record.get("id") or record.get(f"{label}_id") or record.get(f"{label}Id")

    if not record_id:
        raise ValueError(f"GHL {label} metadata is missing an id.")

    return record_id


def _extract_contact_id(response: dict[str, Any]) -> str:
    if "id" in response:
        return response["id"]

    contact = response.get("contact")
    if isinstance(contact, dict) and contact.get("id"):
        return contact["id"]

    raise ValueError("GHL contact response did not include a contact id.")


def _extract_company_id(record: dict[str, Any]) -> str:
    company_id = (
        record.get("id")
        or record.get("_id")
        or record.get("companyId")
        or record.get("businessId")
    )

    if not company_id:
        raise ValueError("Elula BizHub company response did not include a company id.")

    return str(company_id)


def _extract_opportunity_id(response: dict[str, Any]) -> str:
    if "id" in response:
        return response["id"]

    opportunity = response.get("opportunity")
    if isinstance(opportunity, dict) and opportunity.get("id"):
        return opportunity["id"]

    raise ValueError("GHL opportunity response did not include an opportunity id.")


def _extract_task_id(response: dict[str, Any]) -> str | None:
    if not isinstance(response, dict):
        return None

    if response.get("id"):
        return response["id"]

    task = response.get("task")
    if isinstance(task, dict) and task.get("id"):
        return task["id"]

    return None


def _resolve_tags(tags_data: Any, campaign) -> list[str]:
    tag_names = campaign.config.get("tags", [])

    if isinstance(tag_names, str):
        tag_names = [tag_names]

    tag_ids = []
    for tag_name in tag_names:
        record = _resolve_by_name(tags_data, tag_name, "tag")
        tag_ids.append(_record_id(record, "tag"))

    return tag_ids


def _build_company_payload(
    prospect: dict[str, Any],
    owner_id: str,
    campaign,
) -> dict[str, Any]:
    payload = {
        "locationId": settings.ghl_location_id,
        "name": prospect.get("company_name", ""),
        "phone": prospect.get("phone", ""),
        "email": prospect.get("email", ""),
        "website": prospect.get("website", ""),
        "address": prospect.get("address", ""),
        "source": campaign.config.get("source", settings.default_source),
        "assignedTo": owner_id,
    }

    custom_fields = {
        "industry": prospect.get("category", ""),
        "campaign_id": campaign.config.get("campaign_id", ""),
        "campaign_name": campaign.config.get("campaign_name", getattr(campaign, "name", "")),
        "primary_product": prospect.get("primary_product", ""),
        "secondary_products": prospect.get("secondary_products", ""),
        "review_rating": prospect.get("review_rating", ""),
        "review_count": prospect.get("review_count", ""),
        "opening_hours": prospect.get("opening_hours", ""),
        "business_status": prospect.get("business_status", ""),
        "opportunity_score": prospect.get("opportunity_score", ""),
        "opportunity_reasons": prospect.get("opportunity_reasons", ""),
    }

    payload["customFields"] = [
        {"key": key, "field_value": value}
        for key, value in custom_fields.items()
        if value not in ("", None)
    ]

    return {
        key: value
        for key, value in payload.items()
        if value not in ("", None, [])
    }


def _build_contact_payload(
    prospect: dict[str, Any],
    owner_id: str,
    tag_ids: list[str],
    campaign,
) -> dict[str, Any]:
    payload = {
        "locationId": settings.ghl_location_id,
        "companyName": prospect.get("company_name", ""),
        "email": prospect.get("email", ""),
        "phone": prospect.get("phone", ""),
        "address1": prospect.get("address", ""),
        "source": campaign.config.get("source", settings.default_source),
        "assignedTo": owner_id,
    }

    if prospect.get("website"):
        payload["website"] = prospect["website"]

    if tag_ids:
        payload["tags"] = tag_ids

    return {key: value for key, value in payload.items() if value not in ("", None)}


def _has_contact_identity(prospect: dict[str, Any]) -> bool:
    return bool(str(prospect.get("email") or "").strip() or str(prospect.get("phone") or "").strip())


def _sync_company_if_available(
    prospect: dict[str, Any],
    owner_id: str,
    campaign,
    summary: SyncSummary,
) -> str | None:
    company_payload = _build_company_payload(prospect, owner_id, campaign)

    try:
        company_record, company_created = companies.sync_company(company_payload)
    except GHLAPIError as exc:
        summary.company_sync_unavailable += 1
        logger.warning(
            "Company sync unavailable for prospect '%s'. Elula BizHub returned: %s. "
            "Continuing with contact, opportunity, and task sync where contact data exists.",
            prospect.get("company_name", "Unknown"),
            exc,
        )
        return None

    company_id = _extract_company_id(company_record)

    if company_created:
        summary.companies_created += 1
        logger.info(
            "Company created for prospect '%s': %s.",
            prospect.get("company_name", "Unknown"),
            company_id,
        )
    else:
        summary.companies_updated += 1
        logger.info(
            "Company updated for prospect '%s': %s.",
            prospect.get("company_name", "Unknown"),
            company_id,
        )

    return company_id


def _opportunity_name(prospect: dict[str, Any]) -> str:
    company = prospect.get("company_name") or "Unknown Company"
    product = prospect.get("primary_product") or settings.default_primary_product
    return f"{company} - {product}"


def _check_people(
    prospect: dict[str, Any],
    service: PeopleEnrichmentService,
    summary: SyncSummary,
) -> None:
    people = service.enrich_prospect(prospect)
    people_found = len(people)

    summary.people_checked += 1
    summary.people_found += people_found

    logger.info(
        "%sPeople enrichment checked for prospect '%s'. people_found=%s.",
        "DRY RUN: " if summary.dry_run else "",
        prospect.get("company_name", "Unknown"),
        people_found,
    )


def _check_website(
    prospect: dict[str, Any],
    service: WebsiteIntelligenceService,
    summary: SyncSummary,
) -> None:
    if not prospect.get("website"):
        return

    intelligence = service.analyze_prospect(prospect)

    summary.websites_checked += 1
    if intelligence.is_reachable:
        summary.websites_reachable += 1

    summary.website_quality_score_total += intelligence.website_quality_score
    summary.digital_maturity_score_total += intelligence.digital_maturity_score

    logger.info(
        "%sWebsite intelligence checked for prospect '%s'. "
        "website_reachable=%s, website_quality_score=%s, digital_maturity_score=%s.",
        "DRY RUN: " if summary.dry_run else "",
        prospect.get("company_name", "Unknown"),
        intelligence.is_reachable,
        intelligence.website_quality_score,
        intelligence.digital_maturity_score,
    )


def _sync_single_prospect(
    prospect: dict[str, Any],
    campaign,
    metadata: dict[str, Any],
    task_service: GHLTasks,
    summary: SyncSummary,
) -> dict[str, str | None]:
    pipeline = _resolve_by_name(metadata["pipelines"], campaign.config.get("pipeline"), "pipeline")
    pipeline_id = _record_id(pipeline, "pipeline")

    stage = _resolve_stage(metadata["stages"], pipeline_id, campaign)
    stage_id = _record_id(stage, "stage")

    owner = _resolve_owner(metadata["owners"], prospect.get("owner"))
    owner_id = _record_id(owner, "owner")

    tag_ids = _resolve_tags(metadata["tags"], campaign)

    company_id = _sync_company_if_available(
        prospect=prospect,
        owner_id=owner_id,
        campaign=campaign,
        summary=summary,
    )

    if not _has_contact_identity(prospect):
        if not company_id:
            raise ValueError(
                "Prospect has no phone or email and company sync is unavailable, "
                "so no Elula BizHub record can be created safely."
            )

        logger.info(
            "Company synced for prospect '%s', but contact, opportunity, and task were skipped "
            "because no phone or email is available.",
            prospect.get("company_name", "Unknown"),
        )
        return {
            "company_id": company_id,
            "contact_id": None,
            "opportunity_id": None,
            "task_id": None,
        }

    contact_payload = _build_contact_payload(prospect, owner_id, tag_ids, campaign)
    existing_contact = importer.find_contact(
        email=contact_payload.get("email"),
        phone=contact_payload.get("phone"),
    )

    contact_response = importer.sync_contact(contact_payload)
    contact_id = existing_contact["id"] if existing_contact else _extract_contact_id(contact_response)

    if existing_contact:
        summary.contacts_updated += 1
        logger.info("Contact updated for prospect '%s': %s.", prospect.get("company_name", "Unknown"), contact_id)
    else:
        summary.contacts_created += 1
        logger.info("Contact created for prospect '%s': %s.", prospect.get("company_name", "Unknown"), contact_id)

    opportunity_response = opportunities.create_opportunity(
        contact_id=contact_id,
        pipeline_id=pipeline_id,
        stage_id=stage_id,
        owner_id=owner_id,
        name=_opportunity_name(prospect),
    )
    opportunity_id = _extract_opportunity_id(opportunity_response)
    summary.opportunities_created += 1
    logger.info("Opportunity created for prospect '%s': %s.", prospect.get("company_name", "Unknown"), opportunity_id)

    task_response = task_service.create_initial_call(
        contact_id=contact_id,
        owner_id=owner_id,
    )
    task_id = _extract_task_id(task_response)
    summary.tasks_created += 1
    logger.info("Task created for prospect '%s': %s.", prospect.get("company_name", "Unknown"), task_id)

    return {
        "company_id": company_id,
        "contact_id": contact_id,
        "opportunity_id": opportunity_id,
        "task_id": task_id,
    }


def _dry_run_single_prospect(
    prospect: dict[str, Any],
    campaign,
    metadata: dict[str, Any],
    summary: SyncSummary,
) -> None:
    pipeline = _resolve_by_name(metadata["pipelines"], campaign.config.get("pipeline"), "pipeline")
    pipeline_id = _record_id(pipeline, "pipeline")

    stage = _resolve_stage(metadata["stages"], pipeline_id, campaign)
    _record_id(stage, "stage")

    owner = _resolve_owner(metadata["owners"], prospect.get("owner"))
    owner_id = _record_id(owner, "owner")

    tag_ids = _resolve_tags(metadata["tags"], campaign)
    _build_company_payload(prospect, owner_id, campaign)
    _build_contact_payload(prospect, owner_id, tag_ids, campaign)

    summary.companies_would_upsert += 1

    if _has_contact_identity(prospect):
        summary.contacts_would_upsert += 1
        summary.opportunities_would_create += 1
        summary.tasks_would_create += 1

    summary.import_history_would_record += 1

    logger.info(
        "DRY RUN: Would upsert company%s in pipeline '%s' and record import history "
        "for prospect '%s'.",
        ", upsert contact, create opportunity, and create initial task"
        if _has_contact_identity(prospect)
        else "; contact, opportunity, and task would be skipped because no phone or email is available",
        pipeline_id,
        prospect.get("company_name", "Unknown"),
    )


def sync_prospects(
    prospects: list[dict[str, Any]],
    campaign,
    dry_run: bool = False,
) -> dict[str, int | float | bool]:
    """
    Synchronise processed prospects with Elula BizHub.
    """

    summary = SyncSummary(dry_run=dry_run)
    task_service = GHLTasks(ghl)
    people_service = PeopleEnrichmentService()
    website_service = WebsiteIntelligenceService()
    import_history = load_import_history(read_only=dry_run)
    metadata = {
        "pipelines": _load_metadata("pipelines.json"),
        "stages": _load_metadata("stages.json"),
        "owners": _load_metadata("owners.json"),
        "tags": _load_metadata("tags.json"),
    }

    if dry_run:
        logger.info("DRY RUN: Elula BizHub write calls and import history writes are disabled.")

    for prospect in prospects:
        company_name = prospect.get("company_name", "Unknown")

        try:
            _check_people(
                prospect=prospect,
                service=people_service,
                summary=summary,
            )
            _check_website(
                prospect=prospect,
                service=website_service,
                summary=summary,
            )

            match_type, match_value, match_key = build_match_key(prospect)
            existing_import = find_import(import_history, match_key)

            if existing_import:
                summary.skipped += 1
                logger.info(
                    "%sSkipped previously imported prospect '%s' using %s match '%s'. "
                    "Original contact: %s, opportunity: %s.",
                    "DRY RUN: " if dry_run else "",
                    company_name,
                    match_type,
                    match_value,
                    existing_import.get("contact_id", ""),
                    existing_import.get("opportunity_id", ""),
                )
                continue

            if dry_run:
                _dry_run_single_prospect(
                    prospect=prospect,
                    campaign=campaign,
                    metadata=metadata,
                    summary=summary,
                )
                continue

            sync_result = _sync_single_prospect(
                prospect=prospect,
                campaign=campaign,
                metadata=metadata,
                task_service=task_service,
                summary=summary,
            )

            record_import(
                ledger=import_history,
                prospect=prospect,
                campaign=campaign,
                match_type=match_type,
                match_value=match_value,
                match_key=match_key,
                contact_id=sync_result["contact_id"] or "",
                opportunity_id=sync_result["opportunity_id"] or "",
                task_id=sync_result["task_id"],
            )
            summary.imported += 1

            logger.info(
                "Imported prospect '%s' using %s match '%s'. Company: %s, contact: %s, opportunity: %s.",
                company_name,
                match_type,
                match_value,
                sync_result["company_id"],
                sync_result["contact_id"],
                sync_result["opportunity_id"],
            )

        except (GHLAPIError, ValueError, KeyError, json.JSONDecodeError) as exc:
            summary.failures += 1
            logger.exception(
                "%sFailed to synchronise prospect '%s': %s",
                "DRY RUN: " if dry_run else "",
                company_name,
                exc,
            )

    return summary.as_dict()
