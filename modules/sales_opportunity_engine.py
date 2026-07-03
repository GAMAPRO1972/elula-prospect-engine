"""
modules/sales_opportunity_engine.py

Translates business intelligence into conservative sales opportunities.
"""

from __future__ import annotations

from dataclasses import dataclass

from integrations.google_business.models import GoogleBusinessProfile


@dataclass
class SalesOpportunity:
    opportunity_name: str
    priority: str
    business_impact: str
    recommended_elula_service: str


def identify_sales_opportunities(
    profile: GoogleBusinessProfile,
    profile_completeness_score: int,
) -> list[SalesOpportunity]:
    opportunities: list[SalesOpportunity] = []

    if not profile.website:
        opportunities.append(
            SalesOpportunity(
                opportunity_name="No website detected",
                priority="High",
                business_impact="Potential customers may struggle to validate the business online before making an enquiry.",
                recommended_elula_service="Website Refresh",
            )
        )

    if profile.review_count is not None and profile.review_count < 10:
        opportunities.append(
            SalesOpportunity(
                opportunity_name="Low review count",
                priority="Medium",
                business_impact="A low review count can reduce trust during comparison against competitors.",
                recommended_elula_service="Review Automation",
            )
        )

    if profile.rating is not None and profile.rating < 3.8:
        opportunities.append(
            SalesOpportunity(
                opportunity_name="Poor public rating",
                priority="High",
                business_impact="A weak rating may reduce enquiry conversion and damage first impressions.",
                recommended_elula_service="Review Automation",
            )
        )

    if not profile.phone:
        opportunities.append(
            SalesOpportunity(
                opportunity_name="Missing phone number",
                priority="High",
                business_impact="Customers may not have a direct way to contact the business from its profile.",
                recommended_elula_service="Elula BizHub",
            )
        )

    if not profile.opening_hours:
        opportunities.append(
            SalesOpportunity(
                opportunity_name="Missing opening hours",
                priority="Medium",
                business_impact="Unclear trading hours can reduce customer confidence and inbound enquiries.",
                recommended_elula_service="Google Business Optimisation",
            )
        )

    if profile_completeness_score < 60:
        opportunities.append(
            SalesOpportunity(
                opportunity_name="Weak profile completeness",
                priority="High",
                business_impact="Incomplete public information can reduce trust and make follow-up harder.",
                recommended_elula_service="Google Business Optimisation",
            )
        )

    if profile.website and not profile.phone:
        opportunities.append(
            SalesOpportunity(
                opportunity_name="Incomplete digital presence",
                priority="Medium",
                business_impact="The business has a website but missing contact details weaken enquiry capture.",
                recommended_elula_service="Elula BizHub",
            )
        )

    return opportunities


def top_opportunity(opportunities: list[SalesOpportunity]) -> SalesOpportunity | None:
    priority_order = {
        "High": 0,
        "Medium": 1,
        "Low": 2,
    }

    if not opportunities:
        return None

    return sorted(
        opportunities,
        key=lambda opportunity: priority_order.get(opportunity.priority, 99),
    )[0]
