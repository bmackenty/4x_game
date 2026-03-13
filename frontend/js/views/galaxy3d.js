/**
 * views/galaxy3d.js — 3D galaxy visualisation view.
 *
 * Read-only view: rotate and zoom the galaxy cloud in three dimensions.
 * Uses no external libraries — pure Canvas 2D with a hand-rolled 3-D
 * rotation matrix + perspective projection.
 *
 * Controls:
 *   Mouse drag     → orbit (azimuth + elevation)
 *   Scroll / pinch → zoom
 *   Hover          → system name tooltip
 *
 * Territory borders:
 *   Thin lines connect star systems that share the same controlling_faction
 *   and are within BORDER_DIST_THRESHOLD normalised units of one another.
 */

import { getGalaxyMap } from "../api.js";
import { notify }       from "../ui/notifications.js";

// ---------------------------------------------------------------------------
// Public view object
// ---------------------------------------------------------------------------

export const galaxy3dView = { mount, unmount };


// ---------------------------------------------------------------------------
// Module-level state (reset on every mount)
// ---------------------------------------------------------------------------

/** Raw + normalised system data loaded from the API */
let _systems   = [];
/** Orbit angles (radians) */
let _azimuth   = 0.4;
let _elevation = 0.25;
/** Camera distance (perspective) — 1 = default, larger = zoomed out */
let _camDist   = 3.5;
/** Drag tracking */
let _dragging      = false;
let _lastMouse     = { x: 0, y: 0 };
/** Hover tooltip */
let _hoveredSystem = null;
/** requestAnimationFrame handle */
let _rafId     = null;
/** Canvas + context */
let _canvas    = null;
let _ctx       = null;
/** Whether data has been loaded */
let _loaded    = false;


/** Perspective projection — eye distance multiplier; larger = less distortion */
const PERSPECTIVE_DEPTH = 2.0;


// ---------------------------------------------------------------------------
// System type → colour mapping  (mirrors the 2D map's colour scheme)
// ---------------------------------------------------------------------------

const TYPE_COLORS = {
  "Star":         "#ffe082",
  "Binary Star":  "#ffb74d",
  "Neutron Star": "#ce93d8",
  "Black Hole":   "#9e9e9e",
  "Nebula":       "#80cbc4",
  "Void":         "#546e7a",
  "Unknown":      "#607d8b",
};

/** Fallback when type is not in the map */
const DEFAULT_COLOR = "#90a4ae";

/** Faction hue palette — generated per unique faction name for borders */
const _factionColorCache = {};
let   _factionHueIndex   = 0;
const FACTION_HUES = [180, 30, 270, 90, 330, 210, 150, 60, 300, 0];

function _factionColor(faction) {
  if (!_factionColorCache[faction]) {
    const hue = FACTION_HUES[_factionHueIndex % FACTION_HUES.length];
    _factionHueIndex++;
    _factionColorCache[faction] = `hsl(${hue},70%,55%)`;
  }
  return _factionColorCache[faction];
}


// ---------------------------------------------------------------------------
// mount / unmount
// ---------------------------------------------------------------------------

async function mount() {
  // Reset module state for a clean mount
  _systems       = [];
  _loaded        = false;
  _hoveredSystem = null;
  _factionHueIndex = 0;
  Object.keys(_factionColorCache).forEach(k => delete _factionColorCache[k]);

  const container = document.getElementById("view-galaxy3d");
  if (!container) return;

  // Build (or reuse) the canvas and toolbar
  container.innerHTML = _buildShell();

  _canvas = document.getElementById("galaxy3d-canvas");
  _ctx    = _canvas.getContext("2d");

  // Keep canvas pixel-perfect when the window is resized
  _resizeCanvas();
  window.addEventListener("resize", _resizeCanvas);

  // Wire interaction events
  _canvas.addEventListener("mousedown",  _onMouseDown);
  _canvas.addEventListener("mousemove",  _onMouseMove);
  _canvas.addEventListener("mouseup",    _onMouseUp);
  _canvas.addEventListener("mouseleave", _onMouseUp);
  _canvas.addEventListener("wheel",      _onWheel, { passive: false });

  // Touch support for mobile / trackpads
  _canvas.addEventListener("touchstart",  _onTouchStart,  { passive: false });
  _canvas.addEventListener("touchmove",   _onTouchMove,   { passive: false });
  _canvas.addEventListener("touchend",    _onTouchEnd);

  // Wire reset button
  const resetBtn = document.getElementById("g3d-reset-btn");
  if (resetBtn) resetBtn.addEventListener("click", _resetCamera);

  // Start render loop immediately (shows loading message)
  _startRenderLoop();

  // Fetch galaxy data
  try {
    const data = await getGalaxyMap();
    _processData(data.systems || []);
    _loaded = true;
  } catch (err) {
    notify("ERROR", `3D view: ${err.message}`);
  }
}

