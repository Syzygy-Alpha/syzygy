/* Static isometric map for the institutional home page. */

const terrainSectors = [
  { id: "foundation", label: "Foundation", shortLabel: "FOUND", x: 0.46, y: 0.43, status: "functional" },
  { id: "forge", label: "Forge", shortLabel: "FORGE", x: 0.23, y: 0.51, status: "functional" },
  { id: "mycelium", label: "Mycelium", shortLabel: "MYCEL", x: 0.3, y: 0.28, status: "functional" },
  { id: "observatory", label: "Observatory", shortLabel: "OBS", x: 0.67, y: 0.45, status: "functional" },
  { id: "nerv", label: "NERV", shortLabel: "NERV", x: 0.55, y: 0.22, status: "functional" },
  { id: "tungsten", label: "Tungsten", shortLabel: "TUNG", x: 0.78, y: 0.27, status: "future" },
  { id: "coppermind", label: "Coppermind", shortLabel: "COPPER", x: 0.8, y: 0.57, status: "future" },
  { id: "magi", label: "MAGI", shortLabel: "MAGI", x: 0.72, y: 0.75, status: "future" },
  { id: "balance", label: "Balance", shortLabel: "BAL", x: 0.53, y: 0.84, status: "future" },
  { id: "elric", label: "Elric", shortLabel: "ELRIC", x: 0.37, y: 0.74, status: "future" },
  { id: "imrryr", label: "Imrryr", shortLabel: "IMR", x: 0.2, y: 0.78, status: "future" },
  { id: "bastion", label: "Bastion", shortLabel: "BAS", x: 0.1, y: 0.36, status: "future" },
];

