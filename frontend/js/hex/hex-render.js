/**
 * hex/hex-render.js — Canvas rendering for hex grids.
 *
 * Provides functions to draw hexes, system icons, fog of war, faction colour
 * tints, ether zone overlays, and selection highlights onto an HTML5 Canvas.
 *
 * All drawing functions take a CanvasRenderingContext2D as their first
 * argument and respect the current canvas transform (pan + zoom).
 *
 * Coordinate convention: flat-top hexagons, axial (q, r).
 */

import { axialToPixel, HEX_DIRECTIONS } from "./hex-math.js";


// ---------------------------------------------------------------------------
// Hex rendering constants
// ---------------------------------------------------------------------------

/** Default hex radius (centre → corner) in pixels for the galaxy map */
export const GALAXY_HEX_SIZE = 22;

/** Default hex radius for the planet colony map */
export const PLANET_HEX_SIZE = 32;


// ---------------------------------------------------------------------------
// Colour maps
// ---------------------------------------------------------------------------

/** Background fill colour for each star system type */
const SYSTEM_TYPE_COLORS = {
  "Core World":    "#0d1a30",
  "Urban":         "#0d1e2e",
  "Military":      "#1a1200",
  "Scientific":    "#001a1a",
  "Trading":       "#1a1400",
  "Frontier":      "#0a1020",
  "Outpost":       "#0a0f18",
  default:         "#0a0e1a",
};

/** Glyph used as the star icon for each system type */
const SYSTEM_GLYPHS = {
  "Core World":  "★",
  "Urban":       "◉",
  "Military":    "⬡",
  "Scientific":  "✦",
  "Trading":     "◈",
  "Frontier":    "·",
  "Outpost":     "○",
  default:       "·",
};

/** Terrain fill colours for planet colony hexes */
export const TERRAIN_COLORS = {
  plains:    "#1a2e1a",
  forest:    "#0f2010",
  ocean:     "#0a1826",
  mountains: "#2a2318",
  tundra:    "#1e2830",
  volcanic:  "#2a0e00",
  crystal:   "#101830",
  void:      "#08080e",
  desert:    "#2a1e08",
  coastal:   "#0f1e28",
  geothermal:"#1e1208",
};

/** Improvement icons (emoji / ASCII) drawn inside colony hex tiles */
const IMPROVEMENT_ICONS = {
  "Mineral Extractor":    "⛏",
  "Biofarm Complex":      "🌾",
  "Research Node":        "⬡",
  "Ether Conduit":        "✦",
  "Defense Array":        "⚔",
  "Trade Nexus":          "◈",
  "Neural Institute":     "◉",
  "Quantum Relay":        "⊕",
  "Bio-Synthesis Lab":    "⚗",
  "Deep Core Drill":      "⬢",
  "Etheric Purifier":     "✧",
  "Void Anchor":          "⊛",
  "Population Hub":       "⌂",
  "Solar Harvester":      "☀",
  "Xenobiology Station":  "☿",
};


// ---------------------------------------------------------------------------
// Core hex drawing
// ---------------------------------------------------------------------------

/**
 * Draw a single flat-top hexagon at pixel centre (cx, cy).
 * @param {CanvasRenderingContext2D} ctx
 * @param {number} cx          - Centre x
 * @param {number} cy          - Centre y
 * @param {number} size        - Radius (centre → corner)
 * @param {string} fillColor   - CSS colour string
 * @param {string} strokeColor - CSS colour string
 * @param {number} [strokeWidth=1]
 */
export function drawHex(ctx, cx, cy, size, fillColor, strokeColor, strokeWidth = 1) {
  ctx.beginPath();
  for (let i = 0; i < 6; i++) {
    // Flat-top: first corner is at 0° (east)
    const angle = (Math.PI / 180) * (60 * i);
    const px = cx + size * Math.cos(angle);
    const py = cy + size * Math.sin(angle);
    i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
  }
  ctx.closePath();
  ctx.fillStyle   = fillColor;
  ctx.fill();
  ctx.strokeStyle = strokeColor;
  ctx.lineWidth   = strokeWidth;
  ctx.stroke();
}


