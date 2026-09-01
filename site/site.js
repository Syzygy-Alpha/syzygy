const requestedTheme = new URLSearchParams(location.search).get("theme");
if (requestedTheme === "clean")
  document.documentElement.classList.add("theme-clean");
if (requestedTheme === "orbital")
  document.documentElement.classList.add("theme-orbital");
const requestedQuality = new URLSearchParams(location.search).get("quality");
const deviceMemory = Number(navigator.deviceMemory) || Infinity;
const hardwareConcurrency = Number(navigator.hardwareConcurrency) || Infinity;
const constrainedHardware = deviceMemory <= 4 || hardwareConcurrency <= 4;
const performanceLite =
  requestedQuality === "low" ||
  (requestedQuality !== "high" && constrainedHardware);
if (performanceLite)
  document.documentElement.classList.add("performance-lite");
const reducedMotion = window.matchMedia(
  "(prefers-reduced-motion: reduce)",
).matches;
const animationFrameInterval = performanceLite ? 1000 / 30 : 0;

function animateWhenVisible(element, draw) {
  let frameId = null;
  let visible = false;
  let lastDraw = 0;

  function stop() {
    if (frameId !== null) cancelAnimationFrame(frameId);
    frameId = null;
  }

  function frame(timestamp) {
    if (!visible || document.hidden || reducedMotion) {
      stop();
      return;
    }
    if (
      animationFrameInterval === 0 ||
      timestamp - lastDraw >= animationFrameInterval - 1
    ) {
      draw(timestamp);
      lastDraw = timestamp;
    }
    frameId = requestAnimationFrame(frame);
  }

  function sync() {
    if (visible && !document.hidden && !reducedMotion && frameId === null) {
      frameId = requestAnimationFrame(frame);
    } else if ((!visible || document.hidden) && frameId !== null) {
      stop();
    }
  }

  draw();
  if (reducedMotion || !("IntersectionObserver" in window)) {
    if (!reducedMotion) {
      visible = true;
      sync();
    }
    return;
  }

  const observer = new IntersectionObserver(
    ([entry]) => {
      visible = entry.isIntersecting;
      sync();
    },
    { rootMargin: "160px 0px" },
  );
  observer.observe(element);
  document.addEventListener("visibilitychange", sync);
}

function themeColor(name, fallback, element = document.documentElement) {
  return getComputedStyle(element).getPropertyValue(name).trim() || fallback;
}

function sizeCanvas(canvas) {
  const rect = canvas.getBoundingClientRect();
  const scale = Math.min(
    window.devicePixelRatio || 1,
    performanceLite ? 1 : 1.5,
  );
  canvas.width = Math.round(rect.width * scale);
  canvas.height = Math.round(rect.height * scale);
  const context = canvas.getContext("2d");
  context.setTransform(scale, 0, 0, scale, 0, 0);
  return { context, width: rect.width, height: rect.height };
}

function createHeroField() {
  const canvas = document.getElementById("hero-particles");
  if (!canvas) return;
  const hero = canvas.closest(".hero,.module-detail-hero");
  const particleBase = themeColor("--hero-particle-base", "rgba(23,25,20,.25)");
  const particleActive = themeColor(
    "--hero-particle-active",
    "rgba(55,94,50,.86)",
  );
  const particleLinkRgb = themeColor("--hero-particle-link-rgb", "72,105,55");
  let field = sizeCanvas(canvas);
  let pointer = { x: field.width / 2, y: field.height / 2, active: false };
  let dots = [];

  function reset() {
    field = sizeCanvas(canvas);
    const idealCount = Math.min(140, Math.floor(field.width / 10));
    const count = performanceLite
      ? Math.max(36, Math.floor(idealCount * 0.5))
      : idealCount;
    dots = Array.from({ length: count }, () => {
      const x = Math.random() * field.width,
        y = Math.random() * field.height;
      return {
        x,
        y,
        homeX: x,
        homeY: y,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        radius: Math.random() * 1.7 + 0.7,
        phase: Math.random() * Math.PI * 2,
        orbitRadius: 32 + Math.random() * 105,
        orbitDirection: Math.random() > 0.5 ? 1 : -1,
      };
    });
  }

  function setPointer(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left,
      y = event.clientY - rect.top;
    pointer = {
      x,
      y,
      active: x >= 0 && x <= rect.width && y >= 0 && y <= rect.height,
    };
  }
  hero.addEventListener("pointerenter", setPointer);
  hero.addEventListener("pointermove", setPointer);
  hero.addEventListener("pointerleave", () => {
    pointer.active = false;
  });
  hero.addEventListener("pointercancel", () => {
    pointer.active = false;
  });
  hero.addEventListener("pointerup", (event) => {
    if (event.pointerType !== "mouse") pointer.active = false;
  });

  function draw() {
    const { context, width, height } = field;
    const time = performance.now() * 0.001;
    context.clearRect(0, 0, width, height);
    for (const dot of dots) {
      const dx = pointer.x - dot.x,
        dy = pointer.y - dot.y,
        distance = Math.hypot(dx, dy) || 1;
      const orbiting = pointer.active && distance < 380;
      if (orbiting) {
        const influence = 1 - distance / 380,
          unitX = dx / distance,
          unitY = dy / distance;
        const radialError = distance - dot.orbitRadius;
        dot.vx += unitX * radialError * 0.0009 * influence;
        dot.vy += unitY * radialError * 0.0009 * influence;
        const orbit = (0.008 + influence * 0.022) * dot.orbitDirection;
        dot.vx += -unitY * orbit;
        dot.vy += unitX * orbit;
      } else {
        const driftX = Math.cos(time * 0.38 + dot.phase) * 11,
          driftY = Math.sin(time * 0.31 + dot.phase) * 9;
        dot.vx += (dot.homeX + driftX - dot.x) * 0.0055;
        dot.vy += (dot.homeY + driftY - dot.y) * 0.0055;
      }
      const friction = orbiting ? 0.972 : 0.92;
      dot.vx *= friction;
      dot.vy *= friction;
      const speed = Math.hypot(dot.vx, dot.vy),
        limit = orbiting ? 2.35 : 1.25;
      if (speed > limit) {
        dot.vx = (dot.vx / speed) * limit;
        dot.vy = (dot.vy / speed) * limit;
      }
      dot.x += dot.vx;
      dot.y += dot.vy;
      if (dot.x < 0) {
        dot.x = 0;
        dot.vx = Math.abs(dot.vx) * 0.35;
      } else if (dot.x > width) {
        dot.x = width;
        dot.vx = -Math.abs(dot.vx) * 0.35;
      }
      if (dot.y < 0) {
        dot.y = 0;
        dot.vy = Math.abs(dot.vy) * 0.35;
      } else if (dot.y > height) {
        dot.y = height;
        dot.vy = -Math.abs(dot.vy) * 0.35;
      }
      context.beginPath();
      context.arc(dot.x, dot.y, dot.radius, 0, Math.PI * 2);
      context.fillStyle =
        pointer.active && distance < 240 ? particleActive : particleBase;
      context.fill();
      if (pointer.active && distance < 155) {
        context.beginPath();
        context.moveTo(dot.x, dot.y);
        context.lineTo(pointer.x, pointer.y);
        context.strokeStyle = `rgba(${particleLinkRgb},${(1 - distance / 155) * 0.24})`;
        context.stroke();
      }
    }
  }
  reset();
  animateWhenVisible(canvas, draw);
  window.addEventListener("resize", reset);
}

function colorVector(value, fallback) {
  const hex = value.match(/^#([\da-f]{3}|[\da-f]{6})$/i);
  if (hex) {
    const normalized =
      hex[1].length === 3
        ? hex[1]
            .split("")
            .map((part) => part + part)
            .join("")
        : hex[1];
    return [0, 2, 4].map(
      (index) => Number.parseInt(normalized.slice(index, index + 2), 16) / 255,
    );
  }
  const rgb = value.match(/rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)/i);
  return rgb
    ? [Number(rgb[1]) / 255, Number(rgb[2]) / 255, Number(rgb[3]) / 255]
    : fallback;
}

function createMedusaeFallback(canvas) {
  const context = canvas.getContext("2d");
  if (!context) return;
  let field = sizeCanvas(canvas);
  const dots = Array.from({ length: performanceLite ? 42 : 84 }, () => ({
    x: Math.random(),
    y: Math.random(),
    phase: Math.random() * Math.PI * 2,
  }));

  function draw(time = performance.now()) {
    context.clearRect(0, 0, field.width, field.height);
    dots.forEach((dot, index) => {
      const x =
        (dot.x + Math.cos(time * 0.00025 + dot.phase) * 0.018) * field.width;
      const y =
        (dot.y + Math.sin(time * 0.00021 + dot.phase) * 0.018) * field.height;
      context.beginPath();
      context.arc(x, y, index % 11 ? 1.1 : 2.3, 0, Math.PI * 2);
      context.fillStyle = index % 11
        ? "rgba(24,26,24,.2)"
        : "rgba(118,144,112,.65)";
      context.fill();
    });
  }

  animateWhenVisible(canvas, draw);
  window.addEventListener("resize", () => {
    field = sizeCanvas(canvas);
  });
}

