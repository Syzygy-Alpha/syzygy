/* Dependency-free topographic view for the institutional site. */

function createTerrainMap() {
  const canvas = document.getElementById("ecosystem-terrain");
  if (!canvas) return;
  const map = canvas.parentElement;
  const layerButtons = [
    ...document.querySelectorAll("[data-terrain-layer]"),
  ];
  const nodeButtons = [...map.querySelectorAll("[data-terrain-module]")];
  const activeModuleLabel = document.getElementById(
    "terrain-active-module",
  );
  const activeValueLabel = document.getElementById("terrain-active-value");
  const activeDescription = document.getElementById(
    "terrain-active-description",
  );
  const moduleLink = document.getElementById("terrain-module-link");
  const layerSummary = document.getElementById("terrain-layer-summary");
  const dataSource = document.getElementById("terrain-data-source");
  const announcement = document.getElementById("terrain-announcement");
  const accent = themeColor("--lime", "#c9ff45");
  const modules = {
    foundation: {
      title: "Foundation",
      architecture: 1,
      current: true,
      responsibility: "Núcleo compartilhado",
      description:
        "Configuração, identidade, contratos e ciclo de vida comuns ao ecossistema.",
    },
    forge: {
      title: "Forge",
      architecture: 0.7,
      current: true,
      responsibility: "Engenharia e automação",
      description:
        "Projetos, Git, builds, deploy e automação de engenharia local.",
    },
    mycelium: {
      title: "Mycelium",
      architecture: 0.76,
      current: true,
      responsibility: "Malha distribuída",
      description:
        "Identidade de nós e base para descoberta, sincronização e replicação.",
    },
    observatory: {
      title: "Observatory",
      architecture: 0.68,
      current: true,
      responsibility: "Observabilidade",
      description:
        "Saúde, tendências e visibilidade operacional dos módulos conhecidos.",
    },
    nerv: {
      title: "NERV",
      architecture: 0.82,
      current: true,
      responsibility: "Centro operacional",
      description:
        "Superfície local para compreender e conduzir capacidades do ecossistema.",
    },
    tungsten: {
      title: "Tungsten",
      architecture: 0.62,
      current: false,
      responsibility: "Confiança e segurança",
      description:
        "Direção futura para secrets, certificados, criptografia e controle de acesso.",
    },
    coppermind: {
      title: "Coppermind",
      architecture: 0.58,
      current: false,
      responsibility: "Memória permanente",
      description:
        "Direção futura para documentos, código, busca e conhecimento pessoal.",
    },
    magi: {
      title: "MAGI",
      architecture: 0.5,
      current: false,
      responsibility: "Inteligência especializada",
      description:
        "Direção futura para um conselho de raciocínio, criatividade e comunicação.",
    },
    balance: {
      title: "Balance",
      architecture: 0.46,
      current: false,
      responsibility: "Governança",
      description:
        "Direção futura para explorar, restringir e conciliar decisões do sistema.",
    },
    elric: {
      title: "Elric",
      architecture: 0.5,
      current: false,
      responsibility: "Contexto do usuário",
      description:
        "Direção futura para preferências, histórico e personalização integrados.",
    },
    imrryr: {
      title: "Imrryr",
      architecture: 0.4,
      current: false,
      responsibility: "Aplicações próprias",
      description:
        "Direção futura para aplicações e ferramentas experimentais do ecossistema.",
    },
    bastion: {
      title: "Bastion",
      architecture: 0.38,
      current: false,
      responsibility: "Laboratório isolado",
      description:
        "Direção futura para validação de segurança em ambientes autorizados.",
    },
  };
  const relationships = [
    ["elric", "nerv"],
    ["nerv", "foundation"],
    ["foundation", "forge"],
    ["foundation", "mycelium"],
    ["foundation", "observatory"],
    ["mycelium", "tungsten"],
    ["tungsten", "coppermind"],
    ["coppermind", "magi"],
    ["magi", "balance"],
  ];
  const layerCopy = {
    architecture: {
      summary:
        "A altura representa centralidade conceitual; proximidade não implica chamadas diretas entre módulos.",
      source: "DADOS · DOCUMENTAÇÃO OFICIAL",
    },
    state: {
      summary:
        "Picos altos identificam colunas funcionais v0.1; relevos baixos preservam conceitos futuros sem apresentá-los como prontos.",
      source: "DADOS · ESTADO DOCUMENTADO",
    },
    activity: {
      summary:
        "A altura representa commits que tocaram o diretório de cada módulo na janela registrada pelo build.",
      source: "DADOS · SNAPSHOT GIT",
    },
  };
  let field = sizeCanvas(canvas);
  let activeLayer = "architecture";
  let activeModule = "foundation";
  let activitySnapshot = null;
  let resizeFrame = null;

  function positionedModules() {
    return nodeButtons.map((button) => {
      const key = button.dataset.terrainModule;
      return {
        ...modules[key],
        key,
        button,
        x:
          parseFloat(button.style.getPropertyValue("--terrain-x")) / 100 ||
          0.5,
        y:
          parseFloat(button.style.getPropertyValue("--terrain-y")) / 100 ||
          0.5,
      };
    });
  }

  function activityCount(key) {
    const count = activitySnapshot?.modules?.[key];
    return Number.isInteger(count) && count >= 0 ? count : null;
  }

  function terrainWeight(module, maximumActivity) {
    if (activeLayer === "architecture") return module.architecture;
    if (activeLayer === "state") return module.current ? 0.96 : 0.22;
    const count = activityCount(module.key);
    if (count === null || maximumActivity === 0) return 0;
    return count === 0
      ? 0.08
      : 0.2 + (Math.log1p(count) / Math.log1p(maximumActivity)) * 0.8;
  }

  function edgePoint(edge, cell, level) {
    const interpolate = (a, b) => {
      const difference = b - a;
      if (Math.abs(difference) < 0.00001) return 0.5;
      return Math.max(0, Math.min(1, (level - a) / difference));
    };
    if (edge === "top") {
      const t = interpolate(cell.tl, cell.tr);
      return [cell.x + cell.step * t, cell.y];
    }
    if (edge === "right") {
      const t = interpolate(cell.tr, cell.br);
      return [cell.x + cell.step, cell.y + cell.step * t];
    }
    if (edge === "bottom") {
      const t = interpolate(cell.bl, cell.br);
      return [cell.x + cell.step * t, cell.y + cell.step];
    }
    const t = interpolate(cell.tl, cell.bl);
    return [cell.x, cell.y + cell.step * t];
  }

  function drawConnections(context, points) {
    if (activeLayer !== "architecture") return;
    context.save();
    context.setLineDash([4, 8]);
    context.lineWidth = 1;
    context.strokeStyle = "rgba(242,240,233,.18)";
    relationships.forEach(([fromKey, toKey]) => {
      const from = points.find((point) => point.key === fromKey);
      const to = points.find((point) => point.key === toKey);
      if (!from || !to) return;
      context.beginPath();
      context.moveTo(from.x * field.width, from.y * field.height);
      context.lineTo(to.x * field.width, to.y * field.height);
      context.stroke();
    });
    context.restore();
  }

  function drawContours(context, points) {
    if (activeLayer === "activity" && !activitySnapshot?.available) return;
    const step = performanceLite ? 18 : 12;
    const columns = Math.ceil(field.width / step) + 1;
    const rows = Math.ceil(field.height / step) + 1;
    const values = new Float32Array(columns * rows);
    const counts = points.map((point) => activityCount(point.key) ?? 0);
    const maximumActivity = Math.max(0, ...counts);
    let maximumValue = 0;

    for (let row = 0; row < rows; row++) {
      for (let column = 0; column < columns; column++) {
        const x = column * step;
        const y = row * step;
        let value = 0;
        points.forEach((point) => {
          const weight = terrainWeight(point, maximumActivity);
          if (weight === 0) return;
          const sigma =
            Math.min(field.width, field.height) * (0.075 + weight * 0.035);
          const dx = (x - point.x * field.width) / sigma;
          const dy = (y - point.y * field.height) / sigma;
          value += weight * Math.exp(-(dx * dx + dy * dy) * 0.5);
        });
        const variation =
          Math.sin(x * 0.018 + y * 0.006) * 0.012 +
          Math.cos(y * 0.021 - x * 0.004) * 0.01;
        value = Math.max(0, value + variation);
        values[row * columns + column] = value;
        maximumValue = Math.max(maximumValue, value);
      }
    }
    if (maximumValue <= 0.01) return;
    for (let index = 0; index < values.length; index++)
      values[index] /= maximumValue;

    const segments = {
      1: [["left", "top"]],
      2: [["top", "right"]],
      3: [["left", "right"]],
      4: [["right", "bottom"]],
      5: [
        ["left", "top"],
        ["right", "bottom"],
      ],
      6: [["top", "bottom"]],
      7: [["left", "bottom"]],
      8: [["bottom", "left"]],
      9: [["top", "bottom"]],
      10: [
        ["top", "right"],
        ["bottom", "left"],
      ],
      11: [["right", "bottom"]],
      12: [["left", "right"]],
      13: [["top", "right"]],
      14: [["left", "top"]],
    };
    const levels = [0.12, 0.2, 0.29, 0.39, 0.5, 0.62, 0.75, 0.88];
    levels.forEach((level, levelIndex) => {
      context.beginPath();
      for (let row = 0; row < rows - 1; row++) {
        for (let column = 0; column < columns - 1; column++) {
          const cell = {
            x: column * step,
            y: row * step,
            step,
            tl: values[row * columns + column],
            tr: values[row * columns + column + 1],
            br: values[(row + 1) * columns + column + 1],
            bl: values[(row + 1) * columns + column],
          };
          const code =
            (cell.tl >= level ? 1 : 0) |
            (cell.tr >= level ? 2 : 0) |
            (cell.br >= level ? 4 : 0) |
            (cell.bl >= level ? 8 : 0);
          (segments[code] || []).forEach(([fromEdge, toEdge]) => {
            const from = edgePoint(fromEdge, cell, level);
            const to = edgePoint(toEdge, cell, level);
            context.moveTo(from[0], from[1]);
            context.lineTo(to[0], to[1]);
          });
        }
      }
      context.lineWidth = levelIndex % 3 === 0 ? 1.35 : 0.75;
      context.strokeStyle = `rgba(242,240,233,${0.16 + levelIndex * 0.045})`;
      context.stroke();
    });
  }

  function drawActivePoint(context, points) {
    const point = points.find((candidate) => candidate.key === activeModule);
    if (!point) return;
    const x = point.x * field.width;
    const y = point.y * field.height;
    const glow = context.createRadialGradient(x, y, 0, x, y, 72);
    glow.addColorStop(0, "rgba(201,255,69,.2)");
    glow.addColorStop(1, "rgba(201,255,69,0)");
    context.fillStyle = glow;
    context.fillRect(x - 72, y - 72, 144, 144);
    context.save();
    context.strokeStyle = accent;
    context.lineWidth = 1.5;
    context.beginPath();
    context.arc(x, y, 16, 0, Math.PI * 2);
    context.stroke();
    context.restore();
  }

  function draw() {
    const { context } = field;
    const points = positionedModules();
    context.clearRect(0, 0, field.width, field.height);
    drawConnections(context, points);
    drawContours(context, points);
    drawActivePoint(context, points);
  }

  function moduleValue(module) {
    if (activeLayer === "architecture") return module.responsibility;
    if (activeLayer === "state")
      return module.current ? "Funcional · v0.1" : "Conceito · futuro";
    const count = activityCount(activeModule);
    if (count === null) return "Snapshot Git indisponível";
    return `${count} ${count === 1 ? "commit" : "commits"} · ${activitySnapshot.windowDays} dias`;
  }

  function updateReadout() {
    const module = modules[activeModule];
    if (!module) return;
    activeModuleLabel.textContent = module.title;
    activeValueLabel.textContent = moduleValue(module);
    activeDescription.textContent = module.description;
    moduleLink.href = `./modules/${activeModule}.html`;
    nodeButtons.forEach((button) =>
      {
        const selected = button.dataset.terrainModule === activeModule;
        button.classList.toggle("active", selected);
        button.setAttribute("aria-pressed", String(selected));
      },
    );
  }

  function updateLayerCopy() {
    const copy = layerCopy[activeLayer];
    layerSummary.textContent = copy.summary;
    if (activeLayer !== "activity") {
      dataSource.textContent = copy.source;
      return;
    }
    if (!activitySnapshot?.available) {
      dataSource.textContent = "DADOS · SNAPSHOT GIT INDISPONÍVEL";
      return;
    }
    const revisionDate = activitySnapshot.revisionAt?.slice(0, 10);
    dataSource.textContent = `GIT · ${activitySnapshot.revision}${revisionDate ? ` · ${revisionDate}` : ""} · ${activitySnapshot.windowDays} DIAS`;
  }

  function selectModule(key) {
    if (!modules[key]) return;
    activeModule = key;
    updateReadout();
    announcement.textContent = `${modules[key].title}: ${moduleValue(modules[key])}.`;
    draw();
  }

  function selectLayer(layer) {
    if (!layerCopy[layer]) return;
    activeLayer = layer;
    map.dataset.terrainLayer = layer;
    layerButtons.forEach((button) => {
      const selected = button.dataset.terrainLayer === layer;
      button.classList.toggle("active", selected);
      button.setAttribute("aria-pressed", String(selected));
    });
    updateLayerCopy();
    updateReadout();
    announcement.textContent = `Camada ${layerButtons.find((button) => button.dataset.terrainLayer === layer)?.textContent.trim()}. ${layerCopy[layer].summary}`;
    draw();
  }

  nodeButtons.forEach((button) => {
    const select = () => selectModule(button.dataset.terrainModule);
    button.addEventListener("click", select);
    button.addEventListener("focus", select);
    button.addEventListener("pointerenter", select);
  });
  layerButtons.forEach((button) =>
    button.addEventListener("click", () =>
      selectLayer(button.dataset.terrainLayer),
    ),
  );

  window.addEventListener("resize", () => {
    if (resizeFrame !== null) cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(() => {
      field = sizeCanvas(canvas);
      draw();
      resizeFrame = null;
    });
  });

  fetch("./ecosystem-snapshot.json", { cache: "no-store" })
    .then((response) => {
      if (!response.ok) throw new Error("Terrain snapshot is unavailable");
      return response.json();
    })
    .then((snapshot) => {
      activitySnapshot = snapshot?.available ? snapshot : { available: false };
      if (activeLayer === "activity") selectLayer("activity");
    })
    .catch(() => {
      activitySnapshot = { available: false };
      if (activeLayer === "activity") selectLayer("activity");
    });

  updateReadout();
  updateLayerCopy();
  draw();
}

createTerrainMap();
