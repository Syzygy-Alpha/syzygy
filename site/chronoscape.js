import { TOPOGRAPHY_LAYERS, createTopography } from "./topography.js";

const officialModules = [
  "foundation",
  "forge",
  "mycelium",
  "observatory",
  "nerv",
  "tungsten",
  "coppermind",
  "magi",
  "balance",
  "elric",
  "imrryr",
  "bastion",
];

const sectors = [
  {
    id: "foundation",
    label: "Foundation",
    shortLabel: "FOUND",
    x: 0.46,
    y: 0.43,
    status: "functional",
    description: "Núcleo técnico compartilhado e primeiro módulo funcional.",
  },
  {
    id: "forge",
    label: "Forge",
    shortLabel: "FORGE",
    x: 0.23,
    y: 0.51,
    status: "functional",
    description: "Engenharia local, projetos e automação declarada.",
  },
  {
    id: "mycelium",
    label: "Mycelium",
    shortLabel: "MYCEL",
    x: 0.3,
    y: 0.28,
    status: "functional",
    description: "Malha distribuída e identidade de nós locais.",
  },
  {
    id: "observatory",
    label: "Observatory",
    shortLabel: "OBS",
    x: 0.67,
    y: 0.45,
    status: "functional",
    description: "Visibilidade local de saúde e tendências.",
  },
  {
    id: "nerv",
    label: "NERV",
    shortLabel: "NERV",
    x: 0.55,
    y: 0.22,
    status: "functional",
    description: "Centro operacional local do ecossistema.",
  },
  {
    id: "tungsten",
    label: "Tungsten",
    shortLabel: "TUNG",
    x: 0.78,
    y: 0.27,
    status: "future",
    description: "Direção futura para confiança e segurança.",
  },
  {
    id: "coppermind",
    label: "Coppermind",
    shortLabel: "COPPER",
    x: 0.8,
    y: 0.57,
    status: "future",
    description: "Direção futura para memória permanente e conhecimento.",
  },
  {
    id: "magi",
    label: "MAGI",
    shortLabel: "MAGI",
    x: 0.72,
    y: 0.75,
    status: "future",
    description: "Direção futura para inteligência especializada.",
  },
  {
    id: "balance",
    label: "Balance",
    shortLabel: "BAL",
    x: 0.53,
    y: 0.84,
    status: "future",
    description: "Direção futura para governança e decisão.",
  },
  {
    id: "elric",
    label: "Elric",
    shortLabel: "ELRIC",
    x: 0.37,
    y: 0.74,
    status: "future",
    description: "Direção futura para contexto e personalização do usuário.",
  },
  {
    id: "imrryr",
    label: "Imrryr",
    shortLabel: "IMR",
    x: 0.2,
    y: 0.78,
    status: "future",
    description: "Direção futura para aplicações próprias e experimentais.",
  },
  {
    id: "bastion",
    label: "Bastion",
    shortLabel: "BAS",
    x: 0.1,
    y: 0.36,
    status: "future",
    description: "Direção futura para um laboratório de segurança isolado.",
  },
  {
    id: "site",
    label: "Site",
    shortLabel: "SITE",
    x: 0.08,
    y: 0.13,
    status: "repository",
    description: "Superfície institucional do repositório; não é um módulo oficial.",
  },
  {
    id: "docs",
    label: "Docs",
    shortLabel: "DOCS",
    x: 0.94,
    y: 0.12,
    status: "repository",
    description: "Documentação técnica e registros de evolução; não é um módulo oficial.",
  },
  {
    id: "root",
    label: "Root",
    shortLabel: "ROOT",
    x: 0.95,
    y: 0.82,
    status: "repository",
    description: "Arquivos de raiz do repositório e suporte transversal.",
  },
];

const sectorById = new Map(sectors.map((sector) => [sector.id, sector]));
const formatter = new Intl.NumberFormat("pt-BR");
const dateFormatter = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "short",
  year: "numeric",
  timeZone: "UTC",
});