// ---------------------------------------------------------------------------
// Territory rendering helpers (player colony influence zones)
// ---------------------------------------------------------------------------

/**
 * Build a Set of "q,r" string keys for every hex that falls inside the
 * player's territory: each colonised system plus its 6 immediate neighbours.
 * @param {Array} systems - systems array from /api/galaxy/map
 * @returns {Set<string>}
 */
function _buildTerritorySet(systems) {
  const set = new Set();
  for (const sys of systems) {
    if (!sys.has_player_colony) continue;
    const cq = sys.hex_q, cr = sys.hex_r;
    // Centre hex
    set.add(`${cq},${cr}`);
    // Rings 1 and 2 — standard hex-ring walk (Red Blob Games algorithm):
    // start `radius` steps in direction 4, then walk all 6 sides.
    for (const radius of [1, 2]) {
      let hq = cq + HEX_DIRECTIONS[4].q * radius;
      let hr = cr + HEX_DIRECTIONS[4].r * radius;
      for (let side = 0; side < 6; side++) {
        for (let step = 0; step < radius; step++) {
          set.add(`${hq},${hr}`);
          hq += HEX_DIRECTIONS[side].q;
          hr += HEX_DIRECTIONS[side].r;
        }
      }
    }
  }
  return set;
}

/**
 * Draw a very subtle teal wash over all territory hexes.
 * Must be called BEFORE the system hex tiles are drawn so the tiles
 * render on top and the wash shows only in the negative space.
 * @param {CanvasRenderingContext2D} ctx
 * @param {Array}  systems
 * @param {number} size  - GALAXY_HEX_SIZE
 */
function _drawTerritoryFills(ctx, systems, size) {
  const territory = _buildTerritorySet(systems);
  if (!territory.size) return;

  ctx.fillStyle = "rgba(0,212,170,0.07)";
  for (const key of territory) {
    const [q, r] = key.split(",").map(Number);
    const { x: cx, y: cy } = axialToPixel(q, r, size);
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 180) * (60 * i);
      const px = cx + size * Math.cos(angle);
      const py = cy + size * Math.sin(angle);
      i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fill();
  }
}

/**
 * Draw teal border lines on every edge of a territory hex that faces a
 * non-territory hex.  Call AFTER system tiles so borders sit in the gaps.
 * @param {CanvasRenderingContext2D} ctx
 * @param {Array}  systems
 * @param {number} size
 */
function _drawTerritoryBorders(ctx, systems, size) {
  const territory = _buildTerritorySet(systems);
  if (!territory.size) return;

  ctx.strokeStyle = "rgba(0,212,170,0.80)";
  ctx.lineWidth   = 2.5;
  ctx.lineCap     = "round";

  for (const key of territory) {
    const [q, r] = key.split(",").map(Number);
    const { x: cx, y: cy } = axialToPixel(q, r, size);

    for (let e = 0; e < 6; e++) {
      // For flat-top hexes rendered in Y-down screen space, edge e (between
      // corners e and e+1) faces the neighbour in direction (6-e)%6, NOT e.
      const dir = HEX_DIRECTIONS[(6 - e) % 6];
      // Skip interior edges (neighbour is also inside territory)
      if (territory.has(`${q + dir.q},${r + dir.r}`)) continue;

      // Draw the shared edge between corner e and corner (e+1)%6.
      // Use (size - 0.5) so the line sits in the pixel gap between tiles.
      const a1 = (Math.PI / 180) * (60 * e);
      const a2 = (Math.PI / 180) * (60 * (e + 1));
      const r1 = size - 0.5;
      ctx.beginPath();
      ctx.moveTo(cx + r1 * Math.cos(a1), cy + r1 * Math.sin(a1));
      ctx.lineTo(cx + r1 * Math.cos(a2), cy + r1 * Math.sin(a2));
      ctx.stroke();
    }
  }
}


// ---------------------------------------------------------------------------
// Galaxy map rendering
// ---------------------------------------------------------------------------

/**
 * Render the full galaxy hex map onto a canvas.
 *
 * @param {HTMLCanvasElement} canvas
 * @param {Array}  systems          - Array from /api/galaxy/map
 * @param {object} viewState        - { panX, panY, zoom, selectedSystemName, shipHex,
 *                                      stations, selectedStationName }
 * @param {Map}    factionColors    - faction name → CSS colour
 */
