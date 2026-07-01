"""
modules/cleaner.py

Functions for cleaning and standardising prospect data.
"""

import re


COMPANY_SUFFIXES = [
    "(PTY) LTD",
    "(PTY)LTD",
    "PTY LTD",
    "PTY. LTD.",
    "PTY",
    "LIMITED",
    "LTD",
    "CC",
    "INC",
]


def clean_company_name(name: str) -> str:
    """
    Standardise company names.
    """

    if not name:
        return ""

    company = name.upper().strip()

    for suffix in COMPANY_SUFFIXES:
        company = company.replace(suffix, "")

    company = re.sub(r"\s+", " ", company)

    return company.title().strip()


def clean_phone(phone: str) -> str:
    """
    Convert phone numbers into a consistent format.
    """

    if not phone:
        return ""

    phone = re.sub(r"\D", "", phone)

    if phone.startswith("27"):
        return "+" + phone

    if phone.startswith("0"):
        return "+27" + phone[1:]

    return phone


def clean_website(url: str) -> str:
    """
    Remove protocol and www.
    """

    if not url:
        return ""

    url = url.lower().strip()

    url = url.replace("https://", "")
    url = url.replace("http://", "")
    url = url.replace("www.", "")

    return url.rstrip("/")
def clean_row(row: dict) -> dict:
    """
    Clean a raw row from any acquisition source.
    """

    cleaned = dict(row)

    cleaned["title"] = clean_company_name(
        row.get("title", "")
    )

    cleaned["phone"] = clean_phone(
        row.get("phone", "")
    )

    cleaned["website"] = clean_website(
        row.get("website", "")
    )

    return cleaned