function unmount() {
  _stopRenderLoop();

  window.removeEventListener("resize", _resizeCanvas);

  if (_canvas) {
    _canvas.removeEventListener("mousedown",  _onMouseDown);
    _canvas.removeEventListener("mousemove",  _onMouseMove);
    _canvas.removeEventListener("mouseup",    _onMouseUp);
    _canvas.removeEventListener("mouseleave", _onMouseUp);
    _canvas.removeEventListener("wheel",      _onWheel);
    _canvas.removeEventListener("touchstart",  _onTouchStart);
    _canvas.removeEventListener("touchmove",   _onTouchMove);
    _canvas.removeEventListener("touchend",    _onTouchEnd);
  }

  _canvas = null;
  _ctx    = null;
}


// ---------------------------------------------------------------------------
// Shell HTML
// ---------------------------------------------------------------------------

function _buildShell() {
  return `
    <div class="g3d-toolbar">
      <span class="g3d-toolbar__title">3D GALAXY VIEW</span>
      <span class="g3d-toolbar__hint">Drag to orbit · Scroll to zoom</span>
      <div class="g3d-toolbar__right">
        <button class="btn btn--secondary g3d-btn" id="g3d-reset-btn" title="Reset camera">RESET</button>
      </div>
    </div>
    <canvas id="galaxy3d-canvas" class="g3d-canvas"></canvas>
    <div class="g3d-legend" id="g3d-legend"></div>
  `;
}


// ---------------------------------------------------------------------------
// Data processing — normalise raw (x,y,z) coords into a unit sphere
// ---------------------------------------------------------------------------

function _processData(rawSystems) {
  if (!rawSystems.length) return;

  // Compute centroid
  let cx = 0, cy = 0, cz = 0;
  rawSystems.forEach(s => { cx += s.x; cy += s.y; cz += s.z; });
  cx /= rawSystems.length;
  cy /= rawSystems.length;
  cz /= rawSystems.length;

  // Compute max distance from centroid (for normalisation)
  let maxDist = 1;
  rawSystems.forEach(s => {
    const dx = s.x - cx, dy = s.y - cy, dz = s.z - cz;
    const d  = Math.sqrt(dx * dx + dy * dy + dz * dz);
    if (d > maxDist) maxDist = d;
  });

  _systems = rawSystems.map(s => ({
    name:               s.name,
    // Normalised position in [-1, 1]
    nx: (s.x - cx) / maxDist,
    ny: (s.y - cy) / maxDist,
    nz: (s.z - cz) / maxDist,
    // Raw coords for display
    x: s.x, y: s.y, z: s.z,
    type:               s.type || "Unknown",
    visited:            s.visited || false,
    controlling_faction: s.controlling_faction || null,
    population:         s.population || 0,
  }));

  // Populate legend
  _buildLegend();
}


// ---------------------------------------------------------------------------
// Legend
// ---------------------------------------------------------------------------

function _buildLegend() {
  const el = document.getElementById("g3d-legend");
  if (!el) return;

  // Unique factions that have at least one system
  const factions = [...new Set(
    _systems.map(s => s.controlling_faction).filter(Boolean)
  )];

  const factionItems = factions.map(f => {
    const col = _factionColor(f);
    return `<span class="g3d-legend__item">
      <span class="g3d-legend__dot" style="background:${col}"></span>${f}
    </span>`;
  }).join("");

  el.innerHTML = `
    <span class="g3d-legend__item">
      <span class="g3d-legend__dot" style="background:#ffe082"></span>Visited
    </span>
    <span class="g3d-legend__item">
      <span class="g3d-legend__dot" style="background:#607d8b"></span>Unvisited
    </span>
    ${factionItems ? `<span class="g3d-legend__sep">|</span>${factionItems}` : ""}
  `;
}


// ---------------------------------------------------------------------------
// Render loop
// ---------------------------------------------------------------------------

