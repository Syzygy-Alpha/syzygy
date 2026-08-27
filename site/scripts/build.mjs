import { cp, lstat, mkdir, readdir, rm } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const siteRoot = path.resolve(scriptDirectory, "..");
const outputRoot = path.resolve(siteRoot, "dist");
const publicEntries = [
  "404.html",
  "favicon.svg",
  "index.html",
  "module-page.css",
  "modules",
  "robots.txt",
  "site.css",
  "site.js",
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
