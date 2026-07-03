"""
People enrichment foundation for Elula Prospect Engine.
"""

from integrations.people.models import Person
from integrations.people.service import PeopleEnrichmentService


__all__ = [
    "Person",
    "PeopleEnrichmentService",
]
