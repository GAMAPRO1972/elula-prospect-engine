"""
integrations/ghl/opportunities.py

Opportunity management for GoHighLevel.
"""

from __future__ import annotations

from typing import Any

from config.settings import settings
from integrations.ghl.api import GHLAPIError, ghl
from integrations.ghl.logger import logger


class OpportunityManager:
    """Creates and updates opportunities."""

    def __init__(self) -> None:
        self.client = ghl

    def create_opportunity(
        self,
        contact_id: str,
        pipeline_id: str,
        stage_id: str,
        owner_id: str,
        name: str,
        value: float = 0.0,
        status: str = "open",
    ) -> dict[str, Any]:

        payload = {
            "locationId": settings.ghl_location_id,
            "contactId": contact_id,
            "pipelineId": pipeline_id,
            "pipelineStageId": stage_id,
            "assignedTo": owner_id,
            "name": name,
            "status": status,
            "monetaryValue": value,
        }

        logger.info("Creating opportunity for contact %s", contact_id)
        return self.client.post("opportunities/", payload)

    def update_opportunity(
        self,
        opportunity_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:

        logger.info("Updating opportunity %s", opportunity_id)
        return self.client.put(f"opportunities/{opportunity_id}", payload)

    def move_stage(
        self,
        opportunity_id: str,
        stage_id: str,
    ) -> dict[str, Any]:

        logger.info(
            "Moving opportunity %s to stage %s",
            opportunity_id,
            stage_id,
        )

        return self.update_opportunity(
            opportunity_id,
            {
                "pipelineStageId": stage_id,
            },
        )

    def assign_owner(
        self,
        opportunity_id: str,
        owner_id: str,
    ) -> dict[str, Any]:

        logger.info(
            "Assigning owner %s to opportunity %s",
            owner_id,
            opportunity_id,
        )

        return self.update_opportunity(
            opportunity_id,
            {
                "assignedTo": owner_id,
            },
        )


opportunities = OpportunityManager()