function createMedusaeField() {
  const canvas = document.getElementById("medusae-particles");
  if (!canvas) return;
  const surface =
    canvas.closest(".manifest, .module-overview") || canvas.parentElement;
  const gl = canvas.getContext("webgl", {
    alpha: true,
    antialias: false,
    powerPreference: "low-power",
  });
  if (!gl) {
    createMedusaeFallback(canvas);
    return;
  }

  const vertexSource = `
    precision mediump float;
    attribute vec2 aOffset;
    attribute float aRandom;
    uniform float uTime;
    uniform vec2 uMouse;
    uniform vec2 uResolution;
    uniform float uRadiusBase;
    uniform float uRadiusAmplitude;
    uniform float uShapeAmplitude;
    uniform float uRimWidth;
    uniform float uScaleX;
    uniform float uScaleY;
    uniform float uBaseSize;
    uniform float uActiveSize;
    varying float vHalo;
    varying vec2 vPosition;
    float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
    float noise(vec2 p) {
      vec2 i = floor(p), f = fract(p);
      f = f * f * (3.0 - 2.0 * f);
      return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
    }
    void main() {
      vec2 pos = aOffset;
      float drift = uTime * .15;
      pos.x += (sin(drift + pos.y * .5) + sin(drift * .5 + pos.y * 2.0)) * .25;
      pos.y += (cos(drift + pos.x * .5) + cos(drift * .5 + pos.x * 2.0)) * .25;
      vec2 relative = pos - uMouse;
      vec2 scale = max(vec2(uScaleX, uScaleY), vec2(.0001));
      float distanceToMouse = length(relative / scale);
      vec2 direction = normalize(relative + vec2(.0001, 0.0));
      float shape = noise(direction * 2.0 + vec2(0.0, uTime * .1));
      float breath = sin(uTime * .8);
      float baseRadius = uRadiusBase + breath * uRadiusAmplitude;
      float currentRadius = baseRadius + shape * uShapeAmplitude;
      float rim = smoothstep(uRimWidth, 0.0, abs(distanceToMouse - currentRadius));
      pos += direction * ((breath * .5 + .5) * .5) * rim;
      float outer = smoothstep(baseRadius + .4, baseRadius + 2.2, distanceToMouse);
      pos += direction * sin(uTime * 2.6 + pos.x * .6 + pos.y * .6) * .76 * outer;
      float oscillation = .5 + .5 * sin(uTime * .6 + aRandom * 6.283185);
      float size = mix(uBaseSize, uActiveSize, rim) * (.92 + oscillation * .12);
      float aspect = uResolution.x / max(uResolution.y, 1.0);
      vec2 bounds = aspect < 1.818 ? vec2(11.0 * aspect, 11.0) : vec2(20.0, 20.0 / aspect);
      gl_PointSize = size;
      gl_Position = vec4(pos / bounds, 0.0, 1.0);
      vHalo = rim;
      vPosition = pos;
    }
  `;
  const fragmentSource = `
    precision mediump float;
    uniform float uTime;
    uniform vec3 uColorBase;
    uniform vec3 uColorOne;
    uniform vec3 uColorTwo;
    uniform vec3 uColorThree;
    varying float vHalo;
    varying vec2 vPosition;
    void main() {
      float distanceFromCenter = length(gl_PointCoord - vec2(.5)) * 2.0;
      float alpha = 1.0 - smoothstep(.72, 1.0, distanceFromCenter);
      if (alpha < .01) discard;
      float wave = sin(vPosition.x * .8 + uTime * 1.2) * .5 + .5;
      float secondary = sin(vPosition.y * .8 + uTime * .96 + wave) * .5 + .5;
      vec3 active = mix(uColorOne, uColorTwo, wave);
      active = mix(active, uColorThree, secondary);
      vec3 color = mix(uColorBase, active, smoothstep(.1, .8, vHalo));
      gl_FragColor = vec4(color, alpha * mix(.4, .95, vHalo));
    }
  `;
  const compile = (type, source) => {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    return gl.getShaderParameter(shader, gl.COMPILE_STATUS) ? shader : null;
  };
  const vertexShader = compile(gl.VERTEX_SHADER, vertexSource);
  const fragmentShader = compile(gl.FRAGMENT_SHADER, fragmentSource);
  if (!vertexShader || !fragmentShader) return;

  const program = gl.createProgram();
  gl.attachShader(program, vertexShader);
  gl.attachShader(program, fragmentShader);
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) return;

  const columns = performanceLite ? 70 : 100;
  const rows = performanceLite ? 40 : 55;
  const count = columns * rows;
  const offsets = new Float32Array(count * 2);
  const randoms = new Float32Array(count);
  let index = 0;
  for (let y = 0; y < rows; y += 1) {
    for (let x = 0; x < columns; x += 1) {
      offsets[index * 2] = (x / (columns - 1) - 0.5) * 40;
      offsets[index * 2 + 1] = (y / (rows - 1) - 0.5) * 22;
      randoms[index] = Math.random();
      index += 1;
    }
  }

  const buffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  gl.bufferData(gl.ARRAY_BUFFER, offsets, gl.STATIC_DRAW);
  const randomBuffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, randomBuffer);
  gl.bufferData(gl.ARRAY_BUFFER, randoms, gl.STATIC_DRAW);
  gl.useProgram(program);

  const attributeOffset = gl.getAttribLocation(program, "aOffset");
  const attributeRandom = gl.getAttribLocation(program, "aRandom");
  const uniforms = Object.fromEntries(
    [
      "uTime",
      "uMouse",
      "uResolution",
      "uRadiusBase",
      "uRadiusAmplitude",
      "uShapeAmplitude",
      "uRimWidth",
      "uScaleX",
      "uScaleY",
      "uBaseSize",
      "uActiveSize",
      "uColorBase",
      "uColorOne",
      "uColorTwo",
      "uColorThree",
    ].map((name) => [name, gl.getUniformLocation(program, name)]),
  );
  const moduleAccentValue = themeColor("--module-accent", "", surface);
  const hasModulePalette = Boolean(moduleAccentValue);
  const baseColor = hasModulePalette
    ? colorVector(themeColor("--ink", "#171914", surface), [0.1, 0.1, 0.1])
    : colorVector(themeColor("--hero-particle-base", "rgba(24,26,24,.25)"), [0.1, 0.1, 0.1]);
  const activeColor = hasModulePalette
    ? colorVector(moduleAccentValue, [0.45, 0.6, 0.4])
    : colorVector(themeColor("--hero-particle-active", "rgba(118,144,112,.86)"), [0.45, 0.6, 0.4]);
  const accentColor = hasModulePalette
    ? activeColor.map((channel, colorIndex) =>
        Math.min(1, channel * 0.72 + [0.16, 0.1, 0.18][colorIndex]),
      )
    : colorVector(themeColor("--copper", "#b9684c"), [0.7, 0.3, 0.2]);
  let targetMouse = [0, 0];
  let currentMouse = [0, 0];

  function resize() {
    const rect = canvas.getBoundingClientRect();
    const scale = Math.min(window.devicePixelRatio || 1, performanceLite ? 1 : 1.5);
    canvas.width = Math.round(rect.width * scale);
    canvas.height = Math.round(rect.height * scale);
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.uniform2f(uniforms.uResolution, rect.width, rect.height);
  }

  function setPointer(event) {
    const rect = canvas.getBoundingClientRect();
    targetMouse = [
      ((event.clientX - rect.left) / rect.width - 0.5) * 40,
      (0.5 - (event.clientY - rect.top) / rect.height) * 22,
    ];
  }

  surface.addEventListener("pointerenter", setPointer);
  surface.addEventListener("pointermove", setPointer);
  surface.addEventListener("pointerleave", () => {
    targetMouse = [0, 0];
  });
  resize();
  gl.clearColor(0, 0, 0, 0);
  gl.disable(gl.DEPTH_TEST);
  gl.enable(gl.BLEND);
  gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
  gl.uniform1f(uniforms.uRadiusBase, 3.6);
  gl.uniform1f(uniforms.uRadiusAmplitude, 0.7);
  gl.uniform1f(uniforms.uShapeAmplitude, 1);
  gl.uniform1f(uniforms.uRimWidth, 2);
  gl.uniform1f(uniforms.uScaleX, 1.8);
  gl.uniform1f(uniforms.uScaleY, 1.25);
  gl.uniform1f(uniforms.uBaseSize, performanceLite ? 2.5 : 3.1);
  gl.uniform1f(uniforms.uActiveSize, performanceLite ? 6.8 : 8.6);
  gl.uniform3fv(uniforms.uColorBase, baseColor);
  gl.uniform3fv(uniforms.uColorOne, activeColor);
  gl.uniform3fv(uniforms.uColorTwo, accentColor);
  gl.uniform3fv(uniforms.uColorThree, [0.84, 0.72, 0.24]);

  function draw(time = performance.now()) {
    currentMouse[0] += (targetMouse[0] - currentMouse[0]) * 0.015;
    currentMouse[1] += (targetMouse[1] - currentMouse[1]) * 0.015;
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.useProgram(program);
    gl.uniform1f(uniforms.uTime, reducedMotion ? 0 : time * 0.001);
    gl.uniform2f(uniforms.uMouse, currentMouse[0], currentMouse[1]);
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.enableVertexAttribArray(attributeOffset);
    gl.vertexAttribPointer(attributeOffset, 2, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ARRAY_BUFFER, randomBuffer);
    gl.enableVertexAttribArray(attributeRandom);
    gl.vertexAttribPointer(attributeRandom, 1, gl.FLOAT, false, 0, 0);
    gl.drawArrays(gl.POINTS, 0, count);
  }

  animateWhenVisible(canvas, draw);
  window.addEventListener("resize", resize);
}

function createModuleField() {
  const canvas = document.getElementById("module-particles");
  if (!canvas) return;
  const lab = canvas.parentElement;
  const particleMain = themeColor(
    "--module-particle-main",
    "rgba(37,75,59,.72)",
  );
  const particleRare = themeColor("--module-particle-rare", "#7ea524");
  const buttons = [...lab.querySelectorAll(".module-list [data-symbol]")];
  const title = document.getElementById("active-module");
  const description = document.getElementById("active-module-description");
  let field = sizeCanvas(canvas),
    active = null,
    particles = [],
    lastDrawTime = performance.now();

  function addLine(points, from, to, count) {
    for (let i = 0; i < count; i++) {
      const t = i / Math.max(count - 1, 1);
      points.push({
        x: from[0] + (to[0] - from[0]) * t,
        y: from[1] + (to[1] - from[1]) * t,
      });
    }
  }
  function addEllipse(
    points,
    cx,
    cy,
    rx,
    ry,
    count,
    start = 0,
    end = Math.PI * 2,
  ) {
    for (let i = 0; i < count; i++) {
      const angle = start + ((end - start) * i) / count;
      points.push({
        x: cx + Math.cos(angle) * rx,
        y: cy + Math.sin(angle) * ry,
      });
    }
  }
  function addPolygon(points, vertices, density = 24) {
    for (let i = 0; i < vertices.length; i++)
      addLine(
        points,
        vertices[i],
        vertices[(i + 1) % vertices.length],
        density,
      );
  }
  function addCurve(points, from, control, to, count) {
    for (let i = 0; i < count; i++) {
      const t = i / Math.max(count - 1, 1),
        u = 1 - t;
      points.push({
        x: u * u * from[0] + 2 * u * t * control[0] + t * t * to[0],
        y: u * u * from[1] + 2 * u * t * control[1] + t * t * to[1],
      });
    }
  }

  function symbolPoints(name, count) {
    const stageWidth = field.width * (field.width < 800 ? 1 : 0.6),
      cx = stageWidth / 2,
      cy = field.width < 800 ? 190 : field.height * 0.39,
      size = Math.min(stageWidth, field.height) * 0.28,
      points = [];
    if (name === "foundation") {
      addPolygon(
        points,
        [
          [cx - size, cy - size * 0.48],
          [cx, cy - size],
          [cx + size, cy - size * 0.48],
        ],
        42,
      );
      [-0.62, 0, 0.62].forEach((offset) => {
        addLine(
          points,
          [cx + size * offset, cy - size * 0.42],
          [cx + size * offset, cy + size * 0.58],
          36,
        );
        addLine(
          points,
          [cx + size * (offset - 0.13), cy - size * 0.42],
          [cx + size * (offset + 0.13), cy - size * 0.42],
          12,
        );
      });
      addLine(
        points,
        [cx - size, cy + size * 0.62],
        [cx + size, cy + size * 0.62],
        58,
      );
      addLine(
        points,
        [cx - size * 0.82, cy + size * 0.8],
        [cx + size * 0.82, cy + size * 0.8],
        48,
      );
    } else if (name === "forge") {
      addPolygon(
        points,
        [
          [cx - size * 0.94, cy - size * 0.82],
          [cx + size * 0.58, cy - size * 0.82],
          [cx + size * 0.88, cy - size * 0.46],
          [cx + size * 0.44, cy - size * 0.18],
          [cx - size * 0.94, cy - size * 0.28],
        ],
        34,
      );
      addPolygon(
        points,
        [
          [cx - size * 0.12, cy - size * 0.2],
          [cx + size * 0.22, cy - size * 0.12],
          [cx - size * 0.18, cy + size * 0.94],
          [cx - size * 0.55, cy + size * 0.82],
        ],
        32,
      );
      addLine(
        points,
        [cx - size * 0.88, cy - size * 0.55],
        [cx + size * 0.55, cy - size * 0.52],
        42,
      );
    } else if (name === "mycelium") {
      const meshNodes = [
        [cx - size * 0.68, cy - size * 0.58],
        [cx, cy - size * 0.82],
        [cx + size * 0.72, cy - size * 0.54],
        [cx - size * 0.86, cy],
        [cx - size * 0.08, cy - size * 0.02],
        [cx + size * 0.82, cy + size * 0.05],
        [cx - size * 0.62, cy + size * 0.65],
        [cx + size * 0.12, cy + size * 0.82],
        [cx + size * 0.72, cy + size * 0.58],
      ];
      const meshEdges = [
        [0, 1],
        [0, 3],
        [0, 4],
        [1, 2],
        [1, 4],
        [2, 4],
        [2, 5],
        [3, 4],
        [3, 6],
        [4, 5],
        [4, 6],
        [4, 7],
        [5, 7],
        [5, 8],
        [6, 7],
        [7, 8],
      ];
      meshEdges.forEach(([fromIndex, toIndex], index) => {
        const from = meshNodes[fromIndex],
          to = meshNodes[toIndex],
          dx = to[0] - from[0],
          dy = to[1] - from[1],
          length = Math.max(Math.hypot(dx, dy), 1),
          bend =
            (index % 2 ? 1 : -1) *
            size *
            (0.045 + (index % 3) * 0.012);
        addCurve(
          points,
          from,
          [
            (from[0] + to[0]) / 2 - (dy / length) * bend,
            (from[1] + to[1]) / 2 + (dx / length) * bend,
          ],
          to,
          22,
        );
      });
      meshNodes.forEach(([x, y]) =>
        addEllipse(points, x, y, size * 0.075, size * 0.075, 18),
      );
    } else if (name === "observatory") {
      addCurve(
        points,
        [cx - size, cy],
        [cx, cy - size * 0.86],
        [cx + size, cy],
        65,
      );
      addCurve(
        points,
        [cx - size, cy],
        [cx, cy + size * 0.86],
        [cx + size, cy],
        65,
      );
      addEllipse(points, cx, cy, size * 0.38, size * 0.38, 74);
      addEllipse(points, cx, cy, size * 0.11, size * 0.11, 28);
    } else {
      addEllipse(points, cx, cy, size, size, 96);
      addEllipse(points, cx, cy, size * 0.14, size * 0.14, 30);
      const pulse = [
        [cx - size * 0.82, cy],
        [cx - size * 0.45, cy],
        [cx - size * 0.26, cy - size * 0.18],
        [cx - size * 0.08, cy + size * 0.48],
        [cx + size * 0.16, cy - size * 0.55],
        [cx + size * 0.38, cy],
        [cx + size * 0.82, cy],
      ];
      for (let index = 0; index < pulse.length - 1; index++)
        addLine(points, pulse[index], pulse[index + 1], 22);
    }
    return Array.from({ length: count }, (_, index) => {
      const point = points[index % points.length];
      return {
        x: point.x + (Math.random() - 0.5) * 2,
        y: point.y + (Math.random() - 0.5) * 2,
      };
    });
  }

  function newScatterTarget() {
    return {
      x: Math.random() * field.width * (field.width < 800 ? 1 : 0.6),
      y: Math.random() * field.height,
    };
  }
  function reset() {
    field = sizeCanvas(canvas);
    const count = Math.min(560, Math.max(420, Math.floor(field.width / 2.4)));
    particles = Array.from({ length: count }, () => {
      const point = newScatterTarget();
      return {
        x: point.x,
        y: point.y,
        scatter: newScatterTarget(),
        ease: 0.009 + Math.random() * 0.014,
        phase: Math.random() * Math.PI * 2,
        shapeTarget: null,
        delay: 0,
      };
    });
    if (active) assignSymbol(active);
  }
  function disperse() {
    particles.forEach((particle) => {
      particle.scatter = newScatterTarget();
    });
  }
  function assignSymbol(name) {
    const shuffled = [...particles].sort(() => Math.random() - 0.5),
      formingCount = Math.floor(particles.length * 0.88),
      shape = symbolPoints(name, formingCount);
    particles.forEach((particle) => {
      particle.shapeTarget = null;
      particle.delay = Math.random() * 0.4;
    });
    shuffled.slice(0, formingCount).forEach((particle, index) => {
      particle.shapeTarget = shape[index];
    });
  }

  function activateModule(button) {
    active = button.dataset.symbol;
    assignSymbol(active);
    title.textContent = active.toUpperCase();
    description.textContent = button.dataset.description;
    buttons.forEach((item) => item.classList.toggle("active", item === button));
  }
  function deactivateModule() {
    active = null;
    disperse();
    buttons.forEach((item) => item.classList.remove("active"));
    title.textContent = "SYZYGY";
    description.textContent =
      "Uma arquitetura comum para capacidades que evoluem de forma independente.";
  }
  buttons.forEach((button) => {
    button.addEventListener("pointerenter", () => activateModule(button));
    button.addEventListener("pointerleave", deactivateModule);
    button.addEventListener("focus", () => activateModule(button));
    button.addEventListener("blur", deactivateModule);
  });

  function draw(time = performance.now()) {
    const { context } = field;
    context.clearRect(0, 0, field.width, field.height);
    const elapsedSeconds = Math.min(0.05, (time - lastDrawTime) / 1000);
    lastDrawTime = time;
    particles.forEach((particle) => {
      particle.delay = Math.max(0, particle.delay - elapsedSeconds);
      const forming = active && particle.shapeTarget && particle.delay === 0;
      const target = forming ? particle.shapeTarget : particle.scatter;
      const drift = forming ? 1.8 : 0,
        tx = target.x + Math.cos(time * 0.0007 + particle.phase) * drift,
        ty = target.y + Math.sin(time * 0.0009 + particle.phase) * drift;
      particle.x += (tx - particle.x) * particle.ease;
      particle.y += (ty - particle.y) * particle.ease;
      if (
        (!active || !particle.shapeTarget) &&
        Math.hypot(target.x - particle.x, target.y - particle.y) < 8
      )
        particle.scatter = newScatterTarget();
    });

    context.beginPath();
    particles.forEach((particle, index) => {
      if (index % 19 === 0) return;
      context.moveTo(particle.x + 1.25, particle.y);
      context.arc(particle.x, particle.y, 1.25, 0, Math.PI * 2);
    });
    context.fillStyle = particleMain;
    context.fill();

    context.beginPath();
    for (let index = 0; index < particles.length; index += 19) {
      const particle = particles[index];
      context.moveTo(particle.x + 2.9, particle.y);
      context.arc(particle.x, particle.y, 2.9, 0, Math.PI * 2);
    }
    context.fillStyle = particleRare;
    context.fill();
  }
  reset();
  animateWhenVisible(canvas, draw);
  window.addEventListener("resize", reset);
}

