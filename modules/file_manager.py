"""
file_manager.py

Handles input, output and archive files.
"""

from pathlib import Path

INPUT_DIR = Path("input")
ARCHIVE_DIR = Path("archive")


def find_csv_files():

    INPUT_DIR.mkdir(exist_ok=True)

    return sorted(INPUT_DIR.glob("*.csv"))


def archive_file(file_path: Path):

    ARCHIVE_DIR.mkdir(exist_ok=True)

    destination = ARCHIVE_DIR / file_path.name

    file_path.rename(destination)

    return destination