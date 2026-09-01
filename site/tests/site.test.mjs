import assert from "node:assert/strict";
import { access, readFile, readdir, stat } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const testDirectory = path.dirname(fileURLToPath(import.meta.url));
const siteRoot = path.resolve(testDirectory, "..");
const baseUrl = "https://syzygy-alpha.github.io/syzygy/";
const functionalModules = [
  "foundation",
  "forge",
  "mycelium",
  "observatory",
  "nerv",
];
const futureModules = [
  "tungsten",
  "coppermind",
  "magi",
  "balance",
  "elric",
  "imrryr",
  "bastion",
];
const officialModules = [...functionalModules, ...futureModules];
const contentFiles = [
  path.join(siteRoot, "index.html"),
  path.join(siteRoot, "chronoscape.html"),
  ...officialModules.map((name) =>
    path.join(siteRoot, "modules", `${name}.html`),
  ),
];
const htmlFiles = [...contentFiles, path.join(siteRoot, "404.html")];

const htmlByFile = new Map(
  await Promise.all(
    htmlFiles.map(async (file) => [file, await readFile(file, "utf8")]),
  ),
);

function occurrences(source, pattern) {
  return [...source.matchAll(pattern)].length;
}

function escapeRegularExpression(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

test("all official module pages are present", async () => {
  const moduleFiles = (await readdir(path.join(siteRoot, "modules")))
    .filter((name) => name.endsWith(".html"))
    .sort();
  assert.deepEqual(
    moduleFiles,
    officialModules.map((name) => `${name}.html`).sort(),
  );
});

test("GitHub Pages artifact bypasses Jekyll processing", async () => {
  await access(path.join(siteRoot, ".nojekyll"));
});

test("content pages expose semantic and social metadata", () => {
  for (const file of contentFiles) {
    const source = htmlByFile.get(file);
    const relative = path.relative(siteRoot, file).replaceAll("\\", "/");
    const expectedCanonical =
      relative === "index.html" ? baseUrl : `${baseUrl}${relative}`;

    assert.match(source, /^<!doctype html>/i, `${relative}: missing doctype`);
    assert.match(
      source,
      /<html lang="pt-BR">/,
      `${relative}: incorrect language`,
    );
    assert.equal(
      occurrences(source, /<main(?:\s|>)/g),
      1,
      `${relative}: expected one main`,
    );
    assert.equal(
      occurrences(source, /<h1(?:\s|>)/g),
      1,
      `${relative}: expected one h1`,
    );
    assert.match(source, /<title>[^<]+<\/title>/, `${relative}: missing title`);
    assert.match(
      source,
      /<meta\s+name="description"\s+content="[^"]+"\s*\/?>/s,
      `${relative}: missing description`,
    );
    assert.match(
      source,
      /<meta\s+property="og:description"\s+content="[^"]+"\s*\/?>/s,
      `${relative}: missing Open Graph description`,
    );
    const canonicalUrl = escapeRegularExpression(expectedCanonical);
    assert.match(
      source,
      new RegExp(`<link\\s+rel="canonical"\\s+href="${canonicalUrl}"`),
      `${relative}: bad canonical URL`,
    );
    assert.match(
      source,
      new RegExp(`<meta\\s+property="og:url"\\s+content="${canonicalUrl}"`),
      `${relative}: bad Open Graph URL`,
    );
    assert.match(
      source,
      /<link rel="icon" href="[^"]+favicon\.svg"/,
      `${relative}: missing favicon`,
    );
  }
});

test("module status copy preserves current and future boundaries", () => {
  for (const name of functionalModules) {
    const source = htmlByFile.get(
      path.join(siteRoot, "modules", `${name}.html`),
    );
    assert.ok(
      source.includes("FUNCIONAL · v0.1"),
      `${name}: missing functional status`,
    );
    assert.ok(
      !source.includes("CONCEITO · FUTURO"),
      `${name}: incorrectly marked future`,
    );
  }
  for (const name of futureModules) {
    const source = htmlByFile.get(
      path.join(siteRoot, "modules", `${name}.html`),
    );
    assert.ok(
      source.includes("CONCEITO · FUTURO"),
      `${name}: missing future status`,
    );
    assert.ok(
      source.includes("Não implementado"),
      `${name}: missing implementation boundary`,
    );
  }
});

