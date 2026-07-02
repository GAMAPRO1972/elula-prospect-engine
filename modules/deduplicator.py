"""
modules/deduplicator.py

Remove duplicate prospects while keeping the
most complete record.
"""

from typing import List


def record_score(record: dict) -> int:
    """
    Score a record based on how complete it is.
    """

    score = 0

    fields = [
        "website",
        "email",
        "phone",
        "address",
        "review_rating",
        "review_count",
    ]

    for field in fields:
        if record.get(field):
            score += 1

    return score


def deduplicate(prospects: List[dict]) -> List[dict]:
    """
    Remove duplicate prospects.

    Matching priority:

    1. Website
    2. Phone
    3. Company Name
    """

    unique = {}

    for prospect in prospects:

        if prospect.get("website"):
            key = "W:" + prospect["website"].lower()

        elif prospect.get("phone"):
            key = "P:" + prospect["phone"]

        else:
            key = "C:" + prospect["company_name"].lower()

        if key not in unique:

            unique[key] = prospect

        else:

            if record_score(prospect) > record_score(unique[key]):
                unique[key] = prospect

    return list(unique.values())