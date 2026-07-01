"""
docker_runner.py

Runs the Google Maps Scraper Docker container.
"""

from pathlib import Path
import shutil
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXPORT_DIR = PROJECT_ROOT / "exports"
INPUT_DIR = PROJECT_ROOT / "input"

DOCKER_IMAGE = "gosom/google-maps-scraper"
CACHE_VOLUME = "gmaps-playwright-cache"


def _docker_available() -> bool:
    """Return True if Docker is installed."""

    return shutil.which("docker") is not None


def _docker_running() -> bool:
    """Return True if Docker daemon is running."""

    result = subprocess.run(
        ["docker", "info"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return result.returncode == 0


def _image_exists() -> bool:

    result = subprocess.run(
        [
            "docker",
            "image",
            "inspect",
            DOCKER_IMAGE,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return result.returncode == 0


def _pull_image() -> bool:

    print(f"Pulling Docker image '{DOCKER_IMAGE}'...")

    result = subprocess.run(["docker", "pull", DOCKER_IMAGE])

    return result.returncode == 0


def run_scraper() -> bool:

    if not _docker_available():
        print("ERROR: Docker is not installed.")
        return False

    if not _docker_running():
        print("ERROR: Docker Desktop is not running.")
        return False

    queries = EXPORT_DIR / "queries.txt"

    if not queries.exists():
        print(f"ERROR: Query file not found: {queries}")
        return False

    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = INPUT_DIR / "results.csv"

    if results.exists():
        results.unlink()

    if not _image_exists():
        if not _pull_image():
            return False

    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{CACHE_VOLUME}:/opt",
        "-v",
        f"{queries}:/queries.txt:ro",
        "-v",
        f"{INPUT_DIR}:/out",
        DOCKER_IMAGE,
        "-input",
        "/queries.txt",
        "-results",
        "/out/results.csv",
        "-depth",
        "1",
        "-exit-on-inactivity",
        "3m",
    ]

    print("\nStarting Google Maps Scraper...\n")

    completed = subprocess.run(command)

    if completed.returncode != 0:
        print("ERROR: Docker container exited with an error.")
        return False

    if not results.exists():
        print("ERROR: Scraper completed but results.csv was not created.")
        return False

    print(f"\nSuccess: Results saved to {results}")

    return True