function createMyceliumField() {
  const canvas = document.getElementById("mycelium-particles");
  if (!canvas) return;
  const section = canvas.parentElement,
    cursor = section.querySelector(".mycelium-cursor");
  const particleMain = themeColor(
    "--mycelium-particle-main",
    "rgba(226,247,230,.68)",
  );
  const particleStrong = themeColor(
    "--mycelium-particle-strong",
    "rgba(226,247,230,.82)",
  );
  const particleRare = themeColor("--mycelium-particle-rare", "#c9ff45");
  const particleLineRgb = themeColor(
    "--mycelium-particle-line-rgb",
    "201,255,69",
  );
  const hyphaLine = themeColor("--mycelium-hypha-line", "rgba(201,255,69,.07)");
  let field = sizeCanvas(canvas),
    particles = [],
    vertices = [],
    edges = [],
    active = false,
    pointer = { x: 0, y: 0 };

  function distance(a, b) {
    return Math.hypot(a.x - b.x, a.y - b.y);
  }
  function makeEdge(from, to, weight) {
    return {
      from,
      to,
      weight,
      bend: (Math.random() - 0.5) * Math.min(150, weight * 0.55),
      phase: Math.random(),
      growth: 0,
      speed: 0.000025 + Math.random() * 0.000025,
    };
  }
  function connectVertex(index) {
    if (index === 0) return;
    const candidates = vertices
      .slice(0, index)
      .map((vertex, from) => ({
        from,
        weight: distance(vertex, vertices[index]),
      }))
      .sort((a, b) => a.weight - b.weight);
    const nearest = candidates[0];
    edges.push(makeEdge(nearest.from, index, nearest.weight));
    if (index >= 3 && index % 3 === 0 && candidates[1]) {
      const alternate = candidates[1];
      edges.push(makeEdge(alternate.from, index, alternate.weight));
    }
  }
  function curvePoint(edge, t, time) {
    const from = vertices[edge.from],
      to = vertices[edge.to],
      dx = to.x - from.x,
      dy = to.y - from.y,
      length = Math.max(edge.weight, 1),
      midX = (from.x + to.x) / 2 - (dy / length) * edge.bend,
      midY = (from.y + to.y) / 2 + (dx / length) * edge.bend,
      u = 1 - t;
    const breathe =
      Math.sin(time * 0.0007 + edge.phase * Math.PI * 2) *
      5 *
      Math.sin(t * Math.PI);
    return {
      x:
        u * u * from.x +
        2 * u * t * midX +
        t * t * to.x -
        (dy / length) * breathe,
      y:
        u * u * from.y +
        2 * u * t * midY +
        t * t * to.y +
        (dx / length) * breathe,
    };
  }
  function reset() {
    field = sizeCanvas(canvas);
    const count = performanceLite
      ? Math.min(85, Math.max(52, Math.floor(field.width / 14)))
      : Math.min(170, Math.max(110, Math.floor(field.width / 7)));
    particles = Array.from({ length: count }, () => ({
      x: Math.random() * field.width,
      y: Math.random() * field.height,
      vx: (Math.random() - 0.5) * 0.32,
      vy: (Math.random() - 0.5) * 0.32,
      phase: Math.random() * Math.PI * 2,
    }));
    vertices.forEach((vertex) => {
      vertex.x = Math.min(field.width - 12, vertex.x);
      vertex.y = Math.min(field.height - 12, vertex.y);
    });
    edges.forEach((edge) => {
      edge.weight = distance(vertices[edge.from], vertices[edge.to]);
    });
  }
  section.addEventListener("pointerenter", () => {
    active = true;
    section.classList.add("field-active");
  });
  section.addEventListener("pointerleave", () => {
    active = false;
    section.classList.remove("field-active");
  });
  section.addEventListener("pointermove", (event) => {
    const rect = section.getBoundingClientRect();
    pointer = { x: event.clientX - rect.left, y: event.clientY - rect.top };
    cursor.style.left = `${pointer.x}px`;
    cursor.style.top = `${pointer.y}px`;
  });
  section.addEventListener("pointerdown", () => {
    if (!active || vertices.length >= 12) return;
    const index = vertices.length;
    vertices.push({ x: pointer.x, y: pointer.y, pulse: 1 });
    connectVertex(index);
  });

  function drawHyphae(context, time) {
    edges.forEach((edge) => {
      edge.growth = Math.min(1, edge.growth + 0.005);
      const flowCount = Math.max(10, Math.floor(edge.weight / 13));
      context.beginPath();
      for (let step = 0; step <= 22 * edge.growth; step++) {
        const point = curvePoint(edge, step / 22, time);
        if (step === 0) context.moveTo(point.x, point.y);
        else context.lineTo(point.x, point.y);
      }
      context.strokeStyle = hyphaLine;
      context.lineWidth = 1;
      context.stroke();
      for (let i = 0; i < flowCount; i++) {
        const t = (i / flowCount + time * edge.speed + edge.phase) % 1;
        if (t > edge.growth) continue;
        const point = curvePoint(edge, t, time),
          flutter = Math.sin(time * 0.003 + i * 2.3) * 3.5;
        context.beginPath();
        context.arc(
          point.x + flutter * Math.sin(t * Math.PI),
          point.y + flutter * Math.cos(t * Math.PI),
          i % 7 === 0 ? 2.4 : 1.15,
          0,
          Math.PI * 2,
        );
        context.fillStyle = i % 7 === 0 ? particleRare : particleStrong;
        context.fill();
      }
    });
  }
  function draw() {
    const { context, width, height } = field,
      time = performance.now();
    context.clearRect(0, 0, width, height);
    particles.forEach((particle, index) => {
      const pointerDistance = distance(particle, pointer);
      if (active && pointerDistance < 230) {
        const influence = (1 - pointerDistance / 230) * 0.021;
        particle.vx +=
          ((pointer.x - particle.x) * influence) / Math.max(pointerDistance, 1);
        particle.vy +=
          ((pointer.y - particle.y) * influence) / Math.max(pointerDistance, 1);
      }
      particle.vx += Math.cos(particle.phase) * 0.004;
      particle.vy += Math.sin(particle.phase) * 0.004;
      particle.phase += 0.009;
      particle.vx *= 0.972;
      particle.vy *= 0.972;
      particle.x += particle.vx;
      particle.y += particle.vy;
      if (particle.x < 0) particle.x = width;
      if (particle.x > width) particle.x = 0;
      if (particle.y < 0) particle.y = height;
      if (particle.y > height) particle.y = 0;
      context.beginPath();
      context.arc(
        particle.x,
        particle.y,
        index % 17 === 0 ? 2.7 : 1.2,
        0,
        Math.PI * 2,
      );
      context.fillStyle = index % 17 === 0 ? particleRare : particleMain;
      context.fill();
    });
    const linkStride = performanceLite ? 2 : 1;
    for (let i = 0; i < particles.length; i += linkStride) {
      for (let j = i + linkStride; j < particles.length; j += linkStride) {
        const a = particles[i],
          b = particles[j],
          dx = a.x - b.x,
          dy = a.y - b.y,
          gapSquared = dx * dx + dy * dy;
        if (gapSquared < 68 * 68) {
          const gap = Math.sqrt(gapSquared);
          context.beginPath();
          context.moveTo(a.x, a.y);
          context.lineTo(b.x, b.y);
          context.strokeStyle = `rgba(${particleLineRgb},${(1 - gap / 68) * 0.1})`;
          context.stroke();
        }
      }
    }
    drawHyphae(context, time);
    vertices.forEach((vertex, index) => {
      vertex.pulse *= 0.96;
      const radius = 8 + Math.sin(time * 0.004 + index) * 2 + vertex.pulse * 14;
      context.beginPath();
      context.arc(vertex.x, vertex.y, radius, 0, Math.PI * 2);
      context.strokeStyle = `rgba(${particleLineRgb},.7)`;
      context.stroke();
      context.beginPath();
      context.arc(vertex.x, vertex.y, 3, 0, Math.PI * 2);
      context.fillStyle = particleRare;
      context.fill();
    });
  }
  reset();
  animateWhenVisible(canvas, draw);
  window.addEventListener("resize", reset);
}

