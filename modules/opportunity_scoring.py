"""
opportunity_scoring.py

Calculates an opportunity score for each prospect.
"""


def calculate_score(prospect: dict) -> tuple[int, list[str]]:

    score = 0
    reasons = []

    if prospect.get("website"):
        score += 20
        reasons.append("Website")

    if prospect.get("email"):
        score += 20
        reasons.append("Email")

    if prospect.get("phone"):
        score += 15
        reasons.append("Phone")

    try:
        rating = float(prospect.get("review_rating") or 0)

        if rating >= 4:
            score += 15
            reasons.append("Good Google Rating")

    except ValueError:
        pass

    try:
        reviews = int(float(prospect.get("review_count") or 0))

        if reviews >= 20:
            score += 15
            reasons.append("Established Reputation")

    except ValueError:
        pass

    return score, reasons