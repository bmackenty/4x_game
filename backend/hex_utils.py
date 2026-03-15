"""
backend/hex_utils.py — Hex coordinate mathematics and 3D→2D galaxy projection.

This module is pure math — no game state, no FastAPI, no side effects.
It provides two things:
  1. Axial hex coordinate helpers (shared logic with the JS hex-math.js)
  2. A function that takes the galaxy's 3D system coordinates and projects
     them onto a 2D axial hex grid for the frontend to render.

Coordinate system used: AXIAL (q, r).
  - q is the column axis (east/west)
  - r is the row axis (north-east/south-west)
  - The third cube coordinate s = -q - r (computed on demand)

Reference: https://www.redblobgames.com/grids/hexagons/
"""

import math
from typing import NamedTuple


# ---------------------------------------------------------------------------
# Axial coordinate type
# ---------------------------------------------------------------------------

class HexCoord(NamedTuple):
    q: int
    r: int


# ---------------------------------------------------------------------------
# Core axial hex math
# ---------------------------------------------------------------------------

# The six neighbour directions in axial space (flat-top hex orientation)
HEX_DIRECTIONS = [
    HexCoord( 1,  0),   # East
    HexCoord( 1, -1),   # North-East
    HexCoord( 0, -1),   # North-West
    HexCoord(-1,  0),   # West
    HexCoord(-1,  1),   # South-West
    HexCoord( 0,  1),   # South-East
]


def hex_neighbor(h: HexCoord, direction: int) -> HexCoord:
    """Return the neighbour in a given direction (0–5)."""
    d = HEX_DIRECTIONS[direction % 6]
    return HexCoord(h.q + d.q, h.r + d.r)


def cube_distance(a: HexCoord, b: HexCoord) -> int:
    """Chebyshev distance between two axial hex coords."""
    # Convert axial → cube
    a_s = -a.q - a.r
    b_s = -b.q - b.r
    return max(abs(a.q - b.q), abs(a.r - b.r), abs(a_s - b_s))


def hex_ring(center: HexCoord, radius: int) -> list[HexCoord]:
    """Return the ring of hexes exactly `radius` steps from center."""
    if radius == 0:
        return [center]
    results = []
    # Start at the hex directly south-west of center (direction 4), radius steps away
    h = HexCoord(
        center.q + HEX_DIRECTIONS[4].q * radius,
        center.r + HEX_DIRECTIONS[4].r * radius,
    )
    for i in range(6):
        for _ in range(radius):
            results.append(h)
            h = hex_neighbor(h, i)
    return results


def hex_spiral(center: HexCoord, radius: int) -> list[HexCoord]:
    """Return all hexes within `radius` of center, from the inside out."""
    results = [center]
    for r in range(1, radius + 1):
        results.extend(hex_ring(center, r))
    return results


def axial_to_pixel(q: int, r: int, size: float) -> tuple[float, float]:
    """
    Convert axial hex coordinates to pixel center position.
    Uses flat-top orientation.
    `size` is the hex radius (center to corner).
    """
    x = size * (3 / 2 * q)
    y = size * (math.sqrt(3) / 2 * q + math.sqrt(3) * r)
    return x, y


def pixel_to_axial(x: float, y: float, size: float) -> HexCoord:
    """
    Convert a pixel position back to the nearest axial hex coordinate.
    Uses flat-top orientation.
    """
    q_frac = (2 / 3 * x) / size
    r_frac = (-1 / 3 * x + math.sqrt(3) / 3 * y) / size
    return _axial_round(q_frac, r_frac)


def _axial_round(q: float, r: float) -> HexCoord:
    """Round fractional axial coords to the nearest integer hex."""
    s = -q - r
    rq, rr, rs = round(q), round(r), round(s)
    dq, dr, ds = abs(rq - q), abs(rr - r), abs(rs - s)
    if dq > dr and dq > ds:
        rq = -rr - rs
    elif dr > ds:
        rr = -rq - rs
    return HexCoord(int(rq), int(rr))


# ---------------------------------------------------------------------------
# Galaxy 3D → 2D hex projection
# ---------------------------------------------------------------------------

# The galaxy is 500 × 500 × 200 units.
# We project onto a hex grid scaled so the full 500×500 footprint fits in
# roughly a 40×40 hex area.  Scale factor: 500 / 40 = 12.5 units per hex.
GALAXY_SCALE = 12.5


def galaxy_coords_to_hex(x: float, y: float) -> HexCoord:
    """
    Project 3D galaxy coordinates (x, y, z) to a 2D axial hex.
    Z is intentionally ignored here — it's encoded as brightness in the
    renderer instead.  x and y map to the horizontal hex plane.
    """
    q = round(x / GALAXY_SCALE)
    r = round(y / GALAXY_SCALE - q / 2)  # compensate for flat-top axial shear
    return HexCoord(q, r)


def resolve_hex_collisions(systems: list[dict]) -> list[dict]:
    """
    Given a list of system dicts (each with 'x', 'y', 'z' keys), compute
    the axial hex position for each and resolve collisions by nudging
    colliding systems to the nearest empty neighbouring hex.

    Mutates each dict in-place, adding 'hex_q' and 'hex_r' keys.
    Returns the updated list.
    """
    occupied: set[HexCoord] = set()

    for system in systems:
        base = galaxy_coords_to_hex(system["x"], system["y"])
        coord = _find_free_hex(base, occupied)
        system["hex_q"] = coord.q
        system["hex_r"] = coord.r
        occupied.add(coord)

    return systems


def _find_free_hex(preferred: HexCoord, occupied: set[HexCoord]) -> HexCoord:
    """
    Return `preferred` if it's free, otherwise spiral outward until an
    unoccupied hex is found.
    """
    if preferred not in occupied:
        return preferred
    # Search in expanding rings until we find a gap
    for radius in range(1, 10):
        for candidate in hex_ring(preferred, radius):
            if candidate not in occupied:
                return candidate
    # Fallback — should never happen with a sparse galaxy map
    return preferred
