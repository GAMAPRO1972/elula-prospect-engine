"""
modules/file_manager.py

Functions for locating input CSV files and archiving processed files.
"""

from pathlib import Path
from datetime import datetime


INPUT_DIR = Path("input")
ARCHIVE_DIR = Path("archive")


def find_csv_files():
    """
    Return all CSV files waiting to be processed.
    """
    return sorted(INPUT_DIR.glob("*.csv"))


def archive_file(file_path: Path):
    """
    Archive a processed CSV using a timestamp so that
    previous archives are never overwritten.
    """

    ARCHIVE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    destination = (
        ARCHIVE_DIR
        / f"{file_path.stem}_{timestamp}{file_path.suffix}"
    )

    file_path.rename(destination)

    print(f"Archived: {destination}")

    return destination