test("HTML interactions have accessible structure", () => {
  for (const file of htmlFiles) {
    const source = htmlByFile.get(file);
    const relative = path.relative(siteRoot, file);
    const ids = [...source.matchAll(/\sid="([^"]+)"/g)].map(
      (match) => match[1],
    );
    assert.equal(new Set(ids).size, ids.length, `${relative}: duplicate id`);

    for (const match of source.matchAll(/<a\b[^>]*target="_blank"[^>]*>/gs)) {
      assert.match(
        match[0],
        /rel="[^"]*noopener[^"]*"/,
        `${relative}: missing noopener`,
      );
      assert.match(
        match[0],
        /rel="[^"]*noreferrer[^"]*"/,
        `${relative}: missing noreferrer`,
      );
    }
    for (const match of source.matchAll(/<button\b[^>]*>/gs)) {
      assert.match(
        match[0],
        /\stype="button"/,
        `${relative}: button without explicit type`,
      );
    }
    for (const match of source.matchAll(/<canvas\b[^>]*>/gs)) {
      assert.match(
        match[0],
        /\saria-(?:hidden|label)=/,
        `${relative}: inaccessible canvas`,
      );
    }
    for (const match of source.matchAll(/aria-controls="([^"]+)"/g)) {
      assert.ok(
        ids.includes(match[1]),
        `${relative}: aria-controls target does not exist`,
      );
    }
  }

  for (const name of officialModules) {
    const source = htmlByFile.get(
      path.join(siteRoot, "modules", `${name}.html`),
    );
    assert.match(
      source,
      /class="module-identity"[\s\S]*?role="button"/,
      `${name}: identity is not keyboard actionable`,
    );
    assert.match(
      source,
      /<nav class="nav" aria-label="Navegação principal">/,
      `${name}: main nav lacks a label`,
    );
    assert.match(
      source,
      /class="module-pagination"\s+aria-label="Navegação entre módulos"/,
      `${name}: pagination lacks a label`,
    );
  }
});

test("all local HTML and CSS references resolve within the site", async () => {
  for (const file of htmlFiles) {
    const source = htmlByFile.get(file);
    for (const match of source.matchAll(/\s(?:href|src)="([^"]+)"/g)) {
      const reference = match[1];
      if (/^(?:https?:|mailto:|tel:|data:)/.test(reference)) continue;
      assert.ok(
        !reference.startsWith("/"),
        `${reference}: root-relative links break project Pages`,
      );

      const [fileReference, fragment] = reference.split("#", 2);
      const target = fileReference
        ? path.resolve(path.dirname(file), fileReference.split("?", 1)[0])
        : file;
      await access(target);
      if (fragment) {
        const targetSource =
          htmlByFile.get(target) ?? (await readFile(target, "utf8"));
        const idPattern = new RegExp(
          `\\sid="${escapeRegularExpression(decodeURIComponent(fragment))}"`,
        );
        assert.match(
          targetSource,
          idPattern,
          `${reference}: fragment target does not exist`,
        );
      }
    }
  }

  const cssFiles = [
    "chronoscape.css",
    "site.css",
    "module-page.css",
    "syzygy-theme.css",
    "syzygy-theme-bold.css",
  ];
  for (const name of cssFiles) {
    const file = path.join(siteRoot, name);
    const source = await readFile(file, "utf8");
    for (const match of source.matchAll(/url\(["']?([^"')]+)["']?\)/g)) {
      const reference = match[1];
      if (/^(?:data:|https?:|#)/.test(reference)) continue;
      await access(path.resolve(path.dirname(file), reference));
    }
  }
});

test("home page and sitemap enumerate the complete module portfolio", async () => {
  const home = htmlByFile.get(path.join(siteRoot, "index.html"));
  for (const name of officialModules) {
    assert.ok(home.includes(`./modules/${name}.html`), `home: missing ${name}`);
  }

  const sitemap = await readFile(path.join(siteRoot, "sitemap.xml"), "utf8");
  const locations = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)]
    .map((match) => match[1])
    .sort();
  const expected = [
    baseUrl,
    `${baseUrl}chronoscape.html`,
    ...officialModules.map((name) => `${baseUrl}modules/${name}.html`),
  ].sort();
  assert.deepEqual(locations, expected);
});