function createModuleIdentity() {
  const identity = document.querySelector(".module-identity[data-identity]");
  if (!identity) return;
  const canvas = identity.querySelector(".module-identity-canvas"),
    kind = identity.dataset.identity,
    caption = identity.querySelector(".identity-caption span");
  const accent =
    getComputedStyle(identity).getPropertyValue("--module-accent").trim() ||
    "#c9ff45";
  const identityInk = themeColor("--identity-ink", "#171914", identity);
  const identityNetworkInk = themeColor(
    "--identity-network-ink",
    "#254b3b",
    identity,
  );
  const identityNetworkLineAlpha = parseFloat(
    themeColor("--identity-network-line-alpha", ".24", identity),
  );
  const identityNetworkSpecialAlpha = parseFloat(
    themeColor("--identity-network-special-alpha", ".7", identity),
  );
  const identityNetworkNodeAlpha = parseFloat(
    themeColor("--identity-network-node-alpha", ".65", identity),
  );
  const identityNetworkNodeRadius = parseFloat(
    themeColor("--identity-network-node-radius", "1.7", identity),
  );
  const identityNetworkSpecialWidth = parseFloat(
    themeColor("--identity-network-special-width", "1", identity),
  );
  let field = sizeCanvas(canvas),
    pointer = { x: field.width / 2, y: field.height * 0.44, active: false },
    pulse = 0,
    state = { count: 0, anchors: [], target: null, selected: 0 };
  const tau = Math.PI * 2;
  const seeded = (index, salt = 0) => {
    const value = Math.sin((index + 1) * 12.9898 + salt * 78.233) * 43758.5453;
    return value - Math.floor(value);
  };

  function circle(context, x, y, r, color = accent, alpha = 1) {
    context.save();
    context.globalAlpha = alpha;
    context.beginPath();
    context.arc(x, y, r, 0, tau);
    context.fillStyle = color;
    context.fill();
    context.restore();
  }
  function line(
    context,
    fromX,
    fromY,
    toX,
    toY,
    color = identityInk,
    alpha = 0.18,
    width = 1,
  ) {
    context.save();
    context.globalAlpha = alpha;
    context.beginPath();
    context.moveTo(fromX, fromY);
    context.lineTo(toX, toY);
    context.strokeStyle = color;
    context.lineWidth = width;
    context.stroke();
    context.restore();
  }
  function polygon(
    context,
    points,
    color = identityInk,
    alpha = 0.45,
    width = 1,
  ) {
    context.save();
    context.globalAlpha = alpha;
    context.beginPath();
    points.forEach((point, index) =>
      index
        ? context.lineTo(point[0], point[1])
        : context.moveTo(point[0], point[1]),
    );
    context.closePath();
    context.strokeStyle = color;
    context.lineWidth = width;
    context.stroke();
    context.restore();
  }

  function drawFoundation(context, width, height, time) {
    const cx =
        width / 2 + (pointer.active ? (pointer.x - width / 2) * 0.035 : 0),
      cy =
        height * 0.43 +
        (pointer.active ? (pointer.y - height * 0.43) * 0.035 : 0);
    [158, 108, 62].forEach((baseSize, index) => {
      const size = baseSize + (state.count % 4) * 4 * (3 - index);
      context.save();
      context.translate(cx, cy);
      context.rotate(Math.sin(time * 0.00035 + index) * 0.035 * (index + 1));
      context.globalAlpha = 0.22 + index * 0.12;
      context.strokeStyle = index === 2 ? accent : "#171914";
      context.lineWidth = index === 2 ? 1.5 : 1;
      context.strokeRect(-size / 2, -size / 2, size, size);
      [
        [-1, -1],
        [1, -1],
        [1, 1],
        [-1, 1],
      ].forEach((corner, cornerIndex) =>
        circle(
          context,
          (corner[0] * size) / 2,
          (corner[1] * size) / 2,
          cornerIndex === index ? 3 : 1.6,
          index === 2 ? accent : "#171914",
          0.55,
        ),
      );
      context.restore();
    });
    for (let index = 0; index < 16; index++) {
      const angle = time * 0.00014 * (index % 2 ? 1 : -1) + (index / 16) * tau,
        radius = 92 + seeded(index, 2) * 76;
      circle(
        context,
        cx + Math.cos(angle) * radius,
        cy + Math.sin(angle) * radius,
        seeded(index, 3) > 0.82 ? 2.5 : 1.15,
        index % 5 === 0 ? accent : "#171914",
        0.28 + seeded(index, 4) * 0.35,
      );
    }
    context.save();
    context.translate(cx, cy);
    context.rotate(Math.PI / 4 + Math.sin(time * 0.0007) * 0.04);
    context.fillStyle = accent;
    context.fillRect(-15, -15, 30, 30);
    context.restore();
    circle(context, cx, cy, 4, "#171914", 0.85);
    if (pointer.active) {
      line(context, pointer.x, pointer.y, cx, cy, accent, 0.38);
      circle(context, pointer.x, pointer.y, 4, accent, 0.8);
    }
  }

  function drawForge(context, width, height, time) {
    const cx = width / 2,
      cy = height * 0.49,
      heatX = pointer.active ? pointer.x : cx + Math.sin(time * 0.0006) * 38;
    const glow = context.createRadialGradient(
      heatX,
      cy - 72,
      0,
      heatX,
      cy - 72,
      90,
    );
    glow.addColorStop(0, accent);
    glow.addColorStop(1, "rgba(255,155,85,0)");
    context.save();
    context.globalAlpha = 0.16 + pulse * 0.12;
    context.fillStyle = glow;
    context.fillRect(0, 0, width, height);
    context.restore();
    const anvil = [
      [width * 0.18, cy - 58],
      [width * 0.66, cy - 58],
      [width * 0.84, cy - 34],
      [width * 0.7, cy - 13],
      [width * 0.55, cy - 8],
      [width * 0.51, cy + 57],
      [width * 0.67, cy + 76],
      [width * 0.67, cy + 89],
      [width * 0.31, cy + 89],
      [width * 0.31, cy + 76],
      [width * 0.46, cy + 57],
      [width * 0.42, cy - 8],
      [width * 0.2, cy - 22],
    ];
    polygon(context, anvil, "#171914", 0.68, 2);
    line(context, width * 0.19, cy - 48, width * 0.7, cy - 48, accent, 0.82, 2);
    context.save();
    context.translate(
      cx + 70 + (pointer.active ? (pointer.x - cx) * 0.06 : 0),
      cy - 105,
    );
    context.rotate(-0.62 + Math.sin(time * 0.0011) * 0.07 - pulse * 0.08);
    line(context, 0, 0, -48, 65, "#171914", 0.62, 5);
    context.fillStyle = accent;
    context.fillRect(-24, -12, 52, 24);
    context.restore();
    const sparkCount =
      30 + Math.min(24, state.count * 3) + Math.round(pulse * 18);
    for (let index = 0; index < sparkCount; index++) {
      const speed = 0.00012 + seeded(index, 1) * 0.00016,
        progress = (time * speed + seeded(index, 2)) % 1,
        direction = (seeded(index, 3) - 0.5) * 2.2;
      const x = heatX + direction * 85 * progress,
        y =
          cy -
          63 -
          Math.sin(progress * Math.PI) * (45 + seeded(index, 4) * 85) +
          progress * 28;
      circle(
        context,
        x,
        y,
        seeded(index, 5) > 0.82 ? 2.4 : 1.15,
        index % 4 === 0 ? "#171914" : accent,
        1 - progress,
      );
    }
  }

  function drawMycelium(context, width, height, time) {
    const nodes = Array.from({ length: 18 }, (_, index) => ({
      x:
        width * (0.14 + seeded(index, 1) * 0.72) +
        Math.sin(time * 0.00035 + index) * 7,
      y:
        height * (0.13 + seeded(index, 2) * 0.61) +
        Math.cos(time * 0.0003 + index * 1.7) * 7,
      special: false,
    }));
    state.anchors.forEach((anchor) =>
      nodes.push({
        x: anchor.x * width,
        y: anchor.y * height,
        special: true,
        pinned: true,
      }),
    );
    if (pointer.active)
      nodes.push({ x: pointer.x, y: pointer.y, special: true, pinned: false });
    for (let from = 0; from < nodes.length; from++)
      for (let to = from + 1; to < nodes.length; to++) {
        const a = nodes[from],
          b = nodes[to],
          distance = Math.hypot(a.x - b.x, a.y - b.y),
          reach = a.special || b.special ? 155 : 112;
        if (distance > reach) continue;
        context.save();
        context.globalAlpha =
          (1 - distance / reach) *
          (a.special || b.special
            ? identityNetworkSpecialAlpha
            : identityNetworkLineAlpha);
        context.beginPath();
        context.moveTo(a.x, a.y);
        const bend = Math.sin(time * 0.0005 + from * 2.1 + to) * 12;
        context.quadraticCurveTo(
          (a.x + b.x) / 2 + bend,
          (a.y + b.y) / 2 - bend,
          b.x,
          b.y,
        );
        context.strokeStyle =
          a.special || b.special ? accent : identityNetworkInk;
        context.lineWidth =
          a.special || b.special ? identityNetworkSpecialWidth : 1;
        context.stroke();
        context.restore();
      }
    nodes.forEach((node, index) => {
      const radius = node.special
        ? 5
        : index % 5 === 0
          ? 3.2
          : identityNetworkNodeRadius;
      circle(
        context,
        node.x,
        node.y,
        radius,
        node.special || index % 5 === 0 ? accent : identityNetworkInk,
        node.special ? 0.95 : identityNetworkNodeAlpha,
      );
      if (node.special) {
        context.save();
        context.globalAlpha = 0.32;
        context.strokeStyle = accent;
        context.beginPath();
        context.arc(node.x, node.y, 14 + pulse * 22, 0, tau);
        context.stroke();
        context.restore();
      }
    });
  }

  function drawObservatory(context, width, height, time) {
    const cx = width / 2,
      cy = height * 0.42,
      radius = Math.min(width, height) * 0.3;
    [1, 0.66, 0.32].forEach((scale, index) => {
      context.save();
      context.globalAlpha = 0.13 + index * 0.07;
      context.strokeStyle = "#171914";
      context.beginPath();
      context.arc(cx, cy, radius * scale, 0, tau);
      context.stroke();
      context.restore();
    });
    line(context, cx - radius, cy, cx + radius, cy, "#171914", 0.12);
    line(context, cx, cy - radius, cx, cy + radius, "#171914", 0.12);
    const sweep = time * 0.00055,
      gradient = context.createRadialGradient(cx, cy, 0, cx, cy, radius);
    gradient.addColorStop(0, accent);
    gradient.addColorStop(1, "rgba(139,217,255,0)");
    context.save();
    context.globalAlpha = 0.13;
    context.fillStyle = gradient;
    context.beginPath();
    context.moveTo(cx, cy);
    context.arc(cx, cy, radius, sweep - 0.48, sweep);
    context.closePath();
    context.fill();
    context.restore();
    line(
      context,
      cx,
      cy,
      cx + Math.cos(sweep) * radius,
      cy + Math.sin(sweep) * radius,
      accent,
      0.75,
      1.5,
    );
    for (let index = 0; index < 7; index++) {
      const angle = seeded(index, 5) * tau,
        r = radius * (0.2 + seeded(index, 6) * 0.72),
        x = cx + Math.cos(angle) * r,
        y = cy + Math.sin(angle) * r,
        flash = (Math.cos(sweep - angle) + 1) / 2;
      circle(
        context,
        x,
        y,
        2 + flash * 2,
        index % 3 === 0 ? accent : "#171914",
        0.3 + flash * 0.55,
      );
    }
    const fixed = state.target
        ? { x: state.target.x * width, y: state.target.y * height }
        : null,
      target = pointer.active
        ? pointer
        : fixed || { x: cx + radius * 0.42, y: cy - radius * 0.25 };
    line(
      context,
      target.x - 10,
      target.y,
      target.x + 10,
      target.y,
      accent,
      0.75,
    );
    line(
      context,
      target.x,
      target.y - 10,
      target.x,
      target.y + 10,
      accent,
      0.75,
    );
    circle(context, target.x, target.y, 13 + pulse * 18, accent, 0.12);
    context.save();
    context.beginPath();
    for (let step = 0; step <= 52; step++) {
      const x = width * 0.16 + (step / 52) * width * 0.68,
        y =
          height * 0.73 +
          Math.sin(step * 0.65 + time * 0.0022) * 5 +
          Math.sin(step * 0.18 + time * 0.001) * 9;
      if (step) context.lineTo(x, y);
      else context.moveTo(x, y);
    }
    context.strokeStyle = accent;
    context.globalAlpha = 0.7;
    context.stroke();
    context.restore();
  }

  function drawNerv(context, width, height, time) {
    const cx = width / 2,
      cy = height * 0.43,
      radius = Math.min(width, height) * 0.27,
      nodes = [];
    for (let index = 0; index < 7; index++) {
      const angle = (index / 7) * tau - time * 0.00012 * (index % 2 ? 1 : -1),
        r = radius * (index % 3 === 0 ? 0.72 : 1),
        node = { x: cx + Math.cos(angle) * r, y: cy + Math.sin(angle) * r };
      nodes.push(node);
      line(
        context,
        cx,
        cy,
        node.x,
        node.y,
        index % 2 ? accent : "#171914",
        0.18 + index * 0.018,
      );
    }
    let focused = state.selected,
      best = Infinity;
    if (pointer.active)
      nodes.forEach((node, index) => {
        const distance = Math.hypot(pointer.x - node.x, pointer.y - node.y);
        if (distance < best) {
          best = distance;
          focused = index;
        }
      });
    nodes.forEach((node, index) => {
      circle(
        context,
        node.x,
        node.y,
        index === focused ? 6 : index % 3 === 0 ? 4 : 2.5,
        index === focused || index % 3 === 0 ? accent : "#171914",
        index === focused ? 0.95 : 0.58,
      );
      if (index === focused)
        circle(context, node.x, node.y, 16 + pulse * 18, accent, 0.16);
    });
    context.save();
    context.translate(cx, cy);
    context.rotate(time * 0.00035);
    context.strokeStyle = accent;
    context.globalAlpha = 0.72;
    context.lineWidth = 2;
    context.beginPath();
    context.arc(0, 0, 44, -0.25, 1.65);
    context.stroke();
    context.beginPath();
    context.arc(0, 0, 57, 2.3, 4.9);
    context.stroke();
    context.restore();
    circle(context, cx, cy, 25, "#171914", 0.9);
    circle(context, cx, cy, 8, accent, 0.95);
    const beat = (time * 0.0012) % 1;
    context.save();
    context.globalAlpha = (1 - beat) * 0.28;
    context.strokeStyle = accent;
    context.beginPath();
    context.arc(cx, cy, 32 + beat * 68, 0, tau);
    context.stroke();
    context.restore();
    if (pointer.active && nodes[focused])
      line(
        context,
        pointer.x,
        pointer.y,
        nodes[focused].x,
        nodes[focused].y,
        accent,
        0.3,
      );
  }

  function drawCoppermind(context, width, height, time) {
    const cx = width / 2,
      cy = height * 0.43,
      nodes = Array.from({ length: 15 }, (_, index) => ({
        x:
          width * (0.18 + seeded(index, 1) * 0.64) +
          Math.sin(time * 0.0003 + index) * 4,
        y:
          height * (0.14 + seeded(index, 2) * 0.57) +
          Math.cos(time * 0.00027 + index) * 4,
      }));
    for (let from = 0; from < nodes.length; from++)
      for (let to = from + 1; to < nodes.length; to++) {
        const gap = Math.hypot(
          nodes[from].x - nodes[to].x,
          nodes[from].y - nodes[to].y,
        );
        if (gap < 105)
          line(
            context,
            nodes[from].x,
            nodes[from].y,
            nodes[to].x,
            nodes[to].y,
            accent,
            0.11,
          );
      }
    nodes.forEach((node, index) =>
      circle(
        context,
        node.x,
        node.y,
        index === state.selected ? 5 : index % 4 === 0 ? 3 : 1.5,
        index === state.selected ? accent : "#171914",
        index === state.selected ? 0.9 : 0.42,
      ),
    );
    context.save();
    context.translate(cx, cy);
    context.globalAlpha = 0.7;
    context.strokeStyle = accent;
    context.beginPath();
    context.moveTo(-52, -34);
    context.quadraticCurveTo(-20, -45, 0, -23);
    context.quadraticCurveTo(20, -45, 52, -34);
    context.lineTo(52, 48);
    context.quadraticCurveTo(20, 36, 0, 56);
    context.quadraticCurveTo(-20, 36, -52, 48);
    context.closePath();
    context.stroke();
    line(context, 0, -23, 0, 56, accent, 0.7);
    context.restore();
    if (pointer.active) {
      const nearest = nodes.reduce(
        (best, node, index) => {
          const gap = Math.hypot(pointer.x - node.x, pointer.y - node.y);
          return gap < best.gap ? { index, gap, node } : best;
        },
        { index: 0, gap: Infinity, node: nodes[0] },
      );
      line(
        context,
        pointer.x,
        pointer.y,
        nearest.node.x,
        nearest.node.y,
        accent,
        0.45,
      );
    }
  }

  function drawMagi(context, width, height, time) {
    const cx = width / 2,
      cy = height * 0.43,
      radius = Math.min(width, height) * 0.26,
      voices = ["M", "B", "C"],
      points = [];
    for (let index = 0; index < 3; index++) {
      const angle = -Math.PI / 2 + (index * tau) / 3,
        point = {
          x: cx + Math.cos(angle) * radius,
          y: cy + Math.sin(angle) * radius,
        };
      points.push(point);
      line(context, cx, cy, point.x, point.y, accent, 0.26, 1.4);
      circle(
        context,
        point.x,
        point.y,
        index === state.selected ? 24 : 19,
        index === state.selected ? accent : "#171914",
        index === state.selected ? 0.85 : 0.12,
      );
      context.save();
      context.fillStyle = index === state.selected ? "#171914" : "#171914";
      context.globalAlpha = index === state.selected ? 1 : 0.72;
      context.font = "700 12px Arial";
      context.textAlign = "center";
      context.textBaseline = "middle";
      context.fillText(voices[index], point.x, point.y);
      context.restore();
    }
    context.save();
    context.translate(cx, cy);
    context.rotate(time * 0.0003);
    polygon(
      context,
      [
        [0, -28],
        [25, 16],
        [-25, 16],
      ],
      accent,
      0.78,
      2,
    );
    context.restore();
    for (let index = 0; index < 12; index++) {
      const angle = time * 0.0002 + (index / 12) * tau;
      circle(
        context,
        cx + Math.cos(angle) * (radius + 28),
        cy + Math.sin(angle) * (radius + 28),
        1.4,
        accent,
        0.35,
      );
    }
    if (pointer.active)
      line(
        context,
        pointer.x,
        pointer.y,
        points[state.selected].x,
        points[state.selected].y,
        accent,
        0.28,
      );
  }

  function drawBalance(context, width, height, time) {
    const cx = width / 2,
      cy = height * 0.42,
      liveTilt = pointer.active
        ? (pointer.x / width - 0.5) * 0.35
        : Math.sin(time * 0.00045) * 0.045,
      tilt = liveTilt + ((state.count % 3) - 1) * 0.025;
    line(context, cx, cy - 78, cx, cy + 92, "#171914", 0.56, 3);
    line(context, cx - 55, cy + 92, cx + 55, cy + 92, "#171914", 0.56, 3);
    circle(context, cx, cy - 78, 8, accent, 0.9);
    context.save();
    context.translate(cx, cy - 70);
    context.rotate(tilt);
    line(context, -118, 0, 118, 0, "#171914", 0.72, 2);
    [-1, 1].forEach((side) => {
      line(context, side * 91, 0, side * 91, 64, "#171914", 0.35);
      context.beginPath();
      context.arc(side * 91, 64, 34, 0, Math.PI);
      context.strokeStyle = side < 0 ? accent : "#171914";
      context.globalAlpha = 0.55;
      context.stroke();
      for (let index = 0; index < 5; index++)
        circle(
          context,
          side * 91 - 20 + index * 10,
          55 - seeded(index, side) * 14,
          2.3,
          side < 0 ? accent : "#171914",
          0.55,
        );
    });
    context.restore();
    context.save();
    context.fillStyle = accent;
    context.globalAlpha = 0.72;
    context.font = "700 9px Arial";
    context.textAlign = "center";
    context.fillText("EQUILIBRIUM", cx, cy + 118);
    context.restore();
  }

  function drawTungsten(context, width, height, time) {
    const cx = width / 2,
      cy = height * 0.43,
      radius = Math.min(width, height) * 0.26;
    polygon(
      context,
      Array.from({ length: 6 }, (_, index) => {
        const angle = -Math.PI / 2 + (index * tau) / 6;
        return [cx + Math.cos(angle) * radius, cy + Math.sin(angle) * radius];
      }),
      "#171914",
      0.5,
      2,
    );
    [74, 50, 27].forEach((ring, index) => {
      context.save();
      context.translate(cx, cy);
      context.rotate(
        (index % 2 ? 1 : -1) * time * 0.00018 + (state.count % 2) * 0.25,
      );
      context.strokeStyle = index === 2 ? accent : "#171914";
      context.globalAlpha = 0.25 + index * 0.18;
      context.lineWidth = index === 2 ? 3 : 1;
      context.beginPath();
      context.arc(0, 0, ring, 0.12 + index * 0.4, tau - 0.35 - index * 0.18);
      context.stroke();
      for (let mark = 0; mark < 4; mark++)
        circle(
          context,
          Math.cos((mark * tau) / 4) * ring,
          Math.sin((mark * tau) / 4) * ring,
          2,
          index === 2 ? accent : "#171914",
          0.55,
        );
      context.restore();
    });
    context.save();
    context.translate(cx, cy);
    context.fillStyle = "#171914";
    context.globalAlpha = 0.86;
    context.fillRect(-15, -5, 30, 34);
    context.strokeStyle = accent;
    context.lineWidth = 3;
    context.beginPath();
    context.arc(0, -5, 11, Math.PI, tau);
    context.stroke();
    context.restore();
    if (pointer.active)
      line(context, pointer.x, pointer.y, cx, cy, accent, 0.26);
  }

  function drawImrryr(context, width, height, time) {
    const shiftX = pointer.active
        ? (pointer.x / width - 0.5) * 18
        : Math.sin(time * 0.0004) * 4,
      shiftY = pointer.active ? (pointer.y / height - 0.5) * 12 : 0;
    const windows = [
      { x: 0.2, y: 0.17, w: 0.53, h: 0.35 },
      { x: 0.31, y: 0.3, w: 0.53, h: 0.35 },
      { x: 0.16, y: 0.43, w: 0.53, h: 0.28 },
    ];
    windows.forEach((item, index) => {
      const active = index === state.selected,
        x = width * item.x + shiftX * (index - 1),
        y = height * item.y + shiftY * (index - 1);
      context.save();
      context.globalAlpha = active ? 0.84 : 0.24;
      context.fillStyle = active ? accent : "#f2f0e9";
      context.strokeStyle = "#171914";
      context.fillRect(x, y, width * item.w, height * item.h);
      context.strokeRect(x, y, width * item.w, height * item.h);
      line(
        context,
        x,
        y + 22,
        x + width * item.w,
        y + 22,
        "#171914",
        active ? 0.55 : 0.25,
      );
      [0, 1, 2].forEach((dot) =>
        circle(context, x + 12 + dot * 9, y + 11, 2, "#171914", 0.6),
      );
      context.restore();
    });
  }

  function drawElric(context, width, height, time) {
    const cx = width / 2,
      cy = height * 0.41,
      radius = Math.min(width, height) * 0.25;
    for (let index = 0; index < 5; index++) {
      context.save();
      context.globalAlpha = 0.12 + index * 0.055;
      context.strokeStyle = index === state.selected % 5 ? accent : "#171914";
      context.lineWidth = index === state.selected % 5 ? 2 : 1;
      context.beginPath();
      context.arc(
        cx,
        cy,
        radius - index * 16,
        -1.25 + index * 0.22,
        1.75 + index * 0.3,
      );
      context.stroke();
      context.restore();
    }
    circle(context, cx, cy - 31, 24, accent, 0.36);
    context.save();
    context.globalAlpha = 0.48;
    context.strokeStyle = "#171914";
    context.beginPath();
    context.arc(cx, cy + 43, 54, Math.PI, 0);
    context.stroke();
    context.restore();
    const angle = time * 0.00035 + state.selected * 0.8,
      marker = {
        x: cx + Math.cos(angle) * radius,
        y: cy + Math.sin(angle) * radius,
      };
    circle(context, marker.x, marker.y, 5, accent, 0.92);
    if (pointer.active)
      line(context, pointer.x, pointer.y, marker.x, marker.y, accent, 0.3);
  }

  function drawBastion(context, width, height, time) {
    const cx = width / 2,
      cy = height * 0.41,
      radius = Math.min(width, height) * 0.27,
      shield = [
        [cx, cy - radius],
        [cx + radius * 0.78, cy - radius * 0.64],
        [cx + radius * 0.65, cy + radius * 0.42],
        [cx, cy + radius],
        [cx - radius * 0.65, cy + radius * 0.42],
        [cx - radius * 0.78, cy - radius * 0.64],
      ];
    polygon(context, shield, accent, 0.72, 2);
    context.save();
    context.beginPath();
    context.rect(cx - 58, cy - 47, 116, 94);
    context.strokeStyle = "#171914";
    context.globalAlpha = 0.35;
    context.stroke();
    context.setLineDash([4, 5]);
    context.beginPath();
    context.arc(cx, cy, 32, 0, tau);
    context.stroke();
    context.restore();
    const scan = (time * 0.00025 + state.count * 0.17) % 1,
      scanY = cy - 45 + scan * 90;
    line(context, cx - 55, scanY, cx + 55, scanY, accent, 0.72, 2);
    for (let index = 0; index < 9; index++) {
      const x = cx - 42 + seeded(index, 6) * 84,
        y = cy - 35 + seeded(index, 7) * 70;
      circle(
        context,
        x,
        y,
        index === state.selected ? 4 : 1.8,
        index === state.selected ? accent : "#171914",
        index === state.selected ? 0.9 : 0.5,
      );
    }
    if (pointer.active)
      line(context, pointer.x, pointer.y, cx, cy, accent, 0.22);
  }

  const drawers = {
    foundation: drawFoundation,
    forge: drawForge,
    mycelium: drawMycelium,
    observatory: drawObservatory,
    nerv: drawNerv,
    coppermind: drawCoppermind,
    magi: drawMagi,
    balance: drawBalance,
    tungsten: drawTungsten,
    imrryr: drawImrryr,
    elric: drawElric,
    bastion: drawBastion,
  };
  function draw(time = performance.now()) {
    const { context, width, height } = field;
    context.clearRect(0, 0, width, height);
    drawers[kind]?.(context, width, height, time);
    if (pulse > 0.01) {
      const center = pointer.active
        ? pointer
        : { x: width / 2, y: height * 0.43 };
      context.save();
      context.globalAlpha = pulse * 0.34;
      context.strokeStyle = accent;
      context.lineWidth = 1.5;
      context.beginPath();
      context.arc(center.x, center.y, 18 + (1 - pulse) * 95, 0, tau);
      context.stroke();
      context.restore();
      pulse *= 0.94;
    }
  }
  function redraw() {
    if (reducedMotion) draw(performance.now());
  }
  function setPointer(event) {
    const rect = identity.getBoundingClientRect();
    pointer = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
      active: true,
    };
    redraw();
  }
  function updateCaption() {
    const labels = {
      foundation: `CAMADAS · ${1 + (state.count % 4)}`,
      forge: `IMPACTOS · ${state.count}`,
      mycelium: `PARES · ${state.anchors.length}`,
      observatory: state.target ? "SINAL · FIXADO" : "SINAL · LIVRE",
      nerv: `SERVIÇO · ${String(state.selected + 1).padStart(2, "0")}`,
      coppermind: `MEMÓRIA · ${String(state.selected + 1).padStart(2, "0")}`,
      magi: ["MELCHIOR", "BALTHASAR", "CASPER"][state.selected],
      balance: "EQUILÍBRIO · RECALCULADO",
      tungsten: state.count % 2 ? "COFRE · SELADO" : "COFRE · EM ROTAÇÃO",
      imrryr: `ESPAÇO · ${String(state.selected + 1).padStart(2, "0")}`,
      elric: `CONTEXTO · ${String(state.selected + 1).padStart(2, "0")}`,
      bastion: `VARREDURA · ${String(state.count).padStart(2, "0")}`,
    };
    if (caption) caption.textContent = labels[kind] || caption.textContent;
  }
  function activate() {
    pointer.active = true;
    state.count += 1;
    pulse = 1;
    if (kind === "mycelium") {
      state.anchors.push({
        x: pointer.x / field.width,
        y: pointer.y / field.height,
      });
      if (state.anchors.length > 5) state.anchors.shift();
    }
    if (kind === "observatory")
      state.target = {
        x: pointer.x / field.width,
        y: pointer.y / field.height,
      };
    if (
      ["nerv", "coppermind", "magi", "imrryr", "elric", "bastion"].includes(
        kind,
      )
    )
      state.selected =
        (state.selected + 1) %
        (kind === "magi"
          ? 3
          : kind === "imrryr"
            ? 3
            : kind === "elric"
              ? 5
              : kind === "bastion"
                ? 9
                : kind === "coppermind"
                  ? 15
                  : 7);
    updateCaption();
    redraw();
  }
  identity.addEventListener("pointerenter", setPointer);
  identity.addEventListener("pointermove", setPointer);
  identity.addEventListener("pointerleave", () => {
    pointer.active = false;
    redraw();
  });
  identity.addEventListener("pointerdown", (event) => {
    setPointer(event);
    activate();
  });
  identity.addEventListener("focus", () => {
    pointer = { x: field.width / 2, y: field.height * 0.43, active: true };
    pulse = 1;
    redraw();
  });
  identity.addEventListener("blur", () => {
    pointer.active = false;
    redraw();
  });
  identity.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    event.preventDefault();
    activate();
  });
  function reset() {
    field = sizeCanvas(canvas);
    if (!pointer.active)
      pointer = { x: field.width / 2, y: field.height * 0.43, active: false };
    redraw();
  }
  reset();
  animateWhenVisible(canvas, draw);
  window.addEventListener("resize", reset);
}

