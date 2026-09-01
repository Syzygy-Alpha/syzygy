const GRID_SIZE = 18;
const GRID_POINTS = GRID_SIZE + 1;

export const TOPOGRAPHY_SECTORS = [
  { id: "foundation", label: "Foundation", kind: "module", status: "current", x: 8.7, z: 8.5 },
  { id: "forge", label: "Forge", kind: "module", status: "current", x: 4.6, z: 7.2 },
  { id: "mycelium", label: "Mycelium", kind: "module", status: "current", x: 3, z: 13 },
  { id: "observatory", label: "Observatory", kind: "module", status: "current", x: 12.8, z: 6.5 },
  { id: "nerv", label: "NERV", kind: "module", status: "current", x: 9, z: 2.6 },
  { id: "tungsten", label: "Tungsten", kind: "module", status: "future", x: 6, z: 13 },
  { id: "coppermind", label: "Coppermind", kind: "module", status: "future", x: 10.2, z: 15 },
  { id: "magi", label: "MAGI", kind: "module", status: "future", x: 13.7, z: 13.3 },
  { id: "balance", label: "Balance", kind: "module", status: "future", x: 16, z: 10 },
  { id: "elric", label: "Elric", kind: "module", status: "future", x: 5, z: 2.4 },
  { id: "imrryr", label: "Imrryr", kind: "module", status: "future", x: 15.3, z: 4 },
  { id: "bastion", label: "Bastion", kind: "module", status: "future", x: 2, z: 16.1 },
  { id: "site", label: "Site", kind: "repository", status: "support", x: 16.6, z: 1.6 },
  { id: "docs", label: "Docs", kind: "repository", status: "support", x: 16.5, z: 16.1 },
  { id: "root", label: "Root", kind: "repository", status: "support", x: 1.4, z: 1.5 },
];

export const TOPOGRAPHY_LAYERS = {
  commits: { label: "COMMITS / CUMULATIVE", unit: "commits", accent: "#c9ff2f" },
  churn: { label: "CHURN / LINES TOUCHED", unit: "linhas", accent: "#ff304f" },
  footprint: { label: "FOOTPRINT / FILE TOUCHES", unit: "arquivos", accent: "#7c2ca7" },
  state: { label: "ARCHITECTURAL STATE", unit: "estado", accent: "#9d42d1" },
};

const compactFormatter = new Intl.NumberFormat("pt-BR", {
  notation: "compact",
  maximumFractionDigits: 1,
});

function clamp(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value));
}

function hexToRgb(hex) {
  const value = Number.parseInt(hex.slice(1), 16);
  return [value >> 16, (value >> 8) & 255, value & 255];
}

function stateValues() {
  return Object.fromEntries(
    TOPOGRAPHY_SECTORS.map((sector) => [
      sector.id,
      sector.status === "current" ? 100 : sector.status === "support" ? 52 : 16,
    ]),
  );
}

