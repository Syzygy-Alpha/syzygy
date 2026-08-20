const state = {
  loading: false,
};

function pillTone(value) {
  const normalized = String(value || "").toLowerCase();
  if (["ok", "online", "reachable", "running"].includes(normalized)) {
    return "ok";
  }
  if (["warning", "degraded", "starting", "known"].includes(normalized)) {
    return "warn";
  }
  if (["error", "offline", "failed", "stopped", "unreachable"].includes(normalized)) {
    return "danger";
  }
  return "neutral";
}

function formatTimestamp(value) {
  if (!value) {
    return "--";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = value;
  }
}

async function callAction(name, action) {
  await fetch(`/api/surfaces/${name}/${action}`, { method: "POST" });
  await loadDashboard();
}

function renderSurface(surface) {
  const runtimeState = surface.runtime.running ? "running" : "stopped";
  const probeState = surface.probe.reachable
    ? surface.probe.service_status || "reachable"
    : "unreachable";
  const registryState = surface.foundation_status || "unregistered";

  return `
    <article class="surface-card">
      <div class="surface-header">
        <div>
          <h2 class="surface-title">${surface.label}</h2>
          <p class="surface-group">${surface.group.toUpperCase()}</p>
        </div>
        <div class="accent-bar" style="background:${surface.accent}"></div>
      </div>
      <p class="surface-description">${surface.description}</p>
      <div class="status-pills">
        <span class="pill ${pillTone(runtimeState)}">${runtimeState}</span>
        <span class="pill ${pillTone(probeState)}">${probeState}</span>
        <span class="pill ${pillTone(registryState)}">${registryState}</span>
      </div>
      <div class="surface-meta">
        <div>cwd: <strong>${surface.cwd}</strong></div>
        <div>pid: <strong>${surface.runtime.pid ?? "--"}</strong></div>
        <div>started: <strong>${formatTimestamp(surface.runtime.started_at)}</strong></div>
        <div>foundation health: <strong>${surface.foundation_health ?? "--"}</strong></div>
      </div>
      <div class="surface-actions">
        <button class="action-button" type="button" ${surface.launch_enabled ? "" : "disabled"} onclick="callAction('${surface.name}', 'start')">Launch</button>
        <button class="action-button danger" type="button" ${surface.launch_enabled ? "" : "disabled"} onclick="callAction('${surface.name}', 'stop')">Stop</button>
      </div>
      <div class="surface-links">
        <a class="link-button" href="${surface.links.root_url}" target="_blank" rel="noreferrer">Open</a>
        <a class="link-button" href="${surface.links.health_url}" target="_blank" rel="noreferrer">Health</a>
        <a class="link-button" href="${surface.links.capabilities_url}" target="_blank" rel="noreferrer">Capabilities</a>
      </div>
    </article>
  `;
}

async function loadDashboard() {
  if (state.loading) {
    return;
  }
  state.loading = true;
  try {
    const response = await fetch("/api/dashboard");
    const payload = await response.json();

    setText("summary-known", String(payload.summary.known_surfaces));
    setText("summary-running", String(payload.summary.running_surfaces));
    setText("summary-reachable", String(payload.summary.reachable_surfaces));
    setText(
      "summary-registry",
      payload.foundation_registry.enabled
        ? payload.foundation_registry.reachable
          ? `SYNC ${payload.foundation_registry.module_count}`
          : "ERROR"
        : "LOCAL"
    );
    setText(
      "registry-mode",
      payload.foundation_registry.enabled ? "FOUNDATION REGISTRY" : "LOCAL CATALOG"
    );
    setText("last-updated", formatTimestamp(payload.generated_at));

    const grid = document.getElementById("surface-grid");
    if (grid) {
      grid.innerHTML = payload.surfaces.map(renderSurface).join("");
    }
  } finally {
    state.loading = false;
  }
}

document.getElementById("refresh-button")?.addEventListener("click", () => {
  void loadDashboard();
});

void loadDashboard();
window.setInterval(() => {
  void loadDashboard();
}, 5000);