const elements = {
  terrain: document.getElementById("chronoscape-terrain"),
  terrainEmpty: document.getElementById("terrain-empty"),
  layerButtons: [...document.querySelectorAll("[data-chrono-layer]")],
  sectorName: document.getElementById("sector-name"),
  sectorValue: document.getElementById("sector-value"),
  sectorDescription: document.getElementById("sector-description"),
  sectorPicker: document.getElementById("chrono-sector"),
  range: document.getElementById("chrono-range"),
  previous: document.getElementById("previous-stratum"),
  next: document.getElementById("next-stratum"),
  timelineLabel: document.getElementById("timeline-label"),
  stratumPosition: document.getElementById("stratum-position"),
  stratumDate: document.getElementById("stratum-date"),
  stratumKind: document.getElementById("stratum-kind"),
  stratumTitle: document.getElementById("stratum-title-copy"),
  stratumFiles: document.getElementById("stratum-files"),
  stratumAdditions: document.getElementById("stratum-additions"),
  stratumDeletions: document.getElementById("stratum-deletions"),
  stratumSectors: document.getElementById("stratum-sectors"),
  velocity: document.getElementById("velocity-chart"),
  churn: document.getElementById("churn-chart"),
  distribution: document.getElementById("distribution-chart"),
  distributionList: document.getElementById("distribution-list"),
  velocitySummary: document.getElementById("velocity-summary"),
  churnSummary: document.getElementById("churn-summary"),
  heroCommits: document.getElementById("hero-commits"),
  heroDays: document.getElementById("hero-days"),
  heroSectors: document.getElementById("hero-sectors"),
  terrainMode: document.getElementById("chrono-terrain-mode"),
  viewLabel: document.getElementById("chrono-view-label"),
  rotateLeft: document.getElementById("rotate-left"),
  rotateRight: document.getElementById("rotate-right"),
  zoomIn: document.getElementById("zoom-in"),
  zoomOut: document.getElementById("zoom-out"),
  resetView: document.getElementById("reset-view"),
};

const state = {
  layer: "commits",
  activeSector: "foundation",
  index: 0,
  snapshot: null,
  metrics: [],
  historyAvailable: false,
};

const topography = createTopography({
  canvas: elements.terrain,
  viewport: elements.terrain.closest(".terrain-stage"),
  onSectorSelect: (sectorId) => {
    if (!sectorById.has(sectorId)) return;
    state.activeSector = sectorId;
    elements.sectorPicker.value = sectorId;
    render();
  },
  onViewChange: ({ rotation, zoom }) => {
    elements.viewLabel.textContent = `R${rotation} · Z${Math.round(zoom * 100)}`;
  },
});

function formatNumber(value) {
  return formatter.format(Math.max(0, Number(value) || 0));
}

function formatDate(value) {
  if (!value) return "Snapshot indisponível";
  return dateFormatter.format(new Date(`${value}T12:00:00Z`));
}

function emptySectors() {
  return Object.fromEntries(sectors.map((sector) => [sector.id, 0]));
}

function currentCommit() {
  return state.snapshot?.commits?.[state.index] ?? null;
}

function metricAtIndex() {
  return state.metrics[state.index] ?? {
    commits: emptySectors(),
    churn: emptySectors(),
    footprint: emptySectors(),
    additions: 0,
    deletions: 0,
    files: 0,
  };
}

function sectorRecord(commit, sectorId) {
  return commit?.sectors?.[sectorId] ?? {
    files: 0,
    additions: 0,
    deletions: 0,
  };
}

function createMetrics(commits) {
  const running = {
    commits: emptySectors(),
    churn: emptySectors(),
    footprint: emptySectors(),
    additions: 0,
    deletions: 0,
    files: 0,
  };

  return commits.map((commit) => {
    for (const sector of sectors) {
      const record = sectorRecord(commit, sector.id);
      if (record.files > 0) running.commits[sector.id] += 1;
      running.churn[sector.id] += record.additions + record.deletions;
      running.footprint[sector.id] += record.files;
    }
    running.additions += commit.stats?.additions ?? 0;
    running.deletions += commit.stats?.deletions ?? 0;
    running.files += commit.stats?.files ?? 0;
    return {
      commits: { ...running.commits },
      churn: { ...running.churn },
      footprint: { ...running.footprint },
      additions: running.additions,
      deletions: running.deletions,
      files: running.files,
    };
  });
}

