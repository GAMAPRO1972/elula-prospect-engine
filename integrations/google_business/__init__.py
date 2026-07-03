"""
Google Business Profile intelligence foundation.
"""

from integrations.google_business.models import GoogleBusinessProfile
from integrations.google_business.parser import parse_google_business_profile


__all__ = [
    "GoogleBusinessProfile",
    "parse_google_business_profile",
]
