"""
integrations/people/parser.py

Normalization, parsing, and merge logic for people enrichment records.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from integrations.people.models import Person


def normalize_email(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text or "@" not in text:
        return ""

    return text


def normalize_phone(value: Any) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if not digits:
        return ""

    if digits.startswith("00"):
        digits = digits[2:]

    if digits.startswith("0") and len(digits) == 10:
        digits = "27" + digits[1:]

    return digits


def normalize_linkedin_url(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""

    if "linkedin.com" not in text:
        return ""

    if "://" not in text:
        text = f"https://{text}"

    parsed = urlparse(text)
    host = parsed.netloc.removeprefix("www.")
    path = re.sub(r"/+", "/", parsed.path).rstrip("/")

    if not host.endswith("linkedin.com"):
        return ""

    return f"https://{host}{path}"


def normalize_name(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""

    text = re.sub(r"[^a-zA-Z0-9]+", " ", text)
    return " ".join(text.split())


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _confidence(value: Any) -> float:
    if value in (None, ""):
        return 0.0

    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.0

    if confidence < 0:
        return 0.0

    if confidence > 1:
        return 1.0

    return confidence


def _name_parts(first_name: str, last_name: str, full_name: str) -> tuple[str, str, str]:
    if full_name and (not first_name or not last_name):
        parts = full_name.split()
        if not first_name and parts:
            first_name = parts[0]
        if not last_name and len(parts) > 1:
            last_name = " ".join(parts[1:])

    if not full_name:
        full_name = " ".join(part for part in [first_name, last_name] if part)

    return first_name, last_name, full_name


def parse_person(raw: dict[str, Any]) -> Person:
    first_name = _clean_text(
        raw.get("first_name")
        or raw.get("firstName")
        or raw.get("given_name")
    )
    last_name = _clean_text(
        raw.get("last_name")
        or raw.get("lastName")
        or raw.get("family_name")
    )
    full_name = _clean_text(
        raw.get("full_name")
        or raw.get("fullName")
        or raw.get("name")
    )

    first_name, last_name, full_name = _name_parts(
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
    )

    return Person(
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        job_title=_clean_text(raw.get("job_title") or raw.get("jobTitle") or raw.get("title")),
        email=normalize_email(raw.get("email")),
        phone=normalize_phone(raw.get("phone")),
        linkedin=normalize_linkedin_url(raw.get("linkedin") or raw.get("linkedin_url")),
        source=_clean_text(raw.get("source")),
        confidence=_confidence(raw.get("confidence")),
    )


def parse_people(raw_people: list[dict[str, Any]]) -> list[Person]:
    people = []

    for raw in raw_people:
        if isinstance(raw, dict):
            person = parse_person(raw)
            if person.full_name or person.email or person.linkedin:
                people.append(person)

    return people


def _merge_key(person: Person) -> str:
    if person.email:
        return f"email:{person.email}"

    if person.linkedin:
        return f"linkedin:{person.linkedin}"

    name = normalize_name(person.full_name)
    title = normalize_name(person.job_title)
    if name and title:
        return f"name_title:{name}:{title}"

    if name:
        return f"name:{name}"

    return ""


def _merge_sources(first: str, second: str) -> str:
    sources = []

    for source in [first, second]:
        for item in str(source or "").split(","):
            item = item.strip()
            if item and item not in sources:
                sources.append(item)

    return ", ".join(sources)


def _merge_person(existing: Person, candidate: Person) -> Person:
    primary = candidate if candidate.confidence > existing.confidence else existing
    secondary = existing if primary is candidate else candidate

    return Person(
        first_name=primary.first_name or secondary.first_name,
        last_name=primary.last_name or secondary.last_name,
        full_name=primary.full_name or secondary.full_name,
        job_title=primary.job_title or secondary.job_title,
        email=primary.email or secondary.email,
        phone=primary.phone or secondary.phone,
        linkedin=primary.linkedin or secondary.linkedin,
        source=_merge_sources(existing.source, candidate.source),
        confidence=max(existing.confidence, candidate.confidence),
    )


def merge_people(people: list[Person]) -> list[Person]:
    merged: dict[str, Person] = {}
    unkeyed: list[Person] = []

    for person in people:
        key = _merge_key(person)
        if not key:
            unkeyed.append(person)
            continue

        if key in merged:
            merged[key] = _merge_person(merged[key], person)
        else:
            merged[key] = person

    return list(merged.values()) + unkeyed