function stateWeight(sector) {
  if (sector.status === "functional") return 1;
  if (sector.status === "future") return 0.34;
  return 0.15;
}

function valueForSector(sector) {
  if (state.layer === "state") return stateWeight(sector);
  return metricAtIndex()[state.layer]?.[sector.id] ?? 0;
}

function resizeCanvas(canvas) {
  const bounds = canvas.getBoundingClientRect();
  const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
  canvas.width = Math.max(1, Math.round(bounds.width * ratio));
  canvas.height = Math.max(1, Math.round(bounds.height * ratio));
  const context = canvas.getContext("2d");
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  return { context, width: bounds.width, height: bounds.height };
}

function drawTerrain() {
  const values = Object.fromEntries(
    sectors.map((sector) => [sector.id, valueForSector(sector)]),
  );
  topography?.update({
    layer: state.layer,
    values,
    touchedSectors: Object.keys(currentCommit()?.sectors ?? {}),
    activeSector: state.activeSector,
    animate: state.historyAvailable,
  });
  elements.terrainMode.textContent = TOPOGRAPHY_LAYERS[state.layer].label;
}

function groupedDays() {
  const groups = new Map();
  for (const commit of state.snapshot?.commits?.slice(0, state.index + 1) ?? []) {
    const entry = groups.get(commit.date) ?? {
      date: commit.date,
      commits: 0,
      additions: 0,
      deletions: 0,
    };
    entry.commits += 1;
    entry.additions += commit.stats?.additions ?? 0;
    entry.deletions += commit.stats?.deletions ?? 0;
    groups.set(commit.date, entry);
  }
  return [...groups.values()];
}

function chartContext(canvas) {
  const field = resizeCanvas(canvas);
  field.context.clearRect(0, 0, field.width, field.height);
  return field;
}

function drawChartGrid(context, width, height) {
  context.strokeStyle = "rgba(241,237,242,.09)";
  context.lineWidth = 1;
  for (let index = 1; index < 4; index += 1) {
    const y = (height / 4) * index;
    context.beginPath();
    context.moveTo(0, y);
    context.lineTo(width, y);
    context.stroke();
  }
}

function drawVelocity() {
  const { context, width, height } = chartContext(elements.velocity);
  drawChartGrid(context, width, height);
  const days = groupedDays();
  const maximum = Math.max(1, ...days.map((day) => day.commits));
  context.beginPath();
  days.forEach((day, index) => {
    const x = days.length === 1 ? width / 2 : (index / (days.length - 1)) * width;
    const y = height - (day.commits / maximum) * (height - 14) - 7;
    if (index === 0) context.moveTo(x, y);
    else context.lineTo(x, y);
  });
  context.lineWidth = 2;
  context.strokeStyle = "#ccff45";
  context.stroke();
  if (days.length) {
    const latest = days.at(-1);
    elements.velocitySummary.textContent = `${formatNumber(latest.commits)} mudança${latest.commits === 1 ? "" : "s"} no último dia registrado.`;
  } else {
    elements.velocitySummary.textContent = "Snapshot histórico indisponível.";
  }
}

function drawChurn() {
  const { context, width, height } = chartContext(elements.churn);
  drawChartGrid(context, width, height);
  const days = groupedDays();
  const maximum = Math.max(
    1,
    ...days.map((day) => Math.max(day.additions, day.deletions)),
  );
  const columnWidth = Math.max(2, width / Math.max(days.length, 1));
  days.forEach((day, index) => {
    const x = index * columnWidth;
    const additions = (day.additions / maximum) * (height - 10);
    const deletions = (day.deletions / maximum) * (height - 10);
    context.fillStyle = "rgba(112,214,236,.78)";
    context.fillRect(x + 1, height - additions, Math.max(1, columnWidth * 0.4), additions);
    context.fillStyle = "rgba(255,95,115,.74)";
    context.fillRect(x + 1 + columnWidth * 0.44, height - deletions, Math.max(1, columnWidth * 0.4), deletions);
  });
  const metric = metricAtIndex();
  elements.churnSummary.textContent = `+${formatNumber(metric.additions)} adições · −${formatNumber(metric.deletions)} remoções acumuladas.`;
}

