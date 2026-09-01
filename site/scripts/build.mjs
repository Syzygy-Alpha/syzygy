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
const chronoscapeWindowDays = 365;
const chronoscapeMaximumCommits = 120;
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
  "chronoscape.css",
  "chronoscape.html",
  "chronoscape.js",
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

function chronoscapeSectorForPath(filePath) {
  const normalized = filePath.replaceAll("\\", "/").replace(/^\.\//, "");
  const [root = ""] = normalized.split("/", 1);
  const lowerRoot = root.toLocaleLowerCase("en-US");
  if (officialModules.includes(lowerRoot)) return lowerRoot;
  if (lowerRoot === "site") return "site";
  if (
    lowerRoot === "docs" ||
    /^(?:agents|readme|contributing)(?:\.[^.]+)?$/i.test(root)
  ) {
    return "docs";
  }
  return "root";
}

function parseChronoscapeHistory(output) {
  return output
    .split("\x1e")
    .map((record) => record.trim())
    .filter(Boolean)
    .map((record) => {
      const [authoredAt, ...lines] = record.split(/\r?\n/);
      const sectors = {};
      let additions = 0;
      let deletions = 0;
      let files = 0;
      for (const line of lines) {
        const match = /^(\d+|-)\t(\d+|-)\t(.+)$/.exec(line.trim());
        if (!match) continue;
        const binary = match[1] === "-" || match[2] === "-";
        const added = binary ? 0 : Number.parseInt(match[1], 10);
        const removed = binary ? 0 : Number.parseInt(match[2], 10);
        const sector = chronoscapeSectorForPath(match[3]);
        const aggregate = sectors[sector] ?? {
          files: 0,
          additions: 0,
          deletions: 0,
        };
        aggregate.files += 1;
        aggregate.additions += added;
        aggregate.deletions += removed;
        sectors[sector] = aggregate;
        files += 1;
        additions += added;
        deletions += removed;
      }
      return {
        date: authoredAt.slice(0, 10),
        stats: { files, additions, deletions },
        sectors,
      };
    });
}

async function createChronoscapeSnapshot() {
  const unavailable = {
    schemaVersion: 1,
    available: false,
    windowDays: chronoscapeWindowDays,
    range: { firstDate: null, lastDate: null, dayCount: 0, commitCount: 0 },
    commits: [],
  };
  try {
    const [revision, revisionAt] = await Promise.all([
      git(["rev-parse", "--short=12", "HEAD"]),
      git(["log", "-1", "--format=%cI", "HEAD"]),
    ]);
    if (!revision || !revisionAt) return unavailable;
    const windowStart = new Date(
      new Date(revisionAt).getTime() -
        chronoscapeWindowDays * 24 * 60 * 60 * 1000,
    ).toISOString();
    const history = await git([
      "log",
      "--reverse",
      "--no-renames",
      "--date=iso-strict",
      "--format=%x1e%aI",
      "--numstat",
      `--since=${windowStart}`,
      "HEAD",
      "--",
      ".",
    ]);
    const commits = parseChronoscapeHistory(history).slice(-chronoscapeMaximumCommits);
    if (!commits.length) return unavailable;
    const firstDate = commits[0].date;
    const lastDate = commits.at(-1).date;
    const dayCount = Math.max(
      1,
      Math.round(
        (new Date(`${lastDate}T12:00:00Z`) -
          new Date(`${firstDate}T12:00:00Z`)) /
          (24 * 60 * 60 * 1000),
      ) + 1,
    );
    return {
      schemaVersion: 1,
      available: true,
      windowDays: chronoscapeWindowDays,
      range: {
        firstDate,
        lastDate,
        dayCount,
        commitCount: commits.length,
      },
      commits,
    };
  } catch {
    console.warn(
      "Git history is unavailable; building Chronoscape without historical data.",
    );
    return unavailable;
  }
}

const chronoscapeSnapshot = await createChronoscapeSnapshot();
await writeFile(
  path.join(outputRoot, "chronoscape-snapshot.json"),
  `${JSON.stringify(chronoscapeSnapshot)}\n`,
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
