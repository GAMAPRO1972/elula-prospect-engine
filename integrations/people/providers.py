"""
integrations/people/providers.py

Provider interfaces for people enrichment.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PeopleProvider(ABC):
    """Base interface for future people enrichment providers."""

    name = "base"

    @abstractmethod
    def find_people(self, prospect: dict[str, Any]) -> list[dict[str, Any]]:
        """Return raw person-like records for a prospect."""


class EmptyProvider(PeopleProvider):
    """Safe default provider. It performs no external calls."""

    name = "empty"

    def find_people(self, prospect: dict[str, Any]) -> list[dict[str, Any]]:
        return []


class ManualProvider(PeopleProvider):
    """Manual in-memory provider for controlled local tests."""

    name = "manual"

    def __init__(self, records: list[dict[str, Any]] | None = None) -> None:
        self.records = records or []

    def find_people(self, prospect: dict[str, Any]) -> list[dict[str, Any]]:
        return list(self.records)
