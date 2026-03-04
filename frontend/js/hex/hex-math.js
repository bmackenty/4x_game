/**
 * hex/hex-math.js — Axial hex coordinate mathematics.
 *
 * Mirrors the logic in backend/hex_utils.py so that the frontend can
 * independently convert between screen pixels and hex grid positions.
 *
 * Coordinate system: AXIAL (q, r) with flat-top hexagon orientation.
 *   q = column axis (east/west)
 *   r = row axis (north-east/south-west)
 *   s = -q - r  (third cube coord, computed on demand)
 *
 * Reference: https://www.redblobgames.com/grids/hexagons/
 */


// ---------------------------------------------------------------------------
// Pixel ↔ Axial conversion  (flat-top hexagons)
// ---------------------------------------------------------------------------

/**
 * Convert axial hex coordinates to the pixel centre of that hex.
 * @param {number} q     - Axial column
 * @param {number} r     - Axial row
 * @param {number} size  - Hex radius (centre → corner), in pixels
 * @returns {{ x: number, y: number }}
 */
export function axialToPixel(q, r, size) {
  return {
    x: size * (3 / 2 * q),
    y: size * (Math.sqrt(3) / 2 * q + Math.sqrt(3) * r),
  };
}


/**
 * Convert a pixel position to the nearest axial hex coordinate.
 * @param {number} x
 * @param {number} y
 * @param {number} size  - Same hex radius used in axialToPixel
 * @returns {{ q: number, r: number }}
 */
export function pixelToAxial(x, y, size) {
  const q = (2 / 3 * x) / size;
  const r = (-1 / 3 * x + Math.sqrt(3) / 3 * y) / size;
  return axialRound(q, r);
}


/**
 * Round fractional axial coordinates to the nearest integer hex.
 * @param {number} q
 * @param {number} r
 * @returns {{ q: number, r: number }}
 */
export function axialRound(q, r) {
  const s = -q - r;
  let rq = Math.round(q);
  let rr = Math.round(r);
  let rs = Math.round(s);

  const dq = Math.abs(rq - q);
  const dr = Math.abs(rr - r);
  const ds = Math.abs(rs - s);

  if (dq > dr && dq > ds) {
    rq = -rr - rs;
  } else if (dr > ds) {
    rr = -rq - rs;
  }

  return { q: rq, r: rr };
}


// ---------------------------------------------------------------------------
// Distance
// ---------------------------------------------------------------------------

/**
 * Chebyshev distance between two axial hex coordinates.
 * @param {{ q, r }} a
 * @param {{ q, r }} b
 * @returns {number}
 */
export function cubeDistance(a, b) {
  const as = -a.q - a.r;
  const bs = -b.q - b.r;
  return Math.max(Math.abs(a.q - b.q), Math.abs(a.r - b.r), Math.abs(as - bs));
}


// ---------------------------------------------------------------------------
// Neighbourhood
// ---------------------------------------------------------------------------

/**
 * The six neighbour direction vectors in axial space (flat-top).
 * Index 0 = East, going clockwise.
 */
export const HEX_DIRECTIONS = [
  { q:  1, r:  0 },   // 0 East
  { q:  1, r: -1 },   // 1 North-East
  { q:  0, r: -1 },   // 2 North-West
  { q: -1, r:  0 },   // 3 West
  { q: -1, r:  1 },   // 4 South-West
  { q:  0, r:  1 },   // 5 South-East
];


/**
 * Return the neighbour of hex h in direction d (0–5).
 * @param {{ q, r }} h
 * @param {number}   d
 * @returns {{ q: number, r: number }}
 */
export function hexNeighbor(h, d) {
  const dir = HEX_DIRECTIONS[((d % 6) + 6) % 6];
  return { q: h.q + dir.q, r: h.r + dir.r };
}


// ---------------------------------------------------------------------------
// Rings and spirals
// ---------------------------------------------------------------------------

/**
 * Return all hexes exactly `radius` steps from center.
 * @param {{ q, r }} center
 * @param {number}   radius
 * @returns {Array<{ q: number, r: number }>}
 */
export function hexRing(center, radius) {
  if (radius === 0) return [center];

  const results = [];
  // Start at the hex radius steps in direction 4 (South-West) from centre
  let h = {
    q: center.q + HEX_DIRECTIONS[4].q * radius,
    r: center.r + HEX_DIRECTIONS[4].r * radius,
  };

  for (let i = 0; i < 6; i++) {
    for (let j = 0; j < radius; j++) {
      results.push({ ...h });
      h = hexNeighbor(h, i);
    }
  }
  return results;
}


/**
 * Return all hexes within `radius` steps of center, from inside out.
 * @param {{ q, r }} center
 * @param {number}   radius
 * @returns {Array<{ q: number, r: number }>}
 */
export function hexSpiral(center, radius) {
  const results = [center];
  for (let r = 1; r <= radius; r++) {
    results.push(...hexRing(center, r));
  }
  return results;
}


// ---------------------------------------------------------------------------
// Bounds helper — bounding box of a hex grid
// ---------------------------------------------------------------------------

/**
 * Return the pixel bounding box for a hex grid centered at (0, 0).
 * Useful for computing canvas size or centering the view.
 * @param {number} gridRadius  - Maximum hex distance from centre
 * @param {number} hexSize     - Hex radius in pixels
 * @returns {{ width: number, height: number }}
 */
export function hexGridBounds(gridRadius, hexSize) {
  const width  = hexSize * 3 * (gridRadius + 0.5);
  const height = hexSize * Math.sqrt(3) * (gridRadius + 0.5);
  return { width, height };
}
