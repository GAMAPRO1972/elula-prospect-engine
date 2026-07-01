from modules.campaign_manager import load_campaign
from modules.query_exporter import export_queries
from modules.docker_runner import run_scraper


def run(industry, campaign):

    campaign_obj = load_campaign(
        industry,
        campaign
    )

    export_queries(campaign_obj)

    success = run_scraper()

    if success:
        print("\nScraper completed successfully.")
    else:
        print("\nScraper failed.")