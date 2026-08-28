import { execFile } from "node:child_process";
import { cp, lstat, mkdir, readdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";

const execFileAsync = promisify(execFile);
const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const siteRoot = path.resolve(scriptDirectory, "..");
const repositoryRoot = path.resolve(siteRoot, "..");
const outputRoot = path.resolve(siteRoot, "dist");
const activityWindowDays = 90;
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
const publicEntries = [
  ".nojekyll",
  "404.html",
  "favicon.svg",
  "index.html",
  "module-page.css",
  "modules",
  "robots.txt",
  "site.css",
  "site.js",
  "terrain.js",
  "sitemap.xml",
  "syzygy-theme-bold.css",
  "syzygy-theme.css",
];

if (path.dirname(outputRoot) !== siteRoot) {
  throw new Error(`Refusing to build outside the site root: ${outputRoot}`);
}

for (const entry of publicEntries) {
  const source = path.join(siteRoot, entry);
  const metadata = await lstat(source);
  if (metadata.isSymbolicLink()) {
    throw new Error(`Public entries cannot be symbolic links: ${entry}`);
  }
}

await rm(outputRoot, { recursive: true, force: true });
await mkdir(outputRoot, { recursive: true });

for (const entry of publicEntries) {
  await cp(path.join(siteRoot, entry), path.join(outputRoot, entry), {
    recursive: true,
  });
}

async function git(argumentsList) {
  const { stdout } = await execFileAsync("git", argumentsList, {
    cwd: repositoryRoot,
    encoding: "utf8",
    windowsHide: true,
  });
  return stdout.trim();
}

async function createEcosystemSnapshot() {
  const unavailable = {
    schemaVersion: 1,
    available: false,
    windowDays: activityWindowDays,
    revision: null,
    revisionAt: null,
    modules: Object.fromEntries(officialModules.map((name) => [name, null])),
  };
  try {
    const [revision, revisionAt] = await Promise.all([
      git(["rev-parse", "--short=12", "HEAD"]),
      git(["log", "-1", "--format=%cI", "HEAD"]),
    ]);
    if (!revision || !revisionAt) return unavailable;
    const windowStart = new Date(
      new Date(revisionAt).getTime() - activityWindowDays * 24 * 60 * 60 * 1000,
    ).toISOString();
    const counts = await Promise.all(
      officialModules.map(async (name) => {
        const output = await git([
          "rev-list",
          "--count",
          `--since=${windowStart}`,
          "HEAD",
          "--",
          name,
        ]);
        const count = Number.parseInt(output, 10);
        return [name, Number.isInteger(count) && count >= 0 ? count : 0];
      }),
    );
    return {
      schemaVersion: 1,
      available: true,
      windowDays: activityWindowDays,
      revision,
      revisionAt,
      modules: Object.fromEntries(counts),
    };
  } catch {
    console.warn(
      "Git history is unavailable; building the terrain map without commit activity.",
    );
    return unavailable;
  }
}

const ecosystemSnapshot = await createEcosystemSnapshot();
await writeFile(
  path.join(outputRoot, "ecosystem-snapshot.json"),
  `${JSON.stringify(ecosystemSnapshot, null, 2)}\n`,
  "utf8",
);

async function inventory(directory) {
  let bytes = 0;
  let files = 0;
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      const nested = await inventory(target);
      bytes += nested.bytes;
      files += nested.files;
    } else if (entry.isFile()) {
      const metadata = await lstat(target);
      bytes += metadata.size;
      files += 1;
    }
  }
  return { bytes, files };
}

const result = await inventory(outputRoot);
console.log(
  `Built ${result.files} public files (${(result.bytes / 1024).toFixed(1)} KiB) in site/dist.`,
);
