import {
  TOPOGRAPHY_LAYERS,
  TOPOGRAPHY_SECTORS,
  createTopography,
} from "./topography.js";

function emptySectorValues() {
  return Object.fromEntries(TOPOGRAPHY_SECTORS.map(({ id }) => [id, 0]));
}

function latestMetrics(commits) {
  const running = {
    commits: emptySectorValues(),
    churn: emptySectorValues(),
    footprint: emptySectorValues(),
  };
  for (const commit of commits) {
    for (const [sector, record] of Object.entries(commit.sectors ?? {})) {
      if (!Object.hasOwn(running.commits, sector)) continue;
      if (record.files > 0) running.commits[sector] += 1;
      running.churn[sector] += record.additions + record.deletions;
      running.footprint[sector] += record.files;
    }
  }
  return running;
}

function createTerrainMap() {
  const canvas = document.getElementById("ecosystem-topography");
  const viewport = document.getElementById("terrain-panel");
  if (!canvas || !viewport) return;

  const modeLabel = document.getElementById("terrain-mode-label");
  const viewLabel = document.getElementById("terrain-view-label");
  const map = createTopography({
    canvas,
    viewport,
    onViewChange: ({ rotation, zoom }) => {
      if (viewLabel) {
        viewLabel.textContent = `R${rotation} · Z${Math.round(zoom * 100)}`;
      }
    },
  });
  if (!map) return;

  document
    .getElementById("terrain-rotate-left")
    ?.addEventListener("click", map.rotateLeft);
  document
    .getElementById("terrain-rotate-right")
    ?.addEventListener("click", map.rotateRight);
  document
    .getElementById("terrain-zoom-out")
    ?.addEventListener("click", map.zoomOut);
  document
    .getElementById("terrain-zoom-in")
    ?.addEventListener("click", map.zoomIn);
  document
    .getElementById("terrain-reset-view")
    ?.addEventListener("click", map.resetView);

  map.update({ layer: "state", animate: false });
  if (modeLabel) modeLabel.textContent = TOPOGRAPHY_LAYERS.state.label;

  fetch("./chronoscape-snapshot.json", { cache: "no-store" })
    .then((response) => {
      if (!response.ok) throw new Error("Historical snapshot unavailable");
      return response.json();
    })
    .then((snapshot) => {
      if (!snapshot?.available || !snapshot.commits?.length) return;
      const values = latestMetrics(snapshot.commits).commits;
      const latest = snapshot.commits.at(-1);
      map.update({
        layer: "commits",
        values,
        touchedSectors: Object.keys(latest.sectors ?? {}),
        animate: true,
      });
      if (modeLabel) modeLabel.textContent = TOPOGRAPHY_LAYERS.commits.label;
    })
    .catch(() => {
      viewport.dataset.snapshot = "unavailable";
    });
}

createTerrainMap();