function drawDistribution() {
  const { context, width, height } = chartContext(elements.distribution);
  const values = sectors.map((sector) => ({
    sector,
    value: valueForSector(sector),
  }));
  const total = values.reduce((sum, item) => sum + item.value, 0);
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) * 0.36;
  let angle = -Math.PI / 2;
  values.forEach((item, index) => {
    const sweep = total ? (item.value / total) * Math.PI * 2 : 0;
    context.beginPath();
    context.moveTo(centerX, centerY);
    context.arc(centerX, centerY, radius, angle, angle + sweep);
    context.closePath();
    context.fillStyle = item.sector.id === state.activeSector
      ? "#ccff45"
      : index % 3 === 0
        ? "#9d42d1"
        : index % 3 === 1
          ? "#70d6ec"
          : "#ff5f73";
    context.fill();
    angle += sweep;
  });
  context.beginPath();
  context.arc(centerX, centerY, radius * 0.55, 0, Math.PI * 2);
  context.fillStyle = "#12101a";
  context.fill();
  context.fillStyle = "#f1edf2";
  context.font = "700 10px var(--chrono-mono)";
  context.textAlign = "center";
  context.fillText(state.layer.toUpperCase(), centerX, centerY + 3);

  const highest = values
    .filter((item) => item.value > 0)
    .sort((left, right) => right.value - left.value)
    .slice(0, 5);
  elements.distributionList.replaceChildren(
    ...highest.map((item) => {
      const row = document.createElement("li");
      if (item.sector.id === state.activeSector) row.classList.add("active");
      const label = document.createElement("span");
      label.textContent = item.sector.label;
      const track = document.createElement("i");
      const fill = document.createElement("b");
      fill.style.width = `${total ? (item.value / total) * 100 : 0}%`;
      track.append(fill);
      const value = document.createElement("span");
      value.textContent = formatNumber(item.value);
      row.append(label, track, value);
      return row;
    }),
  );
}

function updateReadout() {
  const sector = sectorById.get(state.activeSector) ?? sectors[0];
  const currentValue = valueForSector(sector);
  const layerLabels = {
    commits: "commit(s) acumulado(s)",
    churn: "linhas alteradas",
    footprint: "arquivos alcançados",
    state: sector.status === "functional" ? "funcional · v0.1" : sector.status === "future" ? "conceito · futuro" : "setor auxiliar",
  };
  elements.sectorName.textContent = sector.label;
  elements.sectorValue.textContent = state.layer === "state"
    ? layerLabels.state
    : `${formatNumber(currentValue)} ${layerLabels[state.layer]}`;
  elements.sectorDescription.textContent = sector.description;

  const commit = currentCommit();
  const total = state.snapshot?.commits?.length ?? 0;
  elements.stratumPosition.textContent = total ? `${state.index + 1} / ${total}` : "— / —";
  elements.stratumDate.textContent = commit ? formatDate(commit.date) : "Snapshot indisponível";
  elements.stratumKind.textContent = "MUDANÇA AGREGADA";
  elements.stratumTitle.textContent = commit
    ? `Estrato ${String(state.index + 1).padStart(2, "0")} de ${String(total).padStart(2, "0")}`
    : "Aguardando dados locais";
  elements.stratumFiles.textContent = formatNumber(commit?.stats?.files);
  elements.stratumAdditions.textContent = `+${formatNumber(commit?.stats?.additions)}`;
  elements.stratumDeletions.textContent = `−${formatNumber(commit?.stats?.deletions)}`;
  elements.stratumSectors.replaceChildren(
    ...(commit
      ? Object.entries(commit.sectors ?? {})
          .filter(([, record]) => record.files > 0)
          .sort(([, left], [, right]) => right.files - left.files)
          .map(([id, record]) => {
            const row = document.createElement("li");
            const sectorName = document.createElement("span");
            sectorName.textContent = sectorById.get(id)?.label ?? id;
            const sectorFiles = document.createElement("span");
            sectorFiles.textContent = `${formatNumber(record.files)} arquivo${record.files === 1 ? "" : "s"}`;
            row.append(sectorName, sectorFiles);
            return row;
          })
      : []),
  );
  if (!elements.stratumSectors.children.length) {
    const row = document.createElement("li");
    row.textContent = "Nenhum setor registrado neste estrato.";
    elements.stratumSectors.append(row);
  }

  elements.timelineLabel.textContent = commit ? formatDate(commit.date) : "—";
  elements.range.value = String(state.index);
  const days = state.snapshot?.range?.dayCount;
  elements.heroCommits.textContent = formatNumber(total);
  elements.heroDays.textContent = formatNumber(days);
  elements.heroSectors.textContent = String(sectors.length);
}

