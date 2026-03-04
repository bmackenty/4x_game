/**
 * hex/hex-input.js — Mouse and touch input handling for hex canvas views.
 *
 * Provides pan (drag), zoom (scroll wheel), and click-to-hex detection.
 * Used by both the galaxy map and the planet colony view.
 *
 * Usage:
 *   import { attachHexInput } from "./hex/hex-input.js";
 *
 *   const controls = attachHexInput(canvas, {
 *     hexSize: 22,
 *     onHexClick: ({ q, r }) => { ... },
 *     onHexHover: ({ q, r }) => { ... },  // optional
 *     onViewChanged: (viewState)  => { redraw(); },
 *   });
 *
 *   // Later, to detach listeners:
 *   controls.detach();
 */

import { canvasPointToHex } from "./hex-render.js";


// ---------------------------------------------------------------------------
// Public factory
// ---------------------------------------------------------------------------

/**
 * Attach mouse/touch input listeners to a canvas element.
 *
 * @param {HTMLCanvasElement} canvas
 * @param {{
 *   hexSize:       number,
 *   onHexClick:    function({ q, r }),
 *   onHexHover?:   function({ q, r }),
 *   onViewChanged: function({ panX, panY, zoom }),
 * }} options
 * @returns {{ detach: function, viewState: object }}
 */