export function renderGalaxyMap(canvas, systems, viewState, factionColors) {
  const ctx = canvas.getContext("2d");
  const { panX, panY, zoom, selectedSystemName, stations = [], selectedStationName } = viewState;

  // Clear to deep space background
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#05090f";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Draw a subtle star-field (static dots for perf — seeded by position)
  _drawStarfield(ctx, canvas.width, canvas.height, viewState);

  // Apply pan + zoom transform
  ctx.save();
  ctx.translate(panX + canvas.width / 2, panY + canvas.height / 2);
  ctx.scale(zoom, zoom);

  const size = GALAXY_HEX_SIZE;

  // Territory fills drawn first so hex tiles render on top of the wash
  _drawTerritoryFills(ctx, systems, size);

  for (const sys of systems) {
    const { x: px, y: py } = axialToPixel(sys.hex_q, sys.hex_r, size);

    // Faction colour tint
    const factionColor = sys.controlling_faction
      ? (factionColors.get(sys.controlling_faction) || "rgba(0,212,170,0.08)")
      : null;

    // Background fill
    const bgColor = SYSTEM_TYPE_COLORS[sys.type] || SYSTEM_TYPE_COLORS.default;

    // Fog-of-war: unvisited systems are dark with no label
    const visited = sys.visited;

    // Border colour: selected = bright teal, colonised = solid teal,
    //                faction-owned = faction dim, default = dark
    let borderColor = "#1a2a4a";
    let borderWidth = 0.5;
    if (sys.name === selectedSystemName) {
      borderColor = "#00d4aa";
      borderWidth = 1.5;
    } else if (sys.has_player_colony) {
      borderColor = "rgba(0,212,170,0.85)";
      borderWidth = 1.2;
    } else if (sys.controlling_faction) {
      borderColor = factionColor || "#1a3a2a";
    }

    // Draw hex tile
    drawHex(ctx, px, py, size - 1, bgColor, borderColor, borderWidth);

    // Faction colour overlay (very subtle tint)
    if (factionColor && visited) {
      const overlayColor = factionColor.replace(/[\d.]+\)$/, "0.10)");
      drawHex(ctx, px, py, size - 1, overlayColor, "transparent", 0);
    }

    // Selection glow ring
    if (sys.name === selectedSystemName) {
      ctx.beginPath();
      for (let i = 0; i < 6; i++) {
        const angle = (Math.PI / 180) * (60 * i);
        const hx = px + (size + 3) * Math.cos(angle);
        const hy = py + (size + 3) * Math.sin(angle);
        i === 0 ? ctx.moveTo(hx, hy) : ctx.lineTo(hx, hy);
      }
      ctx.closePath();
      ctx.strokeStyle = "rgba(0,212,170,0.5)";
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    if (!visited) {
      // Fog-of-war: just a faint dot
      ctx.fillStyle = "rgba(90,122,154,0.15)";
      ctx.beginPath();
      ctx.arc(px, py, 2, 0, Math.PI * 2);
      ctx.fill();
      continue;
    }

    // Star glyph
    const glyph = SYSTEM_GLYPHS[sys.type] || SYSTEM_GLYPHS.default;
    ctx.fillStyle = _systemGlyphColor(sys);
    ctx.font = `${Math.max(10, size * 0.7)}px "Courier New", monospace`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(glyph, px, py);

    // System name label (only when zoom is high enough to be readable)
    if (zoom >= 0.7) {
      ctx.fillStyle = sys.name === selectedSystemName ? "#00d4aa" : "rgba(200, 216, 232, 0.7)";
      ctx.font = `${Math.max(7, Math.floor(8 * zoom))}px "Courier New", monospace`;
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillText(sys.name, px, py + size * 0.55);
    }

    // Colony indicator — small ⌂ icon in the upper-right corner of the hex
    if (sys.has_player_colony) {
      const iconSize = Math.max(7, size * 0.42);
      ctx.fillStyle   = "#00d4aa";
      ctx.font        = `${iconSize}px "Courier New", monospace`;
      ctx.textAlign   = "center";
      ctx.textBaseline = "middle";
      // Position at ~60% of radius toward the upper-right corner (angle 30°)
      const iconAngle = (Math.PI / 180) * 30;
      ctx.fillText("⌂", px + size * 0.60 * Math.cos(iconAngle),
                       py + size * 0.60 * Math.sin(iconAngle));
    }
  }

  // Territory borders — drawn after all hex tiles so lines sit in the gaps
  _drawTerritoryBorders(ctx, systems, size);

  // -----------------------------------------------------------------------
  // Deep-space station markers — drawn after systems, before ship
  // -----------------------------------------------------------------------
  for (const st of stations) {
    const { x: stx, y: sty } = axialToPixel(st.hex_q, st.hex_r, size);
    const isSelected = st.name === selectedStationName;

    // Hex background — deep amber for stations
    drawHex(ctx, stx, sty, size - 1, "#1a1200", isSelected ? "#d4a800" : "#5a4000",
            isSelected ? 1.5 : 0.8);

    // Selection glow
    if (isSelected) {
      ctx.beginPath();
      for (let i = 0; i < 6; i++) {
        const angle = (Math.PI / 180) * (60 * i);
        ctx.lineTo(stx + (size + 3) * Math.cos(angle), sty + (size + 3) * Math.sin(angle));
      }
      ctx.closePath();
      ctx.strokeStyle = "rgba(212,168,0,0.55)";
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Station glyph — ⊕ (looks like a station cross)
    ctx.fillStyle = isSelected ? "#d4a800" : "#a07800";
    ctx.font = `${Math.max(9, size * 0.6)}px "Courier New", monospace`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("⊕", stx, sty);

    // Station name label when zoomed in enough
    if (zoom >= 0.7) {
      ctx.fillStyle = isSelected ? "#d4a800" : "rgba(200,168,80,0.7)";
      ctx.font = `${Math.max(7, Math.floor(8 * zoom))}px "Courier New", monospace`;
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillText(st.name, stx, sty + size * 0.55);
    }
  }

  // -----------------------------------------------------------------------
  // Player ship marker — drawn on top of all system hexes
  // -----------------------------------------------------------------------
  // viewState.shipHex = { q, r } from galaxy.js (computed from ship.coordinates)
  if (viewState.shipHex) {
    const { q: sq, r: sr } = viewState.shipHex;
    const { x: spx, y: spy } = axialToPixel(sq, sr, size);

    // Bright teal filled circle as a backdrop
    ctx.beginPath();
    ctx.arc(spx, spy, size * 0.38, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(0, 212, 170, 0.88)";
    ctx.fill();
    ctx.strokeStyle = "#00ffcc";
    ctx.lineWidth = 1;
    ctx.stroke();

    // Ship chevron glyph in the centre
    ctx.fillStyle = "#050910";
    ctx.font = `bold ${Math.round(size * 0.46)}px "Courier New", monospace`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("▲", spx, spy);
  }

  ctx.restore();
}


/**
 * Return a colour for the star glyph based on system properties.
 */
function _systemGlyphColor(sys) {
  if (sys.type === "Core World")   return "#d4a800";
  if (sys.type === "Military")     return "#cc5555";
  if (sys.type === "Scientific")   return "#00aaff";
  if (sys.type === "Trading")      return "#00d4aa";
  if (sys.threat_level >= 7)       return "#cc3333";
  return "#c8d8e8";
}


/**
 * Draw a simple pseudo-random star-field as background texture.
 * Stars are deterministic (seeded by screen position) so they don't flicker
 * during pan/zoom.
 */
function _drawStarfield(ctx, width, height, viewState) {
  // Use a small set of fixed star positions for performance
  const STARS = [
    [0.12, 0.08], [0.34, 0.22], [0.56, 0.11], [0.78, 0.44],
    [0.23, 0.67], [0.45, 0.55], [0.67, 0.33], [0.89, 0.77],
    [0.11, 0.88], [0.55, 0.77], [0.73, 0.55], [0.28, 0.38],
    [0.91, 0.21], [0.38, 0.91], [0.62, 0.62], [0.08, 0.50],
  ];
  ctx.fillStyle = "rgba(200, 216, 232, 0.25)";
  for (const [fx, fy] of STARS) {
    ctx.beginPath();
    ctx.arc(fx * width, fy * height, 0.8, 0, Math.PI * 2);
    ctx.fill();
  }
}


// ---------------------------------------------------------------------------
// Planet colony hex map rendering
// ---------------------------------------------------------------------------

/**
 * Render a planet's hex tile grid for the colony view.
 *
 * @param {HTMLCanvasElement} canvas
 * @param {Array}  tiles          - Array of { q, r, terrain, improvement, is_claimed }
 * @param {object} viewState      - { panX, panY, zoom, selectedQ, selectedR }
 */
export function renderColonyMap(canvas, tiles, viewState) {
  const ctx = canvas.getContext("2d");
  const { panX, panY, zoom, selectedQ, selectedR } = viewState;

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#050810";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.save();
  ctx.translate(panX + canvas.width / 2, panY + canvas.height / 2);
  ctx.scale(zoom, zoom);

  const size = PLANET_HEX_SIZE;

  for (const tile of tiles) {
    const { x: px, y: py } = axialToPixel(tile.q, tile.r, size);

    const terrainColor = TERRAIN_COLORS[tile.terrain] || TERRAIN_COLORS.plains;

    // Unclaimed tiles are dim
    const fillColor = tile.is_claimed
      ? terrainColor
      : _dimColor(terrainColor, 0.4);

    // Border: selected = teal, improvement present = slightly brighter
    let borderColor = "#1a2a3a";
    let borderWidth = 0.5;
    if (tile.q === selectedQ && tile.r === selectedR) {
      borderColor = "#00d4aa";
      borderWidth = 1.5;
    } else if (tile.improvement) {
      borderColor = "#224433";
      borderWidth = 0.8;
    }

    drawHex(ctx, px, py, size - 1, fillColor, borderColor, borderWidth);

    // Improvement icon
    if (tile.improvement) {
      const icon = IMPROVEMENT_ICONS[tile.improvement] || "?";
      ctx.fillStyle = "#00d4aa";
      ctx.font = `${size * 0.55}px "Courier New", monospace`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(icon, px, py);
    }
  }

  ctx.restore();
}


/**
 * Darken a hex colour by multiplying its brightness.
 * Very simple: converts to rgba with reduced alpha over a dark background.
 */
function _dimColor(color, opacity) {
  // Just return the color with low opacity — the canvas background is dark
  return color + Math.round(opacity * 255).toString(16).padStart(2, "0");
}


// ---------------------------------------------------------------------------
// Hover tooltip hit test
// ---------------------------------------------------------------------------

/**
 * Given a canvas-relative click position, return the axial hex coord that
 * was clicked, accounting for the current pan + zoom transform.
 *
 * @param {number} canvasX
 * @param {number} canvasY
 * @param {number} canvasWidth
 * @param {number} canvasHeight
 * @param {object} viewState   - { panX, panY, zoom }
 * @param {number} hexSize
 * @returns {{ q: number, r: number }}
 */
export function canvasPointToHex(canvasX, canvasY, canvasWidth, canvasHeight, viewState, hexSize) {
  // Invert the canvas transform:  translate(panX + W/2, panY + H/2) scale(zoom)
  const { panX, panY, zoom } = viewState;
  const worldX = (canvasX - (panX + canvasWidth  / 2)) / zoom;
  const worldY = (canvasY - (panY + canvasHeight / 2)) / zoom;

  // Import pixelToAxial inline to avoid circular dependency
  const q = (2 / 3 * worldX) / hexSize;
  const r = (-1 / 3 * worldX + Math.sqrt(3) / 3 * worldY) / hexSize;

  // axialRound
  const s = -q - r;
  let rq = Math.round(q), rr = Math.round(r), rs = Math.round(s);
  const dq = Math.abs(rq - q), dr = Math.abs(rr - r), ds = Math.abs(rs - s);
  if (dq > dr && dq > ds) rq = -rr - rs;
  else if (dr > ds) rr = -rq - rs;

  return { q: rq, r: rr };
}