function createModuleDemo() {
  const identity = document.querySelector(".module-identity[data-identity]"),
    anchor = document.querySelector(".capabilities");
  if (!identity || !anchor) return;
  const key = identity.dataset.identity,
    accent =
      getComputedStyle(identity).getPropertyValue("--module-accent").trim() ||
      "#c9ff45";
  const networkLink = themeColor(
    "--network-link",
    "rgba(201,255,69,.28)",
    identity,
  );
  const networkRoot = themeColor("--network-root", "#171914", identity);
  const networkLabel = themeColor("--network-label", "#dce4de", identity);
  const descriptions = {
    foundation: {
      implemented: true,
      title: "O núcleo em movimento.",
      lead: "Ative cada camada e acompanhe como configuração, persistência, eventos e registro sustentam o sistema.",
      instrument: "BOOT CORE",
    },
    forge: {
      implemented: true,
      title: "Um fluxo que pode ser inspecionado.",
      lead: "Percorra descoberta, plano, confirmação, execução e outbox como etapas distintas de uma operação segura.",
      instrument: "BUILD PIPELINE",
    },
    mycelium: {
      implemented: true,
      title: "Construa uma pequena topologia.",
      lead: "Novos pares se conectam ao nó Hypha sem sugerir descoberta automática ou sincronização ainda inexistente.",
      instrument: "PEER MAP",
    },
    observatory: {
      implemented: true,
      title: "Observe o sinal vivo.",
      lead: "Alterne entre serviços e acompanhe uma janela de saúde que se move continuamente.",
      instrument: "SIGNAL SCOPE",
    },
    nerv: {
      implemented: true,
      title: "Opere sem perder a origem.",
      lead: "Selecione serviços, altere seu estado simulado e execute probes dentro de uma superfície operacional.",
      instrument: "CONTROL DECK",
    },
    tungsten: {
      implemented: false,
      title: "Uma concessão com começo e fim.",
      lead: "Percorra solicitação, política, lease, auditoria e revogação sem manipular qualquer segredo real.",
      instrument: "TRUST GATE",
    },
    coppermind: {
      implemented: false,
      title: "Faça a memória criar relações.",
      lead: "Adicione documentos conceituais a um grafo local e acompanhe a formação de conexões rastreáveis.",
      instrument: "MEMORY GRAPH",
    },
    magi: {
      implemented: false,
      title: "Mude a perspectiva do conselho.",
      lead: "Dê foco a cada especialidade e veja como a síntese preserva contribuições diferentes.",
      instrument: "COUNCIL TABLE",
    },
    balance: {
      implemented: false,
      title: "Pese exploração e política.",
      lead: "Ajuste as forças de Chaos e Law para observar como Equilibrium altera a recomendação.",
      instrument: "DECISION FIELD",
    },
    elric: {
      implemented: false,
      title: "Modele um contexto pessoal.",
      lead: "Alterne preferências e contextos em um perfil local que continua referenciando a identidade do Foundation.",
      instrument: "CONTEXT LENS",
    },
    imrryr: {
      implemented: false,
      title: "Troque de ferramenta sem sair do espaço.",
      lead: "Navegue por editor, terminal e explorer dentro de um pequeno workspace conceitual.",
      instrument: "APP SPACE",
    },
    bastion: {
      implemented: false,
      title: "Atravesse o ciclo de isolamento.",
      lead: "Autorize, isole, analise e desmonte um laboratório conceitual sem executar nenhuma ação de segurança.",
      instrument: "LAB CHAMBER",
    },
  };
  const info = descriptions[key];
  if (!info) return;
  const section = document.createElement("section");
  section.className = "module-demo section";
  section.dataset.demo = key;
  section.id = "demo";
  section.setAttribute("aria-label", "Modelo interativo do " + key);
  anchor.insertAdjacentElement("afterend", section);
  const type = info.implemented
    ? "MODELO DO MVP"
    : "PROTÓTIPO CONCEITUAL · NÃO IMPLEMENTADO";
  section.innerHTML =
    '<div class="demo-heading reveal"><div><p class="kicker"><span></span> ' +
    type +
    "</p><h2>" +
    info.title +
    "</h2></div><p>" +
    info.lead +
    '</p></div><div class="instrument-shell reveal" data-instrument="' +
    key +
    '"><aside class="instrument-context"><span>' +
    type +
    "</span><h3>" +
    key.toUpperCase() +
    "</h3><p>Uma miniatura manipulável da capacidade, sem comunicação com serviços ou dados reais.</p><i>" +
    info.instrument +
    '</i></aside><div class="instrument-surface"><header><span>INSTRUMENTO / ' +
    info.instrument +
    '</span><strong data-instrument-status aria-live="polite"></strong></header><div class="instrument-host"></div></div></div>';
  const host = section.querySelector(".instrument-host"),
    status = section.querySelector("[data-instrument-status]");

  function renderFlow() {
    const flows = {
      foundation: {
        action: "Executar boot",
        ready: "CORE READY",
        steps: [
          ["CONFIG", "Ambiente validado"],
          ["SQLITE", "Schema local pronto"],
          ["EVENTBUS", "Adaptador disponível"],
          ["REGISTRY", "Módulos legíveis"],
        ],
      },
      forge: {
        action: "Executar pipeline",
        ready: "RUN COMPLETE",
        steps: [
          ["DISCOVER", "Manifesto encontrado"],
          ["PLAN", "argv e cwd explícitos"],
          ["CONFIRM", "Política aprovada"],
          ["RUN", "Processo concluído"],
          ["OUTBOX", "Evento preservado"],
        ],
      },
      tungsten: {
        action: "Simular concessão",
        ready: "LEASE REVOKED",
        steps: [
          ["REQUEST", "Sujeito solicita escopo"],
          ["POLICY", "Regra local avaliada"],
          ["LEASE", "Acesso temporário"],
          ["AUDIT", "Uso sem segredo"],
          ["REVOKE", "Material liberado"],
        ],
      },
      bastion: {
        action: "Iniciar ciclo",
        ready: "LAB RESTORED",
        steps: [
          ["AUTHORIZE", "Escopo registrado"],
          ["ISOLATE", "Rede sem egress"],
          ["ANALYZE", "Evidência coletada"],
          ["TEARDOWN", "Snapshot restaurado"],
        ],
      },
    };
    const data = flows[key];
    host.innerHTML =
      '<div class="sequence-core"><div class="sequence-orb"><span></span><i></i></div><strong data-sequence-label>' +
      data.steps[0][0] +
      "</strong><small data-sequence-copy>" +
      data.steps[0][1] +
      '</small></div><div class="sequence-track" role="list">' +
      data.steps
        .map(
          (step, index) =>
            '<button class="sequence-step" type="button" data-step="' +
            index +
            '"><span>' +
            String(index + 1).padStart(2, "0") +
            "</span><strong>" +
            step[0] +
            "</strong></button>",
        )
        .join("") +
      '</div><button class="instrument-action" type="button">' +
      data.action +
      " <span>→</span></button>";
    const steps = [...host.querySelectorAll(".sequence-step")],
      label = host.querySelector("[data-sequence-label]"),
      copy = host.querySelector("[data-sequence-copy]"),
      orb = host.querySelector(".sequence-orb"),
      action = host.querySelector(".instrument-action");
    let active = 0,
      timer = null;
    function select(index) {
      active = index;
      steps.forEach((step, position) => {
        step.classList.toggle("active", position === index);
        step.classList.toggle("complete", position < index);
      });
      label.textContent = data.steps[index][0];
      copy.textContent = data.steps[index][1];
      orb.style.setProperty(
        "--stage",
        String(index / (data.steps.length - 1 || 1)),
      );
      status.textContent =
        data.steps[index][0] + " / " + String(index + 1).padStart(2, "0");
    }
    steps.forEach((step, index) =>
      step.addEventListener("click", () => {
        clearInterval(timer);
        select(index);
      }),
    );
    action.addEventListener("click", () => {
      clearInterval(timer);
      if (reducedMotion) {
        select(steps.length - 1);
        status.textContent = data.ready;
        return;
      }
      select(0);
      action.disabled = true;
      timer = setInterval(() => {
        if (active >= steps.length - 1) {
          clearInterval(timer);
          action.disabled = false;
          status.textContent = data.ready;
          return;
        }
        select(active + 1);
      }, 520);
    });
    select(0);
  }

  function renderNetwork() {
    const isMemory = key === "coppermind",
      labels = isMemory
        ? ["ADR-004", "Forge", "NERV", "README", "Vision", "Events"]
        : ["HYPHA-01", "HYPHA-02", "HYPHA-03", "NAS-01", "PHONE-01", "LAB-01"];
    host.innerHTML =
      '<div class="network-instrument"><canvas aria-label="' +
      (isMemory
        ? "Grafo conceitual de documentos"
        : "Topologia local de pares") +
      '"></canvas><div class="network-legend"><span><i></i>' +
      (isMemory ? "fonte local" : "nó conhecido") +
      '</span><strong data-network-count></strong></div></div><div class="instrument-toolbar"><button class="instrument-action" type="button">' +
      (isMemory ? "Indexar documento" : "Adicionar peer") +
      ' <span>+</span></button><button class="instrument-quiet" type="button">Limpar</button></div>';
    const canvas = host.querySelector("canvas"),
      count = host.querySelector("[data-network-count]"),
      add = host.querySelector(".instrument-action"),
      clear = host.querySelector(".instrument-quiet");
    let field = sizeCanvas(canvas),
      nodes = [],
      phase = 0;
    function seed() {
      field = sizeCanvas(canvas);
      nodes = [
        {
          x: field.width / 2,
          y: field.height / 2,
          label: labels[0],
          root: true,
        },
      ];
      if (isMemory) {
        nodes.push(
          { x: field.width * 0.3, y: field.height * 0.35, label: labels[1] },
          { x: field.width * 0.72, y: field.height * 0.38, label: labels[2] },
        );
      }
      update();
    }
    function update() {
      count.textContent =
        String(nodes.length).padStart(2, "0") +
        " " +
        (isMemory ? "FONTES" : "NÓS");
      status.textContent = isMemory
        ? "ÍNDICE LOCAL · " + nodes.length
        : "TOPOLOGIA · " + nodes.length;
      if (reducedMotion) draw();
    }
    function addNode(x, y) {
      if (nodes.length >= labels.length) return;
      const index = nodes.length,
        angle = index * 2.18;
      nodes.push({
        x: x ?? field.width / 2 + Math.cos(angle) * field.width * 0.28,
        y: y ?? field.height / 2 + Math.sin(angle) * field.height * 0.28,
        label: labels[index],
      });
      update();
    }
    function draw() {
      const { context, width, height } = field;
      context.clearRect(0, 0, width, height);
      phase += 0.008;
      for (let index = 1; index < nodes.length; index++) {
        const node = nodes[index],
          nearest = nodes.slice(0, index).reduce(
            (best, candidate) =>
              Math.hypot(candidate.x - node.x, candidate.y - node.y) <
              best.distance
                ? {
                    node: candidate,
                    distance: Math.hypot(
                      candidate.x - node.x,
                      candidate.y - node.y,
                    ),
                  }
                : best,
            { node: nodes[0], distance: Infinity },
          );
        context.beginPath();
        context.moveTo(node.x, node.y);
        context.quadraticCurveTo(
          (node.x + nearest.node.x) / 2 + Math.sin(index) * 18,
          (node.y + nearest.node.y) / 2 + Math.cos(index) * 18,
          nearest.node.x,
          nearest.node.y,
        );
        context.strokeStyle = networkLink;
        context.stroke();
        const flow = (phase + index * 0.17) % 1,
          fx = node.x + (nearest.node.x - node.x) * flow,
          fy = node.y + (nearest.node.y - node.y) * flow;
        circlePoint(context, fx, fy, 2.4, accent, 0.9);
      }
      nodes.forEach((node) => {
        circlePoint(
          context,
          node.x,
          node.y,
          node.root ? 13 : 7,
          node.root ? networkRoot : accent,
          0.96,
        );
        context.fillStyle = networkLabel;
        context.font = "700 9px Arial";
        context.textAlign = "center";
        context.fillText(node.label, node.x, node.y + 25);
      });
    }
    function circlePoint(context, x, y, r, color, alpha) {
      context.save();
      context.globalAlpha = alpha;
      context.beginPath();
      context.arc(x, y, r, 0, Math.PI * 2);
      context.fillStyle = color;
      context.fill();
      context.restore();
    }
    function resize() {
      const previous = field;
      field = sizeCanvas(canvas);
      const scaleX = previous.width ? field.width / previous.width : 1,
        scaleY = previous.height ? field.height / previous.height : 1;
      nodes.forEach((node) => {
        node.x *= scaleX;
        node.y *= scaleY;
      });
      if (reducedMotion) draw();
    }
    add.addEventListener("click", () => addNode());
    clear.addEventListener("click", seed);
    canvas.addEventListener("pointerdown", (event) => {
      const rect = canvas.getBoundingClientRect();
      addNode(event.clientX - rect.left, event.clientY - rect.top);
    });
    window.addEventListener("resize", resize);
    seed();
    animateWhenVisible(canvas, draw);
  }

  function renderTelemetry() {
    const services = [
      { name: "Foundation", health: "healthy", level: 96 },
      { name: "Forge", health: "healthy", level: 88 },
      { name: "Mycelium", health: "forming", level: 62 },
    ];
    host.innerHTML =
      '<div class="scope-tabs">' +
      services
        .map(
          (service, index) =>
            '<button type="button" data-service="' +
            index +
            '">' +
            service.name +
            "</button>",
        )
        .join("") +
      '</div><div class="signal-scope"><canvas aria-label="Série temporal simulada de saúde"></canvas><div class="scope-metrics"><div><span>STATUS</span><strong data-health></strong></div><div><span>AMOSTRAS</span><strong data-samples>24</strong></div><div><span>ESTABILIDADE</span><strong data-stability></strong></div></div></div>';
    const canvas = host.querySelector("canvas"),
      buttons = [...host.querySelectorAll("[data-service]")],
      health = host.querySelector("[data-health]"),
      stability = host.querySelector("[data-stability]");
    let field = sizeCanvas(canvas),
      active = 0,
      phase = 0;
    function select(index) {
      active = index;
      buttons.forEach((button, position) =>
        button.classList.toggle("active", position === index),
      );
      health.textContent = services[index].health;
      stability.textContent = services[index].level + "%";
      status.textContent =
        services[index].name.toUpperCase() +
        " · " +
        services[index].health.toUpperCase();
      if (reducedMotion) draw();
    }
    function draw() {
      const { context, width, height } = field;
      context.clearRect(0, 0, width, height);
      context.strokeStyle = "rgba(255,255,255,.08)";
      for (let row = 1; row < 5; row++) {
        context.beginPath();
        context.moveTo(0, (row * height) / 5);
        context.lineTo(width, (row * height) / 5);
        context.stroke();
      }
      const service = services[active],
        points = 64;
      context.beginPath();
      for (let index = 0; index < points; index++) {
        const x = (index / (points - 1)) * width,
          noise =
            Math.sin(index * 0.52 + phase) * 14 +
            Math.sin(index * 0.16 + phase * 0.5) * 9,
          y = height * (1 - service.level / 120) + noise;
        if (index) context.lineTo(x, y);
        else context.moveTo(x, y);
      }
      context.strokeStyle = accent;
      context.lineWidth = 2;
      context.stroke();
      phase += 0.035;
    }
    buttons.forEach((button, index) =>
      button.addEventListener("click", () => select(index)),
    );
    window.addEventListener("resize", () => {
      field = sizeCanvas(canvas);
    });
    select(0);
    animateWhenVisible(canvas, draw);
  }

  function renderOperations() {
    const services = [
      { name: "Foundation", port: 8000, online: true },
      { name: "Forge", port: 8010, online: true },
      { name: "Mycelium", port: 8030, online: false },
    ];
    host.innerHTML =
      '<div class="ops-grid">' +
      services
        .map(
          (service, index) =>
            '<button class="ops-service" type="button" data-service="' +
            index +
            '"><i></i><span>' +
            service.name +
            "</span><small>:" +
            service.port +
            "</small></button>",
        )
        .join("") +
      '</div><div class="ops-console"><div><span data-ops-name></span><strong data-ops-state></strong><small data-ops-latency>aguardando probe</small></div><button class="instrument-action" type="button" data-probe>Executar probe <span>↗</span></button><button class="instrument-quiet" type="button" data-toggle></button></div>';
    const cards = [...host.querySelectorAll(".ops-service")],
      name = host.querySelector("[data-ops-name]"),
      state = host.querySelector("[data-ops-state]"),
      latency = host.querySelector("[data-ops-latency]"),
      probe = host.querySelector("[data-probe]"),
      toggle = host.querySelector("[data-toggle]");
    let active = 0,
      probes = 0;
    function render() {
      const service = services[active];
      cards.forEach((card, index) => {
        card.classList.toggle("active", index === active);
        card.classList.toggle("online", services[index].online);
      });
      name.textContent = service.name;
      state.textContent = service.online ? "ONLINE" : "STOPPED";
      toggle.textContent = service.online
        ? "Parar simulação"
        : "Iniciar simulação";
      status.textContent =
        service.name.toUpperCase() + " · " + state.textContent;
    }
    cards.forEach((card, index) =>
      card.addEventListener("click", () => {
        active = index;
        latency.textContent = "aguardando probe";
        render();
      }),
    );
    toggle.addEventListener("click", () => {
      services[active].online = !services[active].online;
      latency.textContent = "estado local alterado";
      render();
    });
    probe.addEventListener("click", () => {
      probe.disabled = true;
      latency.textContent = "probing…";
      setTimeout(() => {
        probes += 1;
        latency.textContent = services[active].online
          ? 11 + active * 7 + (probes % 5) + " ms · reachable"
          : "timeout · unavailable";
        probe.disabled = false;
      }, 620);
    });
    render();
  }

  function renderCouncil() {
    const voices = [
      {
        name: "Melchior",
        role: "Estrutura",
        copy: "Contratos mínimos antes de expandir a malha.",
      },
      {
        name: "Balthasar",
        role: "Exploração",
        copy: "Um protótipo reversível pode revelar novas superfícies.",
      },
      {
        name: "Casper",
        role: "Clareza",
        copy: "A interação precisa explicar limites sem interromper o fluxo.",
      },
    ];
    host.innerHTML =
      '<div class="council-orbit">' +
      voices
        .map(
          (voice, index) =>
            '<button type="button" class="council-voice" data-voice="' +
            index +
            '"><i>' +
            voice.name[0] +
            "</i><strong>" +
            voice.name +
            "</strong><span>" +
            voice.role +
            "</span></button>",
        )
        .join("") +
      '<div class="council-center"><span>SÍNTESE</span><p data-synthesis></p></div></div><button class="instrument-action council-next" type="button">Rotacionar foco <span>→</span></button>';
    const buttons = [...host.querySelectorAll("[data-voice]")],
      synthesis = host.querySelector("[data-synthesis]"),
      next = host.querySelector(".council-next");
    let active = 0;
    function select(index) {
      active = index;
      buttons.forEach((button, position) =>
        button.classList.toggle("active", position === index),
      );
      synthesis.textContent = voices[index].copy;
      status.textContent =
        voices[index].name.toUpperCase() +
        " · " +
        voices[index].role.toUpperCase();
    }
    buttons.forEach((button, index) =>
      button.addEventListener("click", () => select(index)),
    );
    next.addEventListener("click", () => select((active + 1) % voices.length));
    select(0);
  }

  function renderBalance() {
    host.innerHTML =
      '<div class="balance-controls"><label><span>CHAOS / exploração</span><input type="range" min="0" max="100" value="68" data-chaos /><strong data-chaos-value>68</strong></label><label><span>LAW / política</span><input type="range" min="0" max="100" value="82" data-law /><strong data-law-value>82</strong></label></div><div class="equilibrium-gauge"><div class="gauge-arc"><i data-needle></i><span>CHAOS</span><span>LAW</span></div><strong data-decision></strong><p data-condition></p></div>';
    const chaos = host.querySelector("[data-chaos]"),
      law = host.querySelector("[data-law]"),
      chaosValue = host.querySelector("[data-chaos-value]"),
      lawValue = host.querySelector("[data-law-value]"),
      needle = host.querySelector("[data-needle]"),
      decision = host.querySelector("[data-decision]"),
      condition = host.querySelector("[data-condition]");
    function update() {
      const c = Number(chaos.value),
        l = Number(law.value),
        balance = (c - l + 100) / 2;
      chaosValue.textContent = c;
      lawValue.textContent = l;
      needle.style.transform = "rotate(" + (-65 + balance * 1.3) + "deg)";
      if (Math.abs(c - l) < 15) {
        decision.textContent = "EXPERIMENTO CONTROLADO";
        condition.textContent =
          "Avançar com revisão humana e escopo reversível.";
      } else if (c > l) {
        decision.textContent = "EXPLORAÇÃO CONDICIONAL";
        condition.textContent = "Ampliar alternativas antes de escolher.";
      } else {
        decision.textContent = "POLÍTICA BLOQUEANTE";
        condition.textContent =
          "Resolver a fronteira de confiança antes de avançar.";
      }
      status.textContent =
        "EQUILIBRIUM · " + Math.round(100 - Math.abs(c - l)) + "%";
    }
    chaos.addEventListener("input", update);
    law.addEventListener("input", update);
    update();
  }

  function renderProfile() {
    host.innerHTML =
      '<div class="profile-card"><div class="profile-avatar"><span>EL</span><i></i></div><div><span>PERFIL LOCAL</span><strong>Elric</strong><small data-profile-context>desktop · syzygy</small></div></div><div class="context-chips"><button type="button" class="active" data-context="desktop · syzygy">Desenvolvimento</button><button type="button" data-context="notebook · leitura">Leitura</button><button type="button" data-context="phone · mobilidade">Mobilidade</button></div><div class="preference-list"><button type="button" aria-pressed="true"><span>Histórico local</span><i></i></button><button type="button" aria-pressed="false"><span>Contexto entre dispositivos</span><i></i></button><button type="button" aria-pressed="true"><span>Personalização consentida</span><i></i></button></div>';
    const context = host.querySelector("[data-profile-context]"),
      chips = [...host.querySelectorAll("[data-context]")],
      toggles = [...host.querySelectorAll(".preference-list button")];
    chips.forEach((chip) =>
      chip.addEventListener("click", () => {
        chips.forEach((item) => item.classList.toggle("active", item === chip));
        context.textContent = chip.dataset.context;
        status.textContent = "CONTEXTO · " + chip.textContent.toUpperCase();
      }),
    );
    toggles.forEach((toggle) =>
      toggle.addEventListener("click", () => {
        const pressed = toggle.getAttribute("aria-pressed") !== "true";
        toggle.setAttribute("aria-pressed", String(pressed));
        status.textContent =
          toggle.querySelector("span").textContent.toUpperCase() +
          " · " +
          (pressed ? "ON" : "OFF");
      }),
    );
    status.textContent = "PERFIL · LOCAL";
  }

  function renderWorkspace() {
    const views = {
      editor:
        '<div class="fake-editor"><aside>01<br>02<br>03<br>04</aside><pre><b># SYZYGY</b>\n\nPlataforma pessoal\nlocal-first<span></span></pre></div>',
      terminal:
        '<div class="fake-terminal"><span>PS syzygy&gt;</span> site/start-site.ps1<br><i>preview ready on :8080</i><br><span>PS syzygy&gt;</span> _</div>',
      explorer:
        '<div class="fake-explorer"><strong>SYZYGY</strong><span>▾ foundation</span><span>▾ forge</span><span>▾ mycelium</span><span>▾ site</span><small>12 módulos · local</small></div>',
    };
    host.innerHTML =
      '<div class="workspace-frame"><nav><button type="button" class="active" data-app="editor">Editor</button><button type="button" data-app="terminal">Terminal</button><button type="button" data-app="explorer">Explorer</button></nav><div class="workspace-view" data-workspace-view></div></div>';
    const buttons = [...host.querySelectorAll("[data-app]")],
      view = host.querySelector("[data-workspace-view]");
    function select(app) {
      buttons.forEach((button) =>
        button.classList.toggle("active", button.dataset.app === app),
      );
      view.innerHTML = views[app];
      status.textContent = "APP · " + app.toUpperCase();
    }
    buttons.forEach((button) =>
      button.addEventListener("click", () => select(button.dataset.app)),
    );
    select("editor");
  }

  const renderers = {
    foundation: renderFlow,
    forge: renderFlow,
    mycelium: renderNetwork,
    observatory: renderTelemetry,
    nerv: renderOperations,
    tungsten: renderFlow,
    coppermind: renderNetwork,
    magi: renderCouncil,
    balance: renderBalance,
    elric: renderProfile,
    imrryr: renderWorkspace,
    bastion: renderFlow,
  };
  renderers[key]();
  if (location.hash === "#demo") {
    section
      .querySelectorAll(".reveal")
      .forEach((element) => element.classList.add("visible"));
    section.scrollIntoView({ block: "start", behavior: "auto" });
    requestAnimationFrame(() =>
      requestAnimationFrame(() =>
        section.scrollIntoView({ block: "start", behavior: "auto" }),
      ),
    );
  }
}