function _startRenderLoop() {
  if (_rafId) return;
  const loop = () => {
    // Re-sync canvas buffer size every frame — catches any layout changes
    // including the initial mount where offsetWidth/Height may be 0 on the
    // first synchronous call (before the browser has painted).
    _resizeCanvas();
    _render();
    _rafId = requestAnimationFrame(loop);
  };
  _rafId = requestAnimationFrame(loop);
}

function _stopRenderLoop() {
  if (_rafId) {
    cancelAnimationFrame(_rafId);
    _rafId = null;
  }
}


// ---------------------------------------------------------------------------
// 3D Math helpers
// ---------------------------------------------------------------------------

/**
 * Rotate a point (x, y, z) by azimuth (around world Y) then elevation
 * (around the resulting X axis), returning a new {x, y, z}.
 */
function _rotate(nx, ny, nz, azimuth, elevation) {
  // Rotation around Y (azimuth)
  const cosA = Math.cos(azimuth), sinA = Math.sin(azimuth);
  const x1 =  nx * cosA + nz * sinA;
  const y1 =  ny;
  const z1 = -nx * sinA + nz * cosA;

  // Rotation around X (elevation)
  const cosE = Math.cos(elevation), sinE = Math.sin(elevation);
  const x2 = x1;
  const y2 = y1 * cosE - z1 * sinE;
  const z2 = y1 * sinE + z1 * cosE;

  return { x: x2, y: y2, z: z2 };
}

/**
 * Project a rotated 3D point onto the canvas.
 * Returns { sx, sy, depth } where depth is used for z-sorting.
 */
function _project(rx, ry, rz, cw, ch) {
  const eyeZ   = _camDist;
  const depth  = eyeZ + rz;            // Camera sits at z = eyeZ looking toward -z
  const fov    = PERSPECTIVE_DEPTH;
  const factor = fov / Math.max(depth, 0.01);

  const half   = Math.min(cw, ch) * 0.45;  // View scale in pixels
  const sx = cw / 2 + rx * half * factor;
  const sy = ch / 2 - ry * half * factor;  // Y is inverted on canvas

  return { sx, sy, depth };
}


// ---------------------------------------------------------------------------
// Main render function
// ---------------------------------------------------------------------------

function _render() {
  if (!_ctx || !_canvas) return;

  const cw = _canvas.width;
  const ch = _canvas.height;

  // Background
  _ctx.fillStyle = "#05080f";
  _ctx.fillRect(0, 0, cw, ch);

  if (!_loaded) {
    _ctx.fillStyle = "#607d8b";
    _ctx.font      = "14px monospace";
    _ctx.textAlign = "center";
    _ctx.fillText("Loading galaxy data…", cw / 2, ch / 2);
    return;
  }

  if (!_systems.length) {
    _ctx.fillStyle = "#607d8b";
    _ctx.font      = "14px monospace";
    _ctx.textAlign = "center";
    _ctx.fillText("No system data available.", cw / 2, ch / 2);
    return;
  }

  // --- Step 1: rotate + project all systems ---------------------------------
  const projected = _systems.map(s => {
    const r = _rotate(s.nx, s.ny, s.nz, _azimuth, _elevation);
    const p = _project(r.x, r.y, r.z, cw, ch);
    return { ...s, ...p, rx: r.x, ry: r.y, rz: r.z };
  });

  // Z-sort back-to-front so closer systems render on top
  projected.sort((a, b) => b.depth - a.depth);

  // --- Step 2: galactic plane reference grid --------------------------------
  _drawPlaneGrid(cw, ch);

  // --- Step 4: star systems -------------------------------------------------
  let newHovered = null;
  const mouseX = _lastMouse.x, mouseY = _lastMouse.y;

  projected.forEach(s => {
    // Base dot radius — slightly bigger for visited/populated systems
    const base   = s.visited ? 4.5 : 2.5;
    const radius = base * (1 + (s.population > 0 ? 0.6 : 0));

    // Perspective scale: closer = slightly larger
    const perspScale = Math.max(0.5, 1.5 / Math.max(s.depth, 0.3));
    const r          = radius * perspScale;

    // Colour
    let color = TYPE_COLORS[s.type] || DEFAULT_COLOR;
    if (!s.visited) color = "#37474f";                  // Unvisited: dim grey
    if (s.controlling_faction) {
      // Tint toward faction colour
      color = _factionColor(s.controlling_faction);
    }

    // Glow for visited + factioned systems
    if (s.visited && s.controlling_faction) {
      _ctx.save();
      const grd = _ctx.createRadialGradient(s.sx, s.sy, 0, s.sx, s.sy, r * 3);
      grd.addColorStop(0, color.replace("55%)", "55%,0.4)").replace("hsl(", "hsla("));
      grd.addColorStop(1, "transparent");
      _ctx.fillStyle = grd;
      _ctx.beginPath();
      _ctx.arc(s.sx, s.sy, r * 3, 0, Math.PI * 2);
      _ctx.fill();
      _ctx.restore();
    }

    // Main dot
    _ctx.beginPath();
    _ctx.arc(s.sx, s.sy, r, 0, Math.PI * 2);
    _ctx.fillStyle = color;
    _ctx.fill();

    // Hover detection
    const dx = s.sx - mouseX, dy = s.sy - mouseY;
    if (Math.sqrt(dx * dx + dy * dy) < Math.max(r + 6, 10)) {
      newHovered = s;
    }
  });

  _hoveredSystem = newHovered;

  // --- Step 5: hover tooltip ------------------------------------------------
  if (_hoveredSystem) {
    _drawTooltip(_hoveredSystem, cw, ch);
  }

  // --- Step 6: HUD overlay --------------------------------------------------
  _drawHudOverlay(cw, ch);
}