export function createTopography({
  canvas,
  viewport = canvas?.parentElement,
  onSectorSelect,
  onViewChange,
} = {}) {
  if (!canvas || !viewport) return null;
  const context = canvas.getContext("2d");
  if (!context) return null;

  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const constrainedHardware =
    (Number(navigator.deviceMemory) || Infinity) <= 4 ||
    (Number(navigator.hardwareConcurrency) || Infinity) <= 4;
  const sectorById = new Map(
    TOPOGRAPHY_SECTORS.map((sector) => [sector.id, sector]),
  );
  const monoFont =
    getComputedStyle(document.documentElement).getPropertyValue("--chrono-mono").trim() ||
    getComputedStyle(document.documentElement).getPropertyValue("--mono").trim() ||
    "ui-monospace, SFMono-Regular, Consolas, monospace";

  const state = {
    width: 0,
    height: 0,
    dpr: 1,
    layer: "state",
    values: stateValues(),
    touched: new Set(),
    activeSector: "foundation",
    rotation: 0,
    zoom: 1,
    currentHeights: new Float32Array(GRID_POINTS * GRID_POINTS),
    targetHeights: new Float32Array(GRID_POINTS * GRID_POINTS),
    hitAreas: [],
    frame: null,
    visible: true,
    initialized: false,
    terrainSignature: "",
  };

  function rotateGrid(x, z) {
    if (state.rotation === 1) return [z, GRID_SIZE - x];
    if (state.rotation === 2) return [GRID_SIZE - x, GRID_SIZE - z];
    if (state.rotation === 3) return [GRID_SIZE - z, x];
    return [x, z];
  }

  function project(x, z, height = 0) {
    const [rotatedX, rotatedZ] = rotateGrid(x, z);
    const scale = Math.min(state.width / 930, state.height / 640, 1.2);
    const tileWidth = 45 * scale * state.zoom;
    const tileHeight = 23 * scale * state.zoom;
    const elevation = 52 * scale * state.zoom;
    return {
      x: state.width / 2 + ((rotatedX - rotatedZ) * tileWidth) / 2,
      y:
        state.height * 0.57 +
        ((rotatedX + rotatedZ - GRID_SIZE) * tileHeight) / 2 -
        height * elevation,
      depth: rotatedX + rotatedZ,
    };
  }

  function polygon(points, fill, stroke, width = 1) {
    context.beginPath();
    context.moveTo(points[0].x, points[0].y);
    points.slice(1).forEach((point) => context.lineTo(point.x, point.y));
    context.closePath();
    if (fill) {
      context.fillStyle = fill;
      context.fill();
    }
    if (stroke) {
      context.strokeStyle = stroke;
      context.lineWidth = width;
      context.stroke();
    }
  }

  function computeTerrain() {
    const maximum = Math.max(1, ...Object.values(state.values));
    for (let z = 0; z < GRID_POINTS; z += 1) {
      for (let x = 0; x < GRID_POINTS; x += 1) {
        let height = 0.06 + Math.sin(x * 0.69 + z * 0.27) * 0.022;
        for (const sector of TOPOGRAPHY_SECTORS) {
          const value = state.values[sector.id] ?? 0;
          const normalized =
            value > 0 ? Math.log1p(value) / Math.log1p(maximum) : 0;
          const pulse = state.touched.has(sector.id) ? 0.34 : 0;
          const sigma = sector.kind === "repository" ? 1.48 : 1.86;
          const distanceX = x - sector.x;
          const distanceZ = z - sector.z;
          height +=
            (normalized * 1.85 + pulse) *
            Math.exp(
              -(distanceX * distanceX + distanceZ * distanceZ) /
                (2 * sigma * sigma),
            );
        }
        state.targetHeights[z * GRID_POINTS + x] = Math.max(0, height);
      }
    }
  }

  function heightAt(x, z) {
    const left = clamp(Math.floor(x), 0, GRID_SIZE);
    const top = clamp(Math.floor(z), 0, GRID_SIZE);
    const right = clamp(left + 1, 0, GRID_SIZE);
    const bottom = clamp(top + 1, 0, GRID_SIZE);
    const horizontal = x - left;
    const vertical = z - top;
    const first =
      state.currentHeights[top * GRID_POINTS + left] * (1 - horizontal) +
      state.currentHeights[top * GRID_POINTS + right] * horizontal;
    const second =
      state.currentHeights[bottom * GRID_POINTS + left] * (1 - horizontal) +
      state.currentHeights[bottom * GRID_POINTS + right] * horizontal;
    return first * (1 - vertical) + second * vertical;
  }

  function drawTerrainBase() {
    const top = [
      project(0, 0),
      project(GRID_SIZE, 0),
      project(GRID_SIZE, GRID_SIZE),
      project(0, GRID_SIZE),
    ];
    const bottom = top.map((point) => ({ ...point, y: point.y + 15 }));
    polygon(
      [top[1], top[2], bottom[2], bottom[1]],
      "rgba(5,4,6,.88)",
      "rgba(238,238,240,.05)",
    );
    polygon(
      [top[2], top[3], bottom[3], bottom[2]],
      "rgba(3,3,4,.94)",
      "rgba(238,238,240,.04)",
    );
    polygon(top, "rgba(14,10,17,.82)", "rgba(157,66,209,.22)");
  }

  function drawTerrainMesh() {
    let maximum = 0.01;
    for (const value of state.currentHeights) maximum = Math.max(maximum, value);
    const [accentRed, accentGreen, accentBlue] = hexToRgb(
      TOPOGRAPHY_LAYERS[state.layer].accent,
    );
    const cells = [];
    for (let z = 0; z < GRID_SIZE; z += 1) {
      for (let x = 0; x < GRID_SIZE; x += 1) {
        const heights = [
          state.currentHeights[z * GRID_POINTS + x],
          state.currentHeights[z * GRID_POINTS + x + 1],
          state.currentHeights[(z + 1) * GRID_POINTS + x + 1],
          state.currentHeights[(z + 1) * GRID_POINTS + x],
        ];
        const points = [
          project(x, z, heights[0]),
          project(x + 1, z, heights[1]),
          project(x + 1, z + 1, heights[2]),
          project(x, z + 1, heights[3]),
        ];
        cells.push({
          x,
          z,
          heights,
          points,
          depth: points.reduce((sum, point) => sum + point.depth, 0) / 4,
        });
      }
    }
    cells.sort((left, right) => left.depth - right.depth);

    for (const cell of cells) {
      const average =
        cell.heights.reduce((sum, value) => sum + value, 0) / 4;
      const normalized = average / maximum;
      const hot = TOPOGRAPHY_SECTORS.some((sector) => {
        if (!state.touched.has(sector.id)) return false;
        const distanceX = cell.x + 0.5 - sector.x;
        const distanceZ = cell.z + 0.5 - sector.z;
        return distanceX * distanceX + distanceZ * distanceZ < 4.8;
      });
      const activeSector = sectorById.get(state.activeSector);
      const active = activeSector
        ? (cell.x + 0.5 - activeSector.x) ** 2 +
            (cell.z + 0.5 - activeSector.z) ** 2 <
          3.5
        : false;
      const alpha = 0.19 + normalized * 0.22;
      const fill = hot
        ? `rgba(255,48,79,${0.28 + normalized * 0.42})`
        : active
          ? `rgba(${accentRed},${accentGreen},${accentBlue},${alpha + 0.14})`
          : `rgba(${Math.round(accentRed * 0.35 + 14)},${Math.round(accentGreen * 0.35 + 10)},${Math.round(accentBlue * 0.35 + 18)},${alpha})`;
      const stroke = hot
        ? "rgba(255,48,79,.22)"
        : `rgba(${accentRed},${accentGreen},${accentBlue},${0.05 + normalized * 0.1})`;
      polygon(cell.points, fill, stroke, 0.65);
    }
  }

  function drawMarkers() {
    state.hitAreas = [];
    const layer = TOPOGRAPHY_LAYERS[state.layer];
    const ordered = TOPOGRAPHY_SECTORS.map((sector) => ({
      sector,
      point: project(sector.x, sector.z, heightAt(sector.x, sector.z)),
    })).sort((left, right) => left.point.depth - right.point.depth);

    for (const { sector, point } of ordered) {
      const active = sector.id === state.activeSector;
      const hot = state.touched.has(sector.id);
      const markerY = point.y - 17;
      context.save();
      context.beginPath();
      context.moveTo(point.x, point.y + 2);
      context.lineTo(point.x, markerY);
      context.strokeStyle = hot
        ? "rgba(255,48,79,.8)"
        : active
          ? layer.accent
          : "rgba(238,238,240,.24)";
      context.lineWidth = hot || active ? 1.4 : 0.7;
      context.stroke();
      context.beginPath();
      context.arc(point.x, markerY, hot ? 4.8 : 3, 0, Math.PI * 2);
      context.fillStyle = hot
        ? "#ff304f"
        : active
          ? layer.accent
          : "rgba(238,238,240,.7)";
      context.shadowColor = hot ? "rgba(255,48,79,.8)" : "transparent";
      context.shadowBlur = hot ? 15 : 0;
      context.fill();
      context.shadowBlur = 0;

      const label = sector.label.toUpperCase();
      const valueText =
        state.layer === "state"
          ? sector.status === "current"
            ? "LIVE"
            : sector.status === "future"
              ? "FUT"
              : "AUX"
          : compactFormatter.format(state.values[sector.id] ?? 0);
      context.font = `700 8px ${monoFont}`;
      const labelWidth = Math.max(
        76,
        context.measureText(label).width +
          context.measureText(valueText).width +
          22,
      );
      const labelX = point.x - labelWidth / 2;
      const labelY = markerY - 27;
      context.fillStyle = active ? layer.accent : "rgba(7,6,8,.88)";
      context.strokeStyle = hot
        ? "rgba(255,48,79,.78)"
        : active
          ? layer.accent
          : "rgba(238,238,240,.17)";
      if (sector.status === "future" && !active) context.setLineDash([3, 3]);
      context.fillRect(labelX, labelY, labelWidth, 19);
      context.strokeRect(labelX + 0.5, labelY + 0.5, labelWidth - 1, 18);
      context.setLineDash([]);
      context.fillStyle = active
        ? "#070608"
        : hot
          ? "#ff304f"
          : "rgba(238,238,240,.68)";
      context.textBaseline = "middle";
      context.fillText(label, labelX + 6, labelY + 9.5);
      context.textAlign = "right";
      context.fillStyle = active
        ? "rgba(7,6,8,.65)"
        : "rgba(238,238,240,.33)";
      context.fillText(valueText, labelX + labelWidth - 6, labelY + 9.5);
      context.textAlign = "left";
      state.hitAreas.push({
        sectorId: sector.id,
        x: labelX - 4,
        y: labelY - 4,
        width: labelWidth + 8,
        height: 30,
      });
      context.restore();
    }
  }

  function requestMap() {
    if (state.visible && state.frame === null) {
      state.frame = requestAnimationFrame(renderMap);
    }
  }

  function renderMap() {
    state.frame = null;
    let moving = false;
    for (let index = 0; index < state.currentHeights.length; index += 1) {
      const difference =
        state.targetHeights[index] - state.currentHeights[index];
      if (Math.abs(difference) > 0.002) moving = true;
      state.currentHeights[index] += difference * (reducedMotion ? 1 : 0.12);
    }
    context.setTransform(state.dpr, 0, 0, state.dpr, 0, 0);
    context.clearRect(0, 0, state.width, state.height);
    drawTerrainBase();
    drawTerrainMesh();
    drawMarkers();
    if (moving) requestMap();
  }

  function resize() {
    const bounds = viewport.getBoundingClientRect();
    state.width = Math.max(1, bounds.width);
    state.height = Math.max(1, bounds.height);
    state.dpr = Math.min(
      devicePixelRatio || 1,
      constrainedHardware ? 1 : 1.5,
    );
    canvas.width = Math.round(state.width * state.dpr);
    canvas.height = Math.round(state.height * state.dpr);
    canvas.style.width = `${state.width}px`;
    canvas.style.height = `${state.height}px`;
    requestMap();
  }

  function notifyView() {
    onViewChange?.({ rotation: state.rotation, zoom: state.zoom });
  }

  function rotate(direction) {
    state.rotation = (state.rotation + direction + 4) % 4;
    notifyView();
    requestMap();
  }

  function zoom(delta) {
    state.zoom = clamp(state.zoom + delta, 0.72, 1.35);
    notifyView();
    requestMap();
  }

  function resetView() {
    state.rotation = 0;
    state.zoom = 1;
    notifyView();
    requestMap();
  }

  function selectAt(clientX, clientY) {
    const bounds = canvas.getBoundingClientRect();
    const x = clientX - bounds.left;
    const y = clientY - bounds.top;
    const hit = [...state.hitAreas]
      .reverse()
      .find(
        (area) =>
          x >= area.x &&
          x <= area.x + area.width &&
          y >= area.y &&
          y <= area.y + area.height,
      );
    if (!hit) return null;
    state.activeSector = hit.sectorId;
    onSectorSelect?.(hit.sectorId);
    requestMap();
    return hit.sectorId;
  }

  function update({
    layer = state.layer,
    values,
    touchedSectors = [],
    activeSector = state.activeSector,
    animate = true,
  } = {}) {
    if (!Object.hasOwn(TOPOGRAPHY_LAYERS, layer)) return;
    const nextValues = layer === "state" ? stateValues() : { ...(values ?? {}) };
    const nextTouched = [...touchedSectors].filter((id) => sectorById.has(id));
    const signature = `${layer}|${TOPOGRAPHY_SECTORS.map((sector) => nextValues[sector.id] ?? 0).join(",")}|${nextTouched.sort().join(",")}`;
    const terrainChanged = signature !== state.terrainSignature;
    const activeChanged = activeSector !== state.activeSector;
    state.layer = layer;
    state.values = nextValues;
    state.touched = new Set(nextTouched);
    state.activeSector = sectorById.has(activeSector)
      ? activeSector
      : state.activeSector;

    if (terrainChanged) {
      state.terrainSignature = signature;
      computeTerrain();
      if (!state.initialized || reducedMotion || !animate || !state.visible) {
        state.currentHeights.set(state.targetHeights);
      }
      state.initialized = true;
    }
    if (terrainChanged || activeChanged) requestMap();
  }

  canvas.addEventListener("click", (event) => {
    selectAt(event.clientX, event.clientY);
  });
  canvas.addEventListener(
    "wheel",
    (event) => {
      event.preventDefault();
      zoom(-Math.sign(event.deltaY) * 0.07);
    },
    { passive: false },
  );

  let resizeFrame;
  window.addEventListener("resize", () => {
    cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(resize);
  });

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      ([entry]) => {
        state.visible = entry.isIntersecting;
        if (!state.visible && state.frame !== null) {
          cancelAnimationFrame(state.frame);
          state.frame = null;
          state.currentHeights.set(state.targetHeights);
        }
        if (state.visible) requestMap();
      },
      { rootMargin: "120px 0px" },
    );
    observer.observe(viewport);
  }

  resize();
  notifyView();

  return {
    update,
    resize,
    rotateLeft: () => rotate(-1),
    rotateRight: () => rotate(1),
    zoomIn: () => zoom(0.1),
    zoomOut: () => zoom(-0.1),
    resetView,
    selectAt,
  };
}
