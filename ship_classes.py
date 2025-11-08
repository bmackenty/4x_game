"""
Ship class registry scaffold.

The previous catalog has been intentionally cleared so that the new attribute
schema can drive future balancing and content creation.
"""

from __future__ import annotations

from typing import Dict, Mapping

ship_classes: Dict[str, Mapping[str, object]] = {}

__all__ = ["ship_classes"]