// ---------------------------------------------------------------------------
// Galactic plane reference grid
// ---------------------------------------------------------------------------

function _drawPlaneGrid(cw, ch) {
  const GRID_LINES = 8;
  const GRID_STEP  = 2 / GRID_LINES; // in normalised space [-1, 1]

  _ctx.save();
  _ctx.strokeStyle = "rgba(0,212,170,0.06)";
  _ctx.lineWidth   = 0.5;

  for (let i = 0; i <= GRID_LINES; i++) {
    const u = -1 + i * GRID_STEP;

    // Lines along X axis
    _ctx.beginPath();
    const a1 = _rotate(u, 0, -1, _azimuth, _elevation);
    const p1 = _project(a1.x, a1.y, a1.z, cw, ch);
    const a2 = _rotate(u, 0,  1, _azimuth, _elevation);
    const p2 = _project(a2.x, a2.y, a2.z, cw, ch);
    _ctx.moveTo(p1.sx, p1.sy);
    _ctx.lineTo(p2.sx, p2.sy);
    _ctx.stroke();

    // Lines along Z axis
    _ctx.beginPath();
    const b1 = _rotate(-1, 0, u, _azimuth, _elevation);
    const q1 = _project(b1.x, b1.y, b1.z, cw, ch);
    const b2 = _rotate( 1, 0, u, _azimuth, _elevation);
    const q2 = _project(b2.x, b2.y, b2.z, cw, ch);
    _ctx.moveTo(q1.sx, q1.sy);
    _ctx.lineTo(q2.sx, q2.sy);
    _ctx.stroke();
  }

  _ctx.restore();
}


// ---------------------------------------------------------------------------
// Tooltip
// ---------------------------------------------------------------------------

function _drawTooltip(s, cw, ch) {
  const lines = [
    s.name,
    s.type,
    s.controlling_faction ? `⬡ ${s.controlling_faction}` : "",
    s.visited ? `(${Math.round(s.x)}, ${Math.round(s.y)}, ${Math.round(s.z)})` : "Unvisited",
  ].filter(Boolean);

  const PADDING    = 8;
  const LINE_H     = 16;
  const boxW       = 200;
  const boxH       = lines.length * LINE_H + PADDING * 2;

  // Position near cursor, keep inside canvas
  let tx = s.sx + 14;
  let ty = s.sy - boxH / 2;
  if (tx + boxW > cw - 4) tx = s.sx - boxW - 14;
  if (ty < 4)             ty = 4;
  if (ty + boxH > ch - 4) ty = ch - boxH - 4;

  _ctx.save();

  // Box background
  _ctx.fillStyle   = "rgba(5,8,15,0.92)";
  _ctx.strokeStyle = "rgba(0,212,170,0.5)";
  _ctx.lineWidth   = 1;
  _ctx.beginPath();
  _ctx.roundRect(tx, ty, boxW, boxH, 4);
  _ctx.fill();
  _ctx.stroke();

  // Text
  _ctx.font         = "11px monospace";
  _ctx.textAlign    = "left";
  _ctx.textBaseline = "top";
  lines.forEach((line, i) => {
    _ctx.fillStyle = i === 0 ? "#e0e0e0" : "#90a4ae";
    _ctx.fillText(line, tx + PADDING, ty + PADDING + i * LINE_H);
  });

  _ctx.restore();
}


