"""
Classes (Occupations) for 7019 - Character Creation

All class data is stored in lore/classes.json.
This module loads that file and exposes the same public API as before,
so all existing callers (pyqt_interface.py, etc.) are unaffected.
"""

import json
import pathlib

# ---------------------------------------------------------------------------
# Load raw data from lore/classes.json
# ---------------------------------------------------------------------------

_LORE_PATH = pathlib.Path(__file__).parent / "lore" / "classes.json"

with _LORE_PATH.open(encoding="utf-8") as _f:
    classes: dict = json.load(_f)

# ---------------------------------------------------------------------------
# Helper functions — pure logic, no data
# ---------------------------------------------------------------------------

def get_available_classes(background_name: str) -> list:
    """Return all class names available for the given background."""
    return [
        class_name
        for class_name, class_data in classes.items()
        if background_name in class_data["available_backgrounds"]
    ]


def get_class_info(class_name: str) -> dict:
    """Return the full data dict for a single class, or None if not found."""
    return classes.get(class_name, None)


def get_classes_by_stat(stat_name: str) -> list:
    """Return all class names that list stat_name as a primary stat."""
    return [
        class_name
        for class_name, class_data in classes.items()
        if stat_name in class_data["primary_stats"]
    ]


def get_classes_by_career(career_path: str) -> list:
    """Return all class names whose career path contains the given string (case-insensitive)."""
    return [
        class_name
        for class_name, class_data in classes.items()
        if career_path.lower() in class_data["career_path"].lower()
    ]
