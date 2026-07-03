"""
integrations/people/models.py

Data models for prospect decision-maker enrichment.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Person:
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    job_title: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    source: str = ""
    confidence: float = 0.0