function render() {
  updateReadout();
  drawTerrain();
  drawVelocity();
  drawChurn();
  drawDistribution();
}

function selectLayer(layer) {
  if (!Object.hasOwn({ commits: true, churn: true, footprint: true, state: true }, layer)) return;
  if (!state.historyAvailable && layer !== "state") return;
  state.layer = layer;
  elements.layerButtons.forEach((button) => {
    const selected = button.dataset.chronoLayer === layer;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
  render();
}

function setHistoryAvailability(available) {
  state.historyAvailable = available;
  elements.layerButtons.forEach((button) => {
    const historicalLayer = button.dataset.chronoLayer !== "state";
    const selected = button.dataset.chronoLayer === state.layer;
    button.disabled = !available && historicalLayer;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
  elements.range.disabled = !available;
  elements.previous.disabled = !available;
  elements.next.disabled = !available;
}

function selectIndex(index) {
  const maximum = Math.max(0, (state.snapshot?.commits?.length ?? 1) - 1);
  state.index = Math.max(0, Math.min(maximum, Number(index) || 0));
  render();
}

function populateSectorPicker() {
  elements.sectorPicker.replaceChildren(
    ...sectors.map((sector) => {
      const option = document.createElement("option");
      option.value = sector.id;
      option.textContent = `${sector.label} · ${sector.status === "repository" ? "setor auxiliar" : sector.status === "functional" ? "funcional" : "futuro"}`;
      return option;
    }),
  );
  elements.sectorPicker.value = state.activeSector;
}

function attachInteractions() {
  elements.layerButtons.forEach((button) =>
    button.addEventListener("click", () => selectLayer(button.dataset.chronoLayer)),
  );
  elements.range.addEventListener("input", () => selectIndex(elements.range.value));
  elements.previous.addEventListener("click", () => selectIndex(state.index - 1));
  elements.next.addEventListener("click", () => selectIndex(state.index + 1));
  elements.sectorPicker.addEventListener("change", () => {
    state.activeSector = elements.sectorPicker.value;
    render();
  });
  elements.rotateLeft.addEventListener("click", topography.rotateLeft);
  elements.rotateRight.addEventListener("click", topography.rotateRight);
  elements.zoomIn.addEventListener("click", topography.zoomIn);
  elements.zoomOut.addEventListener("click", topography.zoomOut);
  elements.resetView.addEventListener("click", topography.resetView);
  let resizeFrame;
  window.addEventListener("resize", () => {
    cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(render);
  });
}

async function loadSnapshot() {
  try {
    const response = await fetch("./chronoscape-snapshot.json", {
      cache: "no-store",
    });
    if (!response.ok) throw new Error("Chronoscape snapshot is unavailable.");
    const snapshot = await response.json();
    if (!snapshot?.available || !Array.isArray(snapshot.commits) || !snapshot.commits.length) {
      throw new Error("Chronoscape snapshot has no public history.");
    }
    state.snapshot = snapshot;
    state.metrics = createMetrics(snapshot.commits);
    state.index = snapshot.commits.length - 1;
    elements.range.max = String(state.index);
    elements.range.value = String(state.index);
    setHistoryAvailability(true);
    elements.terrainEmpty.hidden = true;
  } catch {
    state.snapshot = {
      available: false,
      commits: [],
      range: { dayCount: 0, commitCount: 0 },
    };
    state.metrics = [];
    state.index = 0;
    state.layer = "state";
    elements.range.max = "0";
    elements.range.value = "0";
    setHistoryAvailability(false);
    elements.terrainEmpty.hidden = false;
  }
}

populateSectorPicker();
attachInteractions();
await loadSnapshot();
render();