function addCardInteractions() {
  document.querySelectorAll(".principle-grid article").forEach((card) =>
    card.addEventListener("pointermove", (event) => {
      const rect = card.getBoundingClientRect();
      card.style.setProperty("--spot-x", `${event.clientX - rect.left}px`);
      card.style.setProperty("--spot-y", `${event.clientY - rect.top}px`);
    }),
  );
  document.querySelectorAll(".module-card,.capability-card").forEach((card) =>
    card.addEventListener("pointermove", (event) => {
      const rect = card.getBoundingClientRect(),
        x = event.clientX - rect.left,
        y = event.clientY - rect.top;
      card.style.setProperty("--card-x", `${x}px`);
      card.style.setProperty("--card-y", `${y}px`);
      if (!reducedMotion) {
        const rx = (0.5 - y / rect.height) * 2.2,
          ry = (x / rect.width - 0.5) * 2.2;
        card.style.transform = `perspective(800px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-5px)`;
      }
    }),
  );
  document.querySelectorAll(".module-card,.capability-card").forEach((card) =>
    card.addEventListener("pointerleave", () => {
      card.style.transform = "";
    }),
  );
}

function addNavigation() {
  const toggle = document.querySelector(".menu-toggle"),
    links = document.querySelector(".nav-links"),
    nav = document.querySelector(".nav"),
    progress = document.querySelector(".reading-progress span");
  const toggleText = toggle?.querySelector(".sr-only");
  const setMenuOpen = (open) => {
    links?.classList.toggle("open", open);
    toggle?.setAttribute("aria-expanded", String(open));
    if (toggleText)
      toggleText.textContent = open ? "Fechar menu" : "Abrir menu";
  };
  toggle?.addEventListener("click", () =>
    setMenuOpen(!links.classList.contains("open")),
  );
  links
    ?.querySelectorAll("a")
    .forEach((link) =>
      link.addEventListener("click", () => setMenuOpen(false)),
    );
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setMenuOpen(false);
  });
  document.addEventListener("pointerdown", (event) => {
    if (nav && !nav.contains(event.target)) setMenuOpen(false);
  });
  const updateScroll = () => {
    const top = window.scrollY,
      total = document.documentElement.scrollHeight - window.innerHeight;
    nav?.classList.toggle("scrolled", top > 24);
    if (progress)
      progress.style.width = `${total > 0 ? Math.min(100, (top / total) * 100) : 0}%`;
  };
  window.addEventListener("scroll", updateScroll, { passive: true });
  updateScroll();
  const year = document.getElementById("current-year");
  if (year) year.textContent = String(new Date().getFullYear());
}

createHeroField();
createMedusaeField();
createModuleField();
createMyceliumField();
createModuleIdentity();
createModuleDemo();
addCardInteractions();
addNavigation();
const observer = new IntersectionObserver(
  (entries) =>
    entries.forEach((entry) => {
      if (entry.isIntersecting) entry.target.classList.add("visible");
    }),
  { threshold: 0.16 },
);
document
  .querySelectorAll(".reveal")
  .forEach((element) => observer.observe(element));
document.documentElement.classList.add("js");
