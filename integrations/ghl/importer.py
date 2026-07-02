"""
integrations/ghl/importer.py

High-level contact synchronisation for GoHighLevel.
"""

from __future__ import annotations

from typing import Any

from config.settings import settings
from integrations.ghl.api import GHLAPIError, ghl
from integrations.ghl.logger import logger


class ContactImporter:
    """Creates or updates contacts in GoHighLevel."""

    def __init__(self) -> None:
        self.client = ghl

    def find_contact(self, email: str | None = None, phone: str | None = None) -> dict[str, Any] | None:
        query = email or phone

        if not query:
            return None

        result = self.client.get(
            "contacts/",
            params={
                "locationId": settings.ghl_location_id,
                "query": query,
            },
        )

        contacts = result.get("contacts", [])
        if contacts:
            return contacts[0]

        return None

    def upsert_contact(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload = {
            **payload,
            "locationId": payload.get("locationId") or settings.ghl_location_id,
        }

        logger.info("Upserting contact: %s", payload.get("companyName", "Unknown"))
        return self.client.post("contacts/upsert", payload)

    def create_contact(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload = {
            **payload,
            "locationId": payload.get("locationId") or settings.ghl_location_id,
        }

        logger.info("Creating contact: %s", payload.get("companyName", "Unknown"))
        return self.client.post("contacts/", payload)

    def update_contact(self, contact_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        payload = {
            **payload,
            "locationId": payload.get("locationId") or settings.ghl_location_id,
        }

        logger.info("Updating contact: %s", contact_id)
        return self.client.put(f"contacts/{contact_id}", payload)

    def sync_contact(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create or update a contact and return the GHL response."""
        try:
            return self.upsert_contact(payload)

        except GHLAPIError:
            logger.exception("Failed to synchronise contact.")
            raise


importer = ContactImporter()