function createTerrainMap() {
  const canvas = document.getElementById("ecosystem-topography");
  if (!canvas) return;

  const terrainValues = new Map(
    terrainSectors.map((sector) => [
      sector.id,
      sector.status === "functional" ? 1 : 0.34,
    ]),
  );

  function resizeCanvas() {
    const bounds = canvas.getBoundingClientRect();
    const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
    canvas.width = Math.max(1, Math.round(bounds.width * ratio));
    canvas.height = Math.max(1, Math.round(bounds.height * ratio));
    const context = canvas.getContext("2d");
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    return { context, width: bounds.width, height: bounds.height };
  }

  function projectPoint(point, elevation, width, height) {
    const rotation = -0.18;
    const cosine = Math.cos(rotation);
    const sine = Math.sin(rotation);
    const rotatedX = point.x * cosine - point.y * sine;
    const rotatedY = point.x * sine + point.y * cosine;
    const scale = Math.min(width * 0.35, height * 0.47);
    return {
      x: width / 2 + (rotatedX - rotatedY) * scale,
      y:
        height * 0.57 +
        (rotatedX + rotatedY) * scale * 0.48 -
        elevation * scale * 0.82,
      depth: rotatedX + rotatedY,
    };
  }

  function terrainHeight(x, y) {
    let result = 0;
    for (const sector of terrainSectors) {
      const sectorX = sector.x * 2 - 1;
      const sectorY = sector.y * 2 - 1;
      const distanceX = x - sectorX;
      const distanceY = y - sectorY;
      const influence = Math.exp(
        -(distanceX * distanceX + distanceY * distanceY) * 3.6,
      );
      result += terrainValues.get(sector.id) * influence;
    }
    return Math.min(1.25, result);
  }

  function polygon(context, points, fill, stroke) {
    context.beginPath();
    context.moveTo(points[0].x, points[0].y);
    for (const point of points.slice(1)) context.lineTo(point.x, point.y);
    context.closePath();
    if (fill) {
      context.fillStyle = fill;
      context.fill();
    }
    if (stroke) {
      context.strokeStyle = stroke;
      context.stroke();
    }
  }

  function colorForHeight(value, alpha = 1) {
    return `rgba(201,255,69,${0.11 + value * 0.45 * alpha})`;
  }

  function drawGrid(context, width, height) {
    context.save();
    context.strokeStyle = "rgba(242,240,233,.055)";
    context.lineWidth = 1;
    for (let x = 0; x <= width; x += 42) {
      context.beginPath();
      context.moveTo(x, 0);
      context.lineTo(x, height);
      context.stroke();
    }
    for (let y = 0; y <= height; y += 42) {
      context.beginPath();
      context.moveTo(0, y);
      context.lineTo(width, y);
      context.stroke();
    }
    context.restore();
  }

  function draw() {
    const { context, width, height } = resizeCanvas();
    context.clearRect(0, 0, width, height);
    drawGrid(context, width, height);

    const detail = width < 520 ? 11 : 16;
    const step = 2 / detail;
    const cells = [];
    for (let row = 0; row < detail; row += 1) {
      for (let column = 0; column < detail; column += 1) {
        const x = -1 + column * step;
        const y = -1 + row * step;
        const vertices = [
          { x, y },
          { x: x + step, y },
          { x: x + step, y: y + step },
          { x, y: y + step },
        ];
        const heights = vertices.map((vertex) =>
          terrainHeight(vertex.x, vertex.y),
        );
        const center = projectPoint(
          { x: x + step / 2, y: y + step / 2 },
          Math.max(...heights),
          width,
          height,
        );
        cells.push({ vertices, heights, depth: center.depth });
      }
    }

    cells.sort((left, right) => left.depth - right.depth);
    context.lineWidth = 0.65;
    for (const cell of cells) {
      const top = cell.vertices.map((vertex, index) =>
        projectPoint(vertex, cell.heights[index], width, height),
      );
      const ground = cell.vertices.map((vertex) =>
        projectPoint(vertex, 0, width, height),
      );
      const average =
        cell.heights.reduce((sum, value) => sum + value, 0) /
        cell.heights.length;
      polygon(context, top, colorForHeight(average), "rgba(242,240,233,.1)");
      polygon(
        context,
        [top[2], top[3], ground[3], ground[2]],
        colorForHeight(average, 0.38),
        "rgba(242,240,233,.05)",
      );
      polygon(
        context,
        [top[1], top[2], ground[2], ground[1]],
        colorForHeight(average, 0.23),
        "rgba(242,240,233,.04)",
      );
    }

    const plottedSectors = terrainSectors
      .map((sector) => {
        const point = projectPoint(
          { x: sector.x * 2 - 1, y: sector.y * 2 - 1 },
          terrainHeight(sector.x * 2 - 1, sector.y * 2 - 1) + 0.035,
          width,
          height,
        );
        return { sector, point };
      })
      .sort((left, right) => left.point.depth - right.point.depth);

    for (const { sector, point } of plottedSectors) {
      const functional = sector.status === "functional";
      context.save();
      context.translate(point.x, point.y);
      context.rotate(Math.PI / 4);
      context.fillStyle = functional ? "#ccff45" : "#9d42d1";
      context.fillRect(-4, -4, 8, 8);
      context.restore();

      const showLabel = width > 560 || functional;
      if (showLabel) {
        context.fillStyle = functional
          ? "rgba(242,240,233,.86)"
          : "rgba(242,240,233,.6)";
        context.font = `${functional ? "700" : "500"} ${width < 520 ? "8" : "10"}px ui-monospace, SFMono-Regular, Consolas, monospace`;
        context.textAlign = "center";
        context.fillText(sector.shortLabel, point.x, point.y - 12);
      }
    }

    context.fillStyle = "rgba(242,240,233,.48)";
    context.font = "10px ui-monospace, SFMono-Regular, Consolas, monospace";
    context.textAlign = "left";
    context.fillText("STATE / DOCUMENTED", 18, 24);
  }

  let resizeFrame;
  window.addEventListener("resize", () => {
    cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(draw);
  });
  draw();
}

createTerrainMap();