// ---------------------------------------------------------------------------
// HUD overlay (camera info)
// ---------------------------------------------------------------------------

function _drawHudOverlay(cw, ch) {
  const az  = ((_azimuth   * 180 / Math.PI) % 360).toFixed(0);
  const el  = ((_elevation * 180 / Math.PI) % 360).toFixed(0);
  const zm  = (1 / _camDist * 3.5).toFixed(2);
  const txt = `Az ${az}°  El ${el}°  Zoom ×${zm}  Systems ${_systems.length}`;

  _ctx.save();
  _ctx.font         = "10px monospace";
  _ctx.textAlign    = "right";
  _ctx.textBaseline = "bottom";
  _ctx.fillStyle    = "rgba(96,125,139,0.8)";
  _ctx.fillText(txt, cw - 8, ch - 6);
  _ctx.restore();
}


// ---------------------------------------------------------------------------
// Canvas resize
// ---------------------------------------------------------------------------

function _resizeCanvas() {
  if (!_canvas) return;

  // Read the actual CSS-rendered size of the canvas element.
  // The canvas has flex:1 so it fills whatever the view leaves after
  // the toolbar and legend — offsetWidth/Height reflect that layout.
  const w = _canvas.offsetWidth;
  const h = _canvas.offsetHeight;

  if (w > 0 && h > 0) {
    _canvas.width  = w;
    _canvas.height = h;
  }
}


// ---------------------------------------------------------------------------
// Camera reset
// ---------------------------------------------------------------------------

function _resetCamera() {
  _azimuth   = 0.4;
  _elevation = 0.25;
  _camDist   = 3.5;
}


// ---------------------------------------------------------------------------
// Mouse event handlers
// ---------------------------------------------------------------------------

function _onMouseDown(e) {
  _dragging  = true;
  _lastMouse = { x: e.offsetX, y: e.offsetY };
  _canvas.style.cursor = "grabbing";
}

function _onMouseMove(e) {
  if (_dragging) {
    const dx = e.offsetX - _lastMouse.x;
    const dy = e.offsetY - _lastMouse.y;
    // Sensitivity: 0.005 radians per pixel
    _azimuth   += dx * 0.005;
    _elevation += dy * 0.005;
    // Clamp elevation so the view doesn't flip
    _elevation = Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, _elevation));
  }
  _lastMouse = { x: e.offsetX, y: e.offsetY };
}

function _onMouseUp() {
  _dragging            = false;
  _canvas.style.cursor = "grab";
}

function _onWheel(e) {
  e.preventDefault();
  const delta  = e.deltaY > 0 ? 1.08 : 0.93;
  _camDist    *= delta;
  _camDist     = Math.max(1.2, Math.min(12, _camDist));
}


// ---------------------------------------------------------------------------
// Touch event handlers (two-finger pinch = zoom, one-finger drag = orbit)
// ---------------------------------------------------------------------------

let _lastTouchDist = null;

function _onTouchStart(e) {
  e.preventDefault();
  if (e.touches.length === 1) {
    _dragging  = true;
    _lastMouse = { x: e.touches[0].clientX, y: e.touches[0].clientY };
  } else if (e.touches.length === 2) {
    _lastTouchDist = _touchDist(e.touches);
  }
}

function _onTouchMove(e) {
  e.preventDefault();
  if (e.touches.length === 1 && _dragging) {
    const dx = e.touches[0].clientX - _lastMouse.x;
    const dy = e.touches[0].clientY - _lastMouse.y;
    _azimuth   += dx * 0.005;
    _elevation += dy * 0.005;
    _elevation  = Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, _elevation));
    _lastMouse  = { x: e.touches[0].clientX, y: e.touches[0].clientY };
  } else if (e.touches.length === 2 && _lastTouchDist !== null) {
    const d = _touchDist(e.touches);
    _camDist   *= _lastTouchDist / d;
    _camDist    = Math.max(1.2, Math.min(12, _camDist));
    _lastTouchDist = d;
  }
}

function _onTouchEnd(e) {
  if (e.touches.length === 0) {
    _dragging      = false;
    _lastTouchDist = null;
  }
}

function _touchDist(touches) {
  const dx = touches[0].clientX - touches[1].clientX;
  const dy = touches[0].clientY - touches[1].clientY;
  return Math.sqrt(dx * dx + dy * dy);
}
