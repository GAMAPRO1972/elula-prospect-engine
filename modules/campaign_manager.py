"""
campaign_manager.py

Loads campaign definitions and keyword lists for the
Elula Prospect Engine.
"""

from pathlib import Path
import json


# Root folder for all campaigns
CAMPAIGN_DIR = Path(__file__).resolve().parent.parent / "campaigns"


class Campaign:
    """
    Represents a campaign consisting of:
    - Configuration (.json)
    - Search keywords (.txt)
    """

    def __init__(self, name, config, keywords):
        self.name = name
        self.config = config
        self.keywords = keywords


def load_campaign(industry: str, campaign: str) -> Campaign:
    """
    Load a campaign by industry and name.

    Example:
        load_campaign("security", "gauteng")
    """

    folder = CAMPAIGN_DIR / industry

    json_file = folder / f"{campaign}.json"
    txt_file = folder / f"{campaign}.txt"

    if not json_file.exists():
        raise FileNotFoundError(
            f"Campaign configuration not found: {json_file}"
        )

    if not txt_file.exists():
        raise FileNotFoundError(
            f"Campaign keyword file not found: {txt_file}"
        )

    # Load campaign configuration
    with open(json_file, "r", encoding="utf-8") as file:
        config = json.load(file)

    # Load search keywords
    with open(txt_file, "r", encoding="utf-8") as file:
        keywords = [
            line.strip()
            for line in file.readlines()
            if line.strip()
        ]

    return Campaign(
        config["campaign_name"],
        config,
        keywords
    )


def list_campaigns():
    """
    Return a list of all available campaigns.
    """

    campaigns = []

    for industry_folder in CAMPAIGN_DIR.iterdir():

        if not industry_folder.is_dir():
            continue

        for json_file in industry_folder.glob("*.json"):

            campaigns.append({
                "industry": industry_folder.name,
                "campaign": json_file.stem
            })

    return campaigns