test("ecosystem terrain preserves modules, layers, and static data boundary", async () => {
  const home = htmlByFile.get(path.join(siteRoot, "index.html"));
  const layerControls = [
    ...home.matchAll(
      /<button\b(?=[^>]*data-terrain-layer="([^"]+)")[^>]*>/gs,
    ),
  ];
  const layers = layerControls.map((match) => match[1]);
  assert.deepEqual(layers, ["architecture", "state", "activity"]);
  assert.equal(
    layerControls.filter((match) => match[0].includes('aria-pressed="true"'))
      .length,
    1,
    "terrain: expected one initially selected layer",
  );

  const moduleControls = [
    ...home.matchAll(
      /<button\b(?=[^>]*data-terrain-module="([^"]+)")[^>]*>/gs,
    ),
  ];
  const terrainModules = moduleControls.map((match) => match[1]);
  assert.deepEqual(
    terrainModules.sort(),
    [...officialModules].sort(),
    "terrain: module controls must match the official portfolio",
  );
  assert.equal(
    moduleControls.filter((match) => match[0].includes('aria-pressed="true"'))
      .length,
    1,
    "terrain: expected one initially selected module",
  );
  assert.match(
    home,
    /dados operacionais em tempo real continuam pertencendo ao NERV/,
    "terrain: missing institutional/NERV boundary",
  );

  const terrainScript = await readFile(path.join(siteRoot, "terrain.js"), "utf8");
  assert.match(terrainScript, /function createTerrainMap\(\)/);
  assert.match(terrainScript, /new Float32Array\(/);
  assert.match(terrainScript, /fetch\("\.\/ecosystem-snapshot\.json"/);
  assert.match(terrainScript, /button\.setAttribute\("aria-pressed"/);

  const buildScript = await readFile(
    path.join(siteRoot, "scripts", "build.mjs"),
    "utf8",
  );
  assert.match(buildScript, /"terrain\.js"/);
  assert.match(buildScript, /"ecosystem-snapshot\.json"/);
});

test("Chronoscape remains an aggregated historical site page", async () => {
  const chronoscape = htmlByFile.get(path.join(siteRoot, "chronoscape.html"));
  const script = await readFile(path.join(siteRoot, "chronoscape.js"), "utf8");
  const buildScript = await readFile(
    path.join(siteRoot, "scripts", "build.mjs"),
    "utf8",
  );
  for (const layer of ["commits", "churn", "footprint", "state"]) {
    assert.match(
      chronoscape,
      new RegExp(`data-chrono-layer="${layer}"`),
      `Chronoscape: missing ${layer} layer`,
    );
  }
  for (const identifier of [
    "chronoscape-terrain",
    "velocity-chart",
    "churn-chart",
    "distribution-chart",
    "chrono-range",
    "chrono-sector",
  ]) {
    assert.match(
      chronoscape,
      new RegExp(`id="${identifier}"`),
      `Chronoscape: missing ${identifier}`,
    );
  }
  assert.match(
    chronoscape,
    /não inclui autoria, mensagens de commit, hashes ou caminhos de arquivos/,
    "Chronoscape: missing public data boundary",
  );
  assert.match(script, /function drawTerrain\(\)/);
  assert.match(script, /fetch\("\.\/chronoscape-snapshot\.json"/);
  assert.doesNotMatch(script, /commit\.(?:author|subject|hash|shortHash|files)/);
  assert.match(buildScript, /"chronoscape\.html"/);
  assert.match(buildScript, /"chronoscape-snapshot\.json"/);
  assert.match(buildScript, /chronoscapeMaximumCommits = 120/);
  assert.doesNotMatch(buildScript, /author:\s/);
  assert.doesNotMatch(buildScript, /subject:\s/);
  assert.doesNotMatch(buildScript, /path:\s/);
});

test("generated browser state is not part of the source tree", async () => {
  async function inspect(directory, relative = "") {
    for (const entry of await readdir(directory, { withFileTypes: true })) {
      if (!relative && [".tmp", "dist"].includes(entry.name)) continue;
      assert.ok(
        !entry.name.startsWith(".edge-"),
        `forbidden browser profile: ${entry.name}`,
      );
      assert.ok(
        !entry.name.startsWith(".preview-"),
        `forbidden generated preview: ${entry.name}`,
      );
      assert.notEqual(entry.name, ".runtime-logs", "forbidden runtime logs");
      if (entry.isDirectory())
        await inspect(
          path.join(directory, entry.name),
          path.join(relative, entry.name),
        );
    }
  }
  await inspect(siteRoot);
});

test("public source stays inside the static performance budget", async () => {
  const publicFiles = [
    ".nojekyll",
    "404.html",
    "chronoscape.css",
    "chronoscape.html",
    "chronoscape.js",
    "favicon.svg",
    "index.html",
    "module-page.css",
    "robots.txt",
    "site.css",
    "site.js",
    "terrain.js",
    "sitemap.xml",
    "syzygy-theme-bold.css",
    "syzygy-theme.css",
    ...officialModules.map((name) => path.join("modules", `${name}.html`)),
  ];
  let totalBytes = 0;
  for (const relative of publicFiles) {
    const metadata = await stat(path.join(siteRoot, relative));
    assert.ok(
      metadata.size <= 100 * 1024,
      `${relative}: exceeds the 100 KiB per-file budget`,
    );
    totalBytes += metadata.size;
  }
  assert.ok(
    totalBytes <= 450 * 1024,
    `public source exceeds 450 KiB (${totalBytes} bytes)`,
  );
});
