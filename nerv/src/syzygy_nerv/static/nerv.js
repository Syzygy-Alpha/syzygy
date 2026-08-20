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

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function callAction(name, action) {
  await fetch(`/api/surfaces/${name}/${action}`, { method: "POST" });
  await loadDashboard();
}

function setConsole(surface, label, payload) {
  setText("action-meta-surface", `${surface} :: ${label}`);
  setText("action-meta-time", formatTimestamp(payload.received_at));
  const output = document.getElementById("action-output");
  if (!output) {
    return;
  }
  output.textContent = JSON.stringify(payload, null, 2);
}

async function runQuickAction(surfaceName, actionName, label) {
  const response = await fetch(`/api/surfaces/${surfaceName}/actions/${actionName}/run`, {
    method: "POST",
  });
  const payload = await response.json();
  setConsole(surfaceName.toUpperCase(), label, payload);
}

function forgeQuery(project, command) {
  return new URLSearchParams({ project, command });
}

async function planForgeCommand(project, command) {
  const response = await fetch(`/api/forge/commands/plan?${forgeQuery(project, command)}`);
  const payload = await response.json();
  setConsole(`FORGE :: ${project}`, `Plan ${command}`, payload);
}

async function runForgeCommand(project, command) {
  const planResponse = await fetch(`/api/forge/commands/plan?${forgeQuery(project, command)}`);
  const plan = await planResponse.json();
  setConsole(`FORGE :: ${project}`, `Plan ${command}`, plan);
  if (!planResponse.ok || !plan.allowed) {
    return;
  }
  const approved = window.confirm(
    `Run allowed Forge command '${command}' for project '${project}'?\n\n${plan.command}`
  );
  if (!approved) {
    return;
  }
  const query = forgeQuery(project, command);
  query.set("confirm", "true");
  const response = await fetch(`/api/forge/commands/run?${query}`, { method: "POST" });
  const payload = await response.json();
  setConsole(`FORGE :: ${project}`, `Run ${command}`, payload);
  await loadForgeWorkbench();
}

function renderProjectCommand(project, command) {
  const projectName = escapeHtml(project.name);
  const commandName = escapeHtml(command.name);
  const commandValue = escapeHtml(command.command);
  return `
    <div class="project-command">
      <code>${commandName}: ${commandValue}</code>
      <button
        class="project-command-button"
        type="button"
        data-project="${projectName}"
        data-command="${commandName}"
        onclick="planForgeCommand(this.dataset.project, this.dataset.command)"
      >PLAN</button>
      <button
        class="project-command-button run"
        type="button"
        data-project="${projectName}"
        data-command="${commandName}"
        onclick="runForgeCommand(this.dataset.project, this.dataset.command)"
      >RUN</button>
    </div>
  `;
}

function renderForgeProject(projectSurface) {
  const project = projectSurface.project;
  const commandList = projectSurface.error
    ? `<p class="project-message">${escapeHtml(projectSurface.error)}</p>`
    : projectSurface.commands.length === 0
      ? '<p class="project-message">No declared commands.</p>'
      : `<div class="project-command-list">${projectSurface.commands
          .map((command) => renderProjectCommand(project, command))
          .join("")}</div>`;
  return `
    <article class="project-card">
      <h3>${escapeHtml(project.name)}</h3>
      <p class="project-path">${escapeHtml(project.path)}</p>
      ${commandList}
    </article>
  `;
}

async function loadForgeWorkbench() {
  const grid = document.getElementById("forge-project-grid");
  const response = await fetch("/api/forge/projects");
  const payload = await response.json();
  setText("forge-workbench-state", payload.reachable ? "FORGE LINKED" : "FORGE OFFLINE");
  setText("forge-project-count", `${payload.projects.length} PROJECTS`);
  if (!grid) {
    return;
  }
  if (!payload.reachable) {
    grid.innerHTML = `<p class="project-message">${escapeHtml(payload.error || "Forge is unreachable.")}</p>`;
    return;
  }
  grid.innerHTML = payload.projects.length
    ? payload.projects.map(renderForgeProject).join("")
    : '<p class="project-message">No projects are registered in Forge.</p>';
}

function renderQuickActions(surface) {
  if (!surface.actions || surface.actions.length === 0) {
    return "";
  }
  const items = surface.actions
    .map(
      (action) => `
        <button
          class="quick-action-button"
          type="button"
          onclick="runQuickAction('${surface.name}', '${action.name}', '${action.label}')"
        >
          <strong>${action.label}</strong>
          <span>${action.description}</span>
        </button>
      `
    )
    .join("");
  return `
    <div class="surface-quick-actions">
      ${items}
    </div>
  `;
}

function renderSurface(surface) {
  const runtimeState = surface.runtime.running ? "running" : "stopped";
  const probeState = surface.probe.reachable
    ? surface.probe.service_status || "reachable"
    : "unreachable";
  const registryState = surface.foundation_status || "unregistered";
  const launchDisabled = surface.launch_enabled ? "" : "disabled";

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
        <button
          class="action-button"
          type="button"
          ${launchDisabled}
          onclick="callAction('${surface.name}', 'start')"
        >Launch</button>
        <button
          class="action-button danger"
          type="button"
          ${launchDisabled}
          onclick="callAction('${surface.name}', 'stop')"
        >Stop</button>
      </div>
      ${renderQuickActions(surface)}
      <div class="surface-links">
        <a
          class="link-button"
          href="${surface.links.root_url}"
          target="_blank"
          rel="noreferrer"
        >Open</a>
        <a
          class="link-button"
          href="${surface.links.health_url}"
          target="_blank"
          rel="noreferrer"
        >Health</a>
        <a
          class="link-button"
          href="${surface.links.capabilities_url}"
          target="_blank"
          rel="noreferrer"
        >Capabilities</a>
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
    await loadForgeWorkbench();
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
