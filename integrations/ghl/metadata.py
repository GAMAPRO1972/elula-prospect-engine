"""
integrations/ghl/metadata.py

Fetches live GoHighLevel metadata and stores it locally.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from config.settings import settings, validate_ghl_settings
from integrations.ghl.api import GHLAPIError, ghl


GHL_DIR = Path(__file__).resolve().parent
PIPELINES_PATH = GHL_DIR / "pipelines.json"
STAGES_PATH = GHL_DIR / "stages.json"
OWNERS_PATH = GHL_DIR / "owners.json"


def _sort_value(record: dict[str, Any]) -> int:
    for key in ("position", "order", "sortOrder", "stageOrder"):
        value = record.get(key)
        if isinstance(value, int):
            return value
    return 0


def _extract_pipelines(response: Any) -> list[dict[str, Any]]:
    if isinstance(response, dict):
        pipelines = response.get("pipelines")
        if isinstance(pipelines, list):
            return [item for item in pipelines if isinstance(item, dict)]

    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]

    return []


def _extract_users(response: Any) -> list[dict[str, Any]]:
    if isinstance(response, dict):
        for key in ("users", "teamMembers", "members", "data"):
            users = response.get(key)
            if isinstance(users, list):
                return [item for item in users if isinstance(item, dict)]

    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]

    return []


def _normalise_pipeline(pipeline: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": pipeline.get("id"),
        "name": pipeline.get("name"),
        "locationId": pipeline.get("locationId") or settings.ghl_location_id,
        "position": pipeline.get("position"),
    }


def _normalise_stage(
    stage: dict[str, Any],
    pipeline: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    pipeline_id = pipeline.get("id")

    return {
        "id": stage.get("id"),
        "name": stage.get("name"),
        "pipeline_id": pipeline_id,
        "pipelineId": pipeline_id,
        "pipeline_name": pipeline.get("name"),
        "position": stage.get("position"),
        "default": index == 0,
    }


def _normalise_owner(user: dict[str, Any]) -> dict[str, Any]:
    first_name = user.get("firstName") or user.get("first_name") or ""
    last_name = user.get("lastName") or user.get("last_name") or ""
    full_name = (
        user.get("name")
        or user.get("fullName")
        or user.get("full_name")
        or " ".join(part for part in (first_name, last_name) if part).strip()
    )
    email = user.get("email") or ""

    return {
        "id": user.get("id") or user.get("_id") or user.get("userId"),
        "name": full_name or first_name or email,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "email": email,
        "locationId": user.get("locationId") or settings.ghl_location_id,
    }


def _write_json(path: Path, data: list[dict[str, Any]]) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _normalise(value: Any) -> str:
    return str(value or "").strip().lower()


def fetch_live_pipeline_metadata() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Fetch pipelines and their stages from the configured GHL location.
    """
    validate_ghl_settings()

    response = ghl.get(
        "opportunities/pipelines",
        params={"locationId": settings.ghl_location_id},
    )

    raw_pipelines = _extract_pipelines(response)
    pipelines = []
    stages = []

    for raw_pipeline in sorted(raw_pipelines, key=_sort_value):
        pipeline = _normalise_pipeline(raw_pipeline)
        if not pipeline.get("id") or not pipeline.get("name"):
            continue

        pipelines.append(pipeline)

        raw_stages = raw_pipeline.get("stages", [])
        if not isinstance(raw_stages, list):
            continue

        for index, raw_stage in enumerate(sorted(raw_stages, key=_sort_value)):
            if not isinstance(raw_stage, dict):
                continue

            stage = _normalise_stage(raw_stage, pipeline, index)
            if stage.get("id") and stage.get("name"):
                stages.append(stage)

    return pipelines, stages


def fetch_live_owner_metadata(company_id: str | None = None) -> list[dict[str, Any]]:
    """
    Fetch team users from the configured GHL location.
    """
    validate_ghl_settings()

    company_id = _resolve_company_id(company_id)

    response = ghl.get(
        "users/search",
        params={
            "companyId": company_id,
            "locationId": settings.ghl_location_id,
        },
    )

    owners = []
    for raw_user in _extract_users(response):
        owner = _normalise_owner(raw_user)
        if owner.get("id") and (
            owner.get("name")
            or owner.get("first_name")
            or owner.get("email")
        ):
            owners.append(owner)

    return sorted(
        owners,
        key=lambda owner: _normalise(owner.get("name") or owner.get("email")),
    )


def _resolve_company_id(value: str | None = None) -> str:
    company_id = (value or os.getenv("GHL_COMPANY_ID", "")).strip()
    if company_id:
        return company_id

    try:
        response = ghl.get(f"locations/{settings.ghl_location_id}")
    except GHLAPIError as exc:
        raise ValueError(
            "GHL users/search requires companyId. Set GHL_COMPANY_ID in .env "
            "or pass --company-id because the configured token cannot read "
            f"the location record to discover it automatically. API response: {exc}"
        ) from exc

    location = response.get("location", response) if isinstance(response, dict) else {}

    company_id = (
        location.get("companyId")
        or location.get("company_id")
        or location.get("agencyId")
    )

    if not company_id:
        raise ValueError(
            "GHL companyId could not be resolved. Set GHL_COMPANY_ID in .env."
        )

    return company_id


def refresh_pipeline_metadata(
    required_pipeline: str | None = None,
    company_id: str | None = None,
) -> dict[str, int]:
    """
    Refresh local GHL metadata from live GHL data.
    """
    pipelines, stages = fetch_live_pipeline_metadata()
    owners = fetch_live_owner_metadata(company_id=company_id)

    if required_pipeline:
        pipeline_names = {_normalise(pipeline.get("name")) for pipeline in pipelines}
        if _normalise(required_pipeline) not in pipeline_names:
            raise ValueError(
                f"Live GHL pipeline metadata not found for '{required_pipeline}'."
            )

    _write_json(PIPELINES_PATH, pipelines)
    _write_json(STAGES_PATH, stages)
    _write_json(OWNERS_PATH, owners)

    return {
        "pipelines": len(pipelines),
        "stages": len(stages),
        "owners": len(owners),
    }
