"""
assignment_engine.py

Determines who owns a lead and which Elula product
should be offered first.
"""


def assign_lead(campaign):

    industry = campaign.config.get("industry", "").lower()

    # Default values
    owner = "Gary"
    primary_product = "Elula BizHub"
    secondary_products = ["Red XRay"]

    if industry == "security":
        owner = "Gary"
        primary_product = "Elula BizHub"
        secondary_products = [
            "Elula Mobile",
            "Red XRay"
        ]

    elif industry == "construction":
        owner = "Rob"
        primary_product = "Elula Compliance"
        secondary_products = [
            "Elula Skills",
            "Red XRay"
        ]

    elif industry == "manufacturing":
        owner = "Rob"
        primary_product = "Elula Skills"
        secondary_products = [
            "Elula Compliance",
            "Red XRay"
        ]

    return {
        "owner": owner,
        "primary_product": primary_product,
        "secondary_products": secondary_products
    }