export function attachHexInput(canvas, options) {
  const { hexSize, onHexClick, onHexHover, onViewChanged } = options;

  // Mutable view state — modified by event handlers and read by render functions
  const viewState = {
    panX: 0,
    panY: 0,
    zoom: 1.0,
    selectedQ: null,
    selectedR: null,
  };

  // Pan state
  let isDragging   = false;
  let dragStartX   = 0;
  let dragStartY   = 0;
  let dragStartPanX = 0;
  let dragStartPanY = 0;
  let hasDragged   = false;   // True if the mouse actually moved during drag

  // Zoom clamps
  const MIN_ZOOM = 0.3;
  const MAX_ZOOM = 3.0;

  // Tooltip element (created lazily)
  let tooltipEl = null;


  // -------------------------------------------------------------------------
  // Event handlers
  // -------------------------------------------------------------------------

  function onMouseDown(e) {
    if (e.button !== 0) return;    // Left button only
    isDragging   = true;
    hasDragged   = false;
    dragStartX   = e.clientX;
    dragStartY   = e.clientY;
    dragStartPanX = viewState.panX;
    dragStartPanY = viewState.panY;
    canvas.style.cursor = "grabbing";
  }

  function onMouseMove(e) {
    const rect = canvas.getBoundingClientRect();
    const canvasX = e.clientX - rect.left;
    const canvasY = e.clientY - rect.top;

    if (isDragging) {
      const dx = e.clientX - dragStartX;
      const dy = e.clientY - dragStartY;
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) hasDragged = true;

      viewState.panX = dragStartPanX + dx;
      viewState.panY = dragStartPanY + dy;
      onViewChanged({ ...viewState });
    } else {
      // Hover: find the hex under the cursor and call onHexHover
      if (typeof onHexHover === "function") {
        const hex = canvasPointToHex(
          canvasX, canvasY,
          canvas.width, canvas.height,
          viewState, hexSize
        );
        onHexHover(hex);
      }
    }
  }

  function onMouseUp(e) {
    if (e.button !== 0) return;
    isDragging = false;
    canvas.style.cursor = "crosshair";

    if (!hasDragged && typeof onHexClick === "function") {
      // It was a click, not a drag
      const rect = canvas.getBoundingClientRect();
      const canvasX = e.clientX - rect.left;
      const canvasY = e.clientY - rect.top;
      const hex = canvasPointToHex(
        canvasX, canvasY,
        canvas.width, canvas.height,
        viewState, hexSize
      );
      viewState.selectedQ = hex.q;
      viewState.selectedR = hex.r;
      onHexClick(hex);
      onViewChanged({ ...viewState });
    }
  }

  function onMouseLeave() {
    isDragging = false;
    canvas.style.cursor = "crosshair";
  }

  function onWheel(e) {
    e.preventDefault();
    const delta  = e.deltaY > 0 ? 0.9 : 1.1;
    const newZoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, viewState.zoom * delta));

    // Zoom toward the cursor position
    const rect = canvas.getBoundingClientRect();
    const cx = e.clientX - rect.left - canvas.width  / 2;
    const cy = e.clientY - rect.top  - canvas.height / 2;

    // Adjust pan so the point under the cursor stays fixed
    const scale = newZoom / viewState.zoom;
    viewState.panX = cx - scale * (cx - viewState.panX);
    viewState.panY = cy - scale * (cy - viewState.panY);
    viewState.zoom = newZoom;

    onViewChanged({ ...viewState });
  }


  // -------------------------------------------------------------------------
  // Touch support (basic single-finger pan)
  // -------------------------------------------------------------------------

  let lastTouchX = 0;
  let lastTouchY = 0;

  function onTouchStart(e) {
    if (e.touches.length === 1) {
      lastTouchX = e.touches[0].clientX;
      lastTouchY = e.touches[0].clientY;
    }
  }

  function onTouchMove(e) {
    if (e.touches.length === 1) {
      e.preventDefault();
      const dx = e.touches[0].clientX - lastTouchX;
      const dy = e.touches[0].clientY - lastTouchY;
      viewState.panX += dx;
      viewState.panY += dy;
      lastTouchX = e.touches[0].clientX;
      lastTouchY = e.touches[0].clientY;
      onViewChanged({ ...viewState });
    }
  }

  function onTouchEnd(e) {
    // Single tap = click
    if (e.changedTouches.length === 1) {
      const rect = canvas.getBoundingClientRect();
      const canvasX = e.changedTouches[0].clientX - rect.left;
      const canvasY = e.changedTouches[0].clientY - rect.top;
      const hex = canvasPointToHex(
        canvasX, canvasY,
        canvas.width, canvas.height,
        viewState, hexSize
      );
      viewState.selectedQ = hex.q;
      viewState.selectedR = hex.r;
      if (typeof onHexClick === "function") onHexClick(hex);
      onViewChanged({ ...viewState });
    }
  }


  // -------------------------------------------------------------------------
  // Canvas resize observer — keeps canvas pixel size matching its CSS size
  // -------------------------------------------------------------------------

  const resizeObserver = new ResizeObserver(() => {
    canvas.width  = canvas.clientWidth;
    canvas.height = canvas.clientHeight;
    onViewChanged({ ...viewState });
  });
  resizeObserver.observe(canvas);

  // Initial size
  canvas.width  = canvas.clientWidth  || 800;
  canvas.height = canvas.clientHeight || 600;


  // -------------------------------------------------------------------------
  // Attach listeners
  // -------------------------------------------------------------------------

  canvas.addEventListener("mousedown",  onMouseDown);
  canvas.addEventListener("mousemove",  onMouseMove);
  canvas.addEventListener("mouseup",    onMouseUp);
  canvas.addEventListener("mouseleave", onMouseLeave);
  canvas.addEventListener("wheel",      onWheel,  { passive: false });
  canvas.addEventListener("touchstart", onTouchStart, { passive: true });
  canvas.addEventListener("touchmove",  onTouchMove,  { passive: false });
  canvas.addEventListener("touchend",   onTouchEnd,   { passive: true });


  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------

  return {
    /** Current view transform state — read by render functions */
    viewState,

    /** Remove all event listeners and the resize observer */
    detach() {
      canvas.removeEventListener("mousedown",  onMouseDown);
      canvas.removeEventListener("mousemove",  onMouseMove);
      canvas.removeEventListener("mouseup",    onMouseUp);
      canvas.removeEventListener("mouseleave", onMouseLeave);
      canvas.removeEventListener("wheel",      onWheel);
      canvas.removeEventListener("touchstart", onTouchStart);
      canvas.removeEventListener("touchmove",  onTouchMove);
      canvas.removeEventListener("touchend",   onTouchEnd);
      resizeObserver.disconnect();
    },

    /** Programmatically set the selected hex (used by external navigation) */
    selectHex(q, r) {
      viewState.selectedQ = q;
      viewState.selectedR = r;
      onViewChanged({ ...viewState });
    },

    /** Reset pan and zoom to the default centred view */
    resetView() {
      viewState.panX = 0;
      viewState.panY = 0;
      viewState.zoom = 1.0;
      onViewChanged({ ...viewState });
    },
  };
}
