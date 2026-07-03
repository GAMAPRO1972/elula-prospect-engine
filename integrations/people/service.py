"""
integrations/people/service.py

Service layer for prospect people enrichment.
"""

from __future__ import annotations

from typing import Any

from integrations.people.models import Person
from integrations.people.parser import merge_people, parse_people
from integrations.people.providers import EmptyProvider, PeopleProvider


class PeopleEnrichmentService:
    """Finds and normalizes decision makers for a prospect."""

    def __init__(self, provider: PeopleProvider | None = None) -> None:
        self.provider = provider or EmptyProvider()

    def enrich_prospect(self, prospect: dict[str, Any]) -> list[Person]:
        raw_people = self.provider.find_people(prospect)
        people = parse_people(raw_people)
        return merge_people(people)
