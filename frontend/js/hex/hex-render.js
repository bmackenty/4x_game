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

/** Default hex radius for the system interior map (star + planets + stations) */
export const SYSTEM_HEX_SIZE = 36;


// ---------------------------------------------------------------------------
// Colour maps
// ---------------------------------------------------------------------------

/** Background fill colour for each star system type */
const SYSTEM_TYPE_COLORS = {
  "Core World":    "#152848",
  "Urban":         "#152c44",
  "Military":      "#281c00",
  "Scientific":    "#002828",
  "Trading":       "#281e00",
  "Frontier":      "#101830",
  "Outpost":       "#101620",
  default:         "#101420",
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

// ---------------------------------------------------------------------------
// Z-elevation band helpers
// ---------------------------------------------------------------------------

/**
 * Classify a system's z coordinate into one of five galactic elevation bands.
 *
 * Bands are defined by standard-deviation distance from the dataset mean:
 *   "high"  z >  mean + 2σ   — well above the galactic plane
 *   "above" z >  mean + 1σ   — above the plane
 *   "plane" |z - mean| ≤ 1σ  — at the galactic midplane
 *   "below" z <  mean - 1σ   — below the plane
 *   "deep"  z <  mean - 2σ   — well below the galactic plane
 *
 * @param {number}                         z
 * @param {{ mean: number, std: number }|null} zStats
 * @returns {"high"|"above"|"plane"|"below"|"deep"}
 */
function _zBand(z, zStats) {
  if (!zStats || zStats.std === 0) return "plane";
  const d = (z - zStats.mean) / zStats.std;
  if (d >  2) return "high";
  if (d >  1) return "above";
  if (d < -2) return "deep";
  if (d < -1) return "below";
  return "plane";
}

/**
 * Visual style for each z-elevation band.
 * dot  — colour of the small elevation dot drawn below the star glyph (null = none)
 * ring — colour of the outer elevation ring drawn for extreme bands (null = none)
 */
const Z_BAND_STYLES = {
  high:  { dot: "#00e5ff", ring: "rgba(0,229,255,0.50)"  },  // cyan  — high above plane
  above: { dot: "#4fc3f7", ring: null                    },  // pale blue
  plane: { dot: null,      ring: null                    },  // no indicator at midplane
  below: { dot: "#ffb74d", ring: null                    },  // amber
  deep:  { dot: "#ff7043", ring: "rgba(255,112,67,0.45)" },  // orange-red — deep below plane
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
// ---------------------------------------------------------------------------
// Deep space object rendering helpers
// ---------------------------------------------------------------------------

/** Glyph and colour for each DSO type */
const DSO_RENDER = {
  derelict:      { glyph: "⊘", color: "rgba(220,120,30,0.85)",  bg: "#1a0a00" },
  anomaly:       { glyph: "✦", color: "rgba(160,80,255,0.90)",  bg: "#0e0020" },
  resource_node: { glyph: "◈", color: "rgba(0,210,100,0.90)",   bg: "#001a08" },
  outpost_site:  { glyph: "○", color: "rgba(0,170,255,0.85)",   bg: "#001020" },
};

/**
 * Draw deep space object markers (one per visible/discovered DSO).
 * @param {CanvasRenderingContext2D} ctx
 * @param {Array}  dsos   - from viewState.deepSpaceObjects
 * @param {number} size   - hex radius in pixels
 * @param {number} zoom
 */
function _drawDsoMarkers(ctx, dsos, size, zoom) {
  for (const dso of dsos) {
    if (dso.depleted) continue;   // depleted objects fade from the map
    const render = DSO_RENDER[dso.type] || DSO_RENDER.anomaly;
    const { x: dx, y: dy } = axialToPixel(dso.hex_q, dso.hex_r, size);

    // Subtle hex background
    drawHex(ctx, dx, dy, size - 2, render.bg, render.color, 0.6);

    // Glyph
    ctx.fillStyle = render.color;
    ctx.font = `${Math.max(8, size * 0.55)}px "Courier New", monospace`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(render.glyph, dx, dy);

    // Name label (only when zoomed in and discovered)
    if (zoom >= 0.8 && dso.name) {
      ctx.fillStyle = render.color;
      ctx.globalAlpha = 0.75;
      ctx.font = `${Math.max(6, Math.floor(7 * zoom))}px "Courier New", monospace`;
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillText(dso.name.length > 18 ? dso.name.slice(0, 16) + "…" : dso.name,
                   dx, dy + size * 0.55);
      ctx.globalAlpha = 1.0;
    }
  }
}


export function renderGalaxyMap(canvas, systems, viewState, factionColors) {
  const ctx = canvas.getContext("2d");
  const { panX, panY, zoom, selectedSystemName, stations = [], selectedStationName,
          deepSpaceObjects = [], zStats = null, activeZFilter = "all" } = viewState;

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

  // -----------------------------------------------------------------------
  // Pass 0: Full hex grid background — every cell in the galaxy bounding
  // box rendered as a dim, empty tile.  This makes the grid the primary
  // visual whether or not a cell has content.
  // The galaxy spans 500×500 units at GALAXY_SCALE=12.5, giving ≈40×40 hexes.
  // We use a fixed margin of 3 hexes beyond the galaxy edge.
  // -----------------------------------------------------------------------
  {
    // Q spans the column axis; V spans visual rows (vrow = r + q/2).
    // Iterating over (q, vrow) and computing r = round(vrow - q/2) ensures
    // the covered pixel area is rectangular rather than a parallelogram.
    const Q_MIN = -3, Q_MAX = 46;
    const V_MIN = -3, V_MAX = 46;

    // Viewport bounds in world space (for culling off-screen hexes)
    const halfW = canvas.width  / 2;
    const halfH = canvas.height / 2;
    const vLeft   = (-halfW - panX) / zoom - size * 2;
    const vRight  = ( halfW - panX) / zoom + size * 2;
    const vTop    = (-halfH - panY) / zoom - size * 2;
    const vBottom = ( halfH - panY) / zoom + size * 2;

    for (let q = Q_MIN; q <= Q_MAX; q++) {
      for (let vrow = V_MIN; vrow <= V_MAX; vrow++) {
        const r = Math.round(vrow - q / 2);
        const { x: gx, y: gy } = axialToPixel(q, r, size);
        if (gx < vLeft || gx > vRight || gy < vTop || gy > vBottom) continue;
        drawHex(ctx, gx, gy, size - 0.5, "#0c1520", "#1a2840", 0.5);
      }
    }
  }

  // Territory fills drawn first so hex tiles render on top of the wash
  _drawTerritoryFills(ctx, systems, size);

  for (const sys of systems) {
    const { x: px, y: py } = axialToPixel(sys.hex_q, sys.hex_r, size);

    // ── Z-elevation: compute band and filter dimming ──────────────────────
    // Every system carries a z coordinate from the backend; classify it into
    // one of five elevation bands relative to the dataset mean/std.
    const band   = zStats ? _zBand(sys.z ?? 0, zStats) : "plane";
    const dimmed = activeZFilter !== "all" && band !== activeZFilter;
    // Dimmed systems render at ~10% alpha so the galaxy silhouette stays visible
    ctx.globalAlpha = dimmed ? 0.10 : 1.0;

    // Faction colour tint
    const factionColor = sys.controlling_faction
      ? (factionColors.get(sys.controlling_faction) || "rgba(0,212,170,0.08)")
      : null;

    // Background fill
    const bgColor = SYSTEM_TYPE_COLORS[sys.type] || SYSTEM_TYPE_COLORS.default;

    // Scan visibility:
    //   in_scan_range: true  — currently within sensor range, full render
    //   in_scan_range: false — previously discovered but out of range, ghost render
    //   (systems never scanned are not returned by the API at all)
    const inScanRange = sys.in_scan_range !== false;  // default true for backward compat

    if (!inScanRange) {
      // Ghost render: dim hex outline + name only, no faction/glyph/details
      ctx.globalAlpha = dimmed ? 0.04 : 0.22;
      drawHex(ctx, px, py, size - 1, "#0a0e1a", "#1a2840", 0.5);
      if (zoom >= 0.7) {
        ctx.fillStyle = "rgba(120,150,180,0.5)";
        ctx.font = `${Math.max(7, Math.floor(8 * zoom))}px "Courier New", monospace`;
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        ctx.fillText(sys.name, px, py + size * 0.55);
      }
      ctx.globalAlpha = 1.0;
      continue;
    }

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
    if (factionColor) {
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

    // Elevation ring — extra outer ring for extreme bands (high / deep)
    if (zStats && !dimmed) {
      const zStyle = Z_BAND_STYLES[band];
      if (zStyle.ring) {
        ctx.beginPath();
        for (let i = 0; i < 6; i++) {
          const angle = (Math.PI / 180) * (60 * i);
          const hx = px + (size + 5) * Math.cos(angle);
          const hy = py + (size + 5) * Math.sin(angle);
          i === 0 ? ctx.moveTo(hx, hy) : ctx.lineTo(hx, hy);
        }
        ctx.closePath();
        ctx.strokeStyle = zStyle.ring;
        ctx.lineWidth   = 1.2;
        ctx.stroke();
      }
    }

    // Star glyph — hidden when the player's ship is at this hex (ship marker replaces it)
    const shipIsHere = viewState.shipHex &&
                       sys.hex_q === viewState.shipHex.q &&
                       sys.hex_r === viewState.shipHex.r;
    if (!shipIsHere) {
      const glyph = SYSTEM_GLYPHS[sys.type] || SYSTEM_GLYPHS.default;
      ctx.fillStyle = _systemGlyphColor(sys);
      ctx.font = `${Math.max(10, size * 0.7)}px "Courier New", monospace`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(glyph, px, py);
    }

    // Elevation dot — small coloured circle below the star glyph.
    // Absent for "plane" systems to avoid clutter; always drawn unless dimmed.
    if (zStats && !dimmed) {
      const zStyle = Z_BAND_STYLES[band];
      if (zStyle.dot) {
        ctx.beginPath();
        ctx.arc(px, py + size * 0.68, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = zStyle.dot;
        ctx.fill();
      }
    }

    // System name label (always shown; ship presence highlighted in teal)
    if (zoom >= 0.7) {
      ctx.fillStyle = shipIsHere ? "#00ffcc"
                    : sys.name === selectedSystemName ? "#00d4aa"
                    : "rgba(200, 216, 232, 0.7)";
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

    // Reset alpha after each system so subsequent draws are unaffected
    ctx.globalAlpha = 1.0;
  }

  // Territory borders — drawn after all hex tiles so lines sit in the gaps
  _drawTerritoryBorders(ctx, systems, size);

  // -----------------------------------------------------------------------
  // Deep space object markers — drawn after territory, before stations
  // -----------------------------------------------------------------------
  if (deepSpaceObjects.length > 0) {
    _drawDsoMarkers(ctx, deepSpaceObjects, size, zoom);
  }

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
  // NPC ship markers — drawn after station markers, before the player ship
  // so the player's marker always renders on top.
  //
  // Each NPC ship is a small amber/orange ▲ glyph with a name label.
  // If multiple bots share the same hex, they are grouped and shown as
  // "▲×N" with only the first bot's name to avoid label clutter.
  // -----------------------------------------------------------------------
  const npcShips = viewState.npcShips || [];
  if (npcShips.length > 0) {
    // Group bots by "q,r" key
    const grouped = new Map();
    for (const ship of npcShips) {
      const key = `${ship.hex_q},${ship.hex_r}`;
      if (!grouped.has(key)) grouped.set(key, []);
      grouped.get(key).push(ship);
    }

    for (const [, group] of grouped) {
      const { hex_q: nq, hex_r: nr } = group[0];
      const { x: npx, y: npy } = axialToPixel(nq, nr, size);
      const count = group.length;

      // Small amber filled circle backdrop (half the size of player ship)
      ctx.beginPath();
      ctx.arc(npx, npy, size * 0.22, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(210, 130, 0, 0.80)";
      ctx.fill();
      ctx.strokeStyle = "#ff9900";
      ctx.lineWidth = 0.8;
      ctx.stroke();

      // Triangle glyph — same ▲ as player ship but dark for contrast
      ctx.fillStyle = "#1a0800";
      ctx.font = `bold ${Math.round(size * 0.30)}px "Courier New", monospace`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("▲", npx, npy);

      // Name / count label beneath the marker (only when zoomed in)
      if (zoom >= 0.7) {
        const label = count > 1
          ? `${group[0].name} +${count - 1}`
          : group[0].name;
        ctx.fillStyle = "rgba(255, 153, 0, 0.85)";
        ctx.font = `${Math.max(6, Math.floor(7 * zoom))}px "Courier New", monospace`;
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        ctx.fillText(label, npx, npy + size * 0.32);
      }
    }
  }

  // -----------------------------------------------------------------------
  // Player ship marker — drawn on top of all system hexes
  // -----------------------------------------------------------------------
  // viewState.shipHex = { q, r } from galaxy.js (computed from ship.coordinates)
  if (viewState.shipHex) {
    const { q: sq, r: sr } = viewState.shipHex;
    const { x: spx, y: spy } = axialToPixel(sq, sr, size);

    // Sensor range ring — solid teal-blue circle showing current scan radius.
    // Only drawn when viewState.showScanRing is true (player-toggled).
    if (viewState.showScanRing && viewState.scanRangePx && viewState.scanRangePx > 0) {
      ctx.save();
      // Subtle filled area so the scanned zone reads as a region, not just a line
      ctx.beginPath();
      ctx.arc(spx, spy, viewState.scanRangePx, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(80, 180, 255, 0.04)";
      ctx.fill();
      // Dot-dash border — visually distinct from the jump range ring
      ctx.beginPath();
      ctx.arc(spx, spy, viewState.scanRangePx, 0, Math.PI * 2);
      ctx.strokeStyle = "rgba(80, 180, 255, 0.55)";
      ctx.lineWidth = 1.0;
      ctx.setLineDash([2, 5]);
      ctx.stroke();
      ctx.setLineDash([]);
      // Label: "SENSORS  40 u" rendered at the top of the ring
      const labelY = spy - viewState.scanRangePx - 6;
      ctx.fillStyle = "rgba(80, 180, 255, 0.70)";
      ctx.font = `${Math.max(8, Math.floor(9 * viewState.zoom ?? 1))}px "Courier New", monospace`;
      ctx.textAlign = "center";
      ctx.textBaseline = "bottom";
      ctx.fillText(`SENSORS  ${viewState.scanRangeUnits ?? ""} u`, spx, labelY);
      ctx.restore();
    }

    // Jump range ring — faint dashed circle showing maximum jump distance
    if (viewState.jumpRangePx && viewState.jumpRangePx > 0) {
      ctx.save();
      ctx.beginPath();
      ctx.arc(spx, spy, viewState.jumpRangePx, 0, Math.PI * 2);
      ctx.strokeStyle = "rgba(0, 212, 170, 0.25)";
      ctx.lineWidth = 0.8;
      ctx.setLineDash([4, 6]);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.restore();
    }

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


// ---------------------------------------------------------------------------
// System interior hex map rendering
// ---------------------------------------------------------------------------

/**
 * Fill colour for each planet subtype.
 * Intentionally dark so the glyphs remain readable on a deep-space background.
 */
const PLANET_SUBTYPE_COLORS = {
  "Rocky":        "#1a0e0a",
  "Ocean":        "#081828",
  "Gas Giant":    "#1e1028",
  "Ice":          "#101e28",
  "Desert":       "#281808",
  "Volcanic":     "#280800",
  "Lava":         "#200400",
  "Terrestrial":  "#0a1e0a",
  "Super-Earth":  "#0c1e10",
  "Sub-Earth":    "#141010",
};

/**
 * Render the interior hex map of a star system.
 *
 * Draws a background hex grid (deep space), subtle orbital-ring circles,
 * then each object (star, planets, stations, NPC ships) using distinctive
 * colours and Unicode glyphs.  Respects pan + zoom via the same transform
 * used by renderGalaxyMap and renderColonyMap.
 *
 * @param {HTMLCanvasElement} canvas
 * @param {Array}  objects     - from /api/system/{name}/interior
 * @param {number} gridRadius  - from /api/system/{name}/interior
 * @param {object} viewState   - { panX, panY, zoom, selectedQ, selectedR, playerHere }
 */
export function renderSystemMap(canvas, objects, gridRadius, viewState) {
  const ctx = canvas.getContext("2d");
  const { panX = 0, panY = 0, zoom = 1, selectedQ = null, selectedR = null, playerHere = false } = viewState;
  const size = SYSTEM_HEX_SIZE;

  // 1. Clear with deep-space background (slightly different from galaxy)
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#030508";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // 2. Apply pan + zoom transform, centred on canvas
  ctx.save();
  ctx.translate(panX + canvas.width / 2, panY + canvas.height / 2);
  ctx.scale(zoom, zoom);

  // 3. Draw background hex grid out to gridRadius
  for (let q = -gridRadius; q <= gridRadius; q++) {
    const r1 = Math.max(-gridRadius, -q - gridRadius);
    const r2 = Math.min(gridRadius,  -q + gridRadius);
    for (let r = r1; r <= r2; r++) {
      const { x: px, y: py } = axialToPixel(q, r, size);
      // Viewport cull: skip hexes far outside the visible canvas area
      const screenX = panX + canvas.width  / 2 + px * zoom;
      const screenY = panY + canvas.height / 2 + py * zoom;
      if (screenX < -size * 4 || screenX > canvas.width  + size * 4) continue;
      if (screenY < -size * 4 || screenY > canvas.height + size * 4) continue;
      drawHex(ctx, px, py, size - 0.5, "#0a0d18", "#141e30", 0.35);
    }
  }

  // 4. Orbital ring hints — faint dashed arcs at each planet ring
  //    We use the pixel distance to the east vertex of ring i as the arc radius.
  ctx.save();
  ctx.strokeStyle = "rgba(40,80,120,0.22)";
  ctx.lineWidth   = 0.8;
  ctx.setLineDash([2, 6]);
  const maxPlanetRing = gridRadius - 2;
  for (let ring = 2; ring <= maxPlanetRing; ring++) {
    // Pixel radius = horizontal distance from (0,0) to the east vertex of the ring
    const { x: rPx } = axialToPixel(ring, 0, size);
    ctx.beginPath();
    ctx.arc(0, 0, rPx, 0, Math.PI * 2);
    ctx.stroke();
  }
  ctx.setLineDash([]);
  ctx.restore();

  // 5. Draw object hexes — star, planets, stations, NPC ships
  for (const obj of objects) {
    const { x: px, y: py } = axialToPixel(obj.q, obj.r, size);

    // Selection glow ring
    const isSelected = (obj.q === selectedQ && obj.r === selectedR);

    if (obj.kind === "star") {
      // Bright yellow/white star with a soft glow ring
      const grad = ctx.createRadialGradient(px, py, 0, px, py, size * 0.8);
      grad.addColorStop(0,   "rgba(255,240,120,0.25)");
      grad.addColorStop(1,   "rgba(255,200,60,0)");
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(px, py, size * 0.8, 0, Math.PI * 2);
      ctx.fill();
      drawHex(ctx, px, py, size - 1,
        isSelected ? "#3a2a00" : "#2a1e00",
        isSelected ? "#00d4aa" : "#f0c040",
        isSelected ? 2 : 1.2);
      // Star glyph
      ctx.fillStyle  = "#f0d060";
      ctx.font       = `bold ${Math.round(size * 0.8)}px "Courier New", monospace`;
      ctx.textAlign  = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("★", px, py);

    } else if (obj.kind === "planet") {
      const fill = PLANET_SUBTYPE_COLORS[obj.subtype] || "#10101a";
      const border = obj.has_colony
        ? (isSelected ? "#00d4aa" : "#008866")
        : (isSelected ? "#00d4aa" : "#2a3a4a");
      drawHex(ctx, px, py, size - 1, fill, border, isSelected ? 2 : 0.8);

      // Planet glyph
      ctx.fillStyle  = obj.habitable ? "#66ccaa" : "#607080";
      ctx.font       = `${Math.round(size * 0.65)}px "Courier New", monospace`;
      ctx.textAlign  = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("◉", px, py);

      // Colony badge — small house icon at top-right corner
      if (obj.has_colony) {
        ctx.fillStyle    = "#00d4aa";
        ctx.font         = `${Math.round(size * 0.35)}px "Courier New", monospace`;
        ctx.textBaseline = "top";
        ctx.fillText("⌂", px + size * 0.38, py - size * 0.65);
        ctx.textBaseline = "middle";
      }

      // Label below hex (only when zoomed in enough)
      if (zoom >= 0.6) {
        ctx.fillStyle    = "#8ab0c0";
        ctx.font         = `${Math.round(size * 0.28)}px "Courier New", monospace`;
        ctx.textBaseline = "top";
        ctx.fillText(obj.label, px, py + size * 0.75);
        ctx.textBaseline = "middle";
      }

    } else if (obj.kind === "station") {
      // Amber station hex
      drawHex(ctx, px, py, size - 1,
        isSelected ? "#1e1200" : "#120c00",
        isSelected ? "#00d4aa" : "#c08820",
        isSelected ? 2 : 1);
      ctx.fillStyle  = "#d0a040";
      ctx.font       = `${Math.round(size * 0.65)}px "Courier New", monospace`;
      ctx.textAlign  = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("⊕", px, py);
      if (zoom >= 0.6) {
        ctx.fillStyle    = "#8a7040";
        ctx.font         = `${Math.round(size * 0.28)}px "Courier New", monospace`;
        ctx.textBaseline = "top";
        ctx.fillText(obj.label, px, py + size * 0.75);
        ctx.textBaseline = "middle";
      }

    } else if (obj.kind === "npc_ship") {
      // Small amber circle with a ▲ glyph — same pattern as galaxy map
      drawHex(ctx, px, py, size * 0.6,
        isSelected ? "#1e1000" : "#0e0800",
        isSelected ? "#00d4aa" : "#a07020",
        isSelected ? 2 : 0.8);
      ctx.fillStyle  = "#c09030";
      ctx.font       = `${Math.round(size * 0.45)}px "Courier New", monospace`;
      ctx.textAlign  = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("▲", px, py);
    }
  }

  // 6. Player ship marker at (0,0) when player is in this system
  if (playerHere) {
    const { x: px, y: py } = axialToPixel(0, 0, size);
    // Teal triangle offset slightly so it doesn't overlap the star glyph
    ctx.fillStyle    = "#00d4aa";
    ctx.font         = `${Math.round(size * 0.38)}px "Courier New", monospace`;
    ctx.textAlign    = "center";
    ctx.textBaseline = "bottom";
    ctx.fillText("▲", px + size * 0.5, py - size * 0.3);
    ctx.textBaseline = "middle";
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
