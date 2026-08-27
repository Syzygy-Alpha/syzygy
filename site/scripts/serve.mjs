import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const sourceRoot = path.resolve(scriptDirectory, "..");
const siteRoot = path.resolve(sourceRoot, "dist");
const argumentsList = process.argv.slice(2);

function readOption(name, fallback) {
  const position = argumentsList.indexOf(name);
  if (position !== -1) return argumentsList[position + 1];
  const inlineOption = argumentsList.find((argument) =>
    argument.startsWith(`${name}=`),
  );
  return inlineOption ? inlineOption.slice(name.length + 1) : fallback;
}

const host = readOption("--host", "127.0.0.1");
const positionalPort = argumentsList.find((argument) => /^\d+$/.test(argument));
const port = Number.parseInt(
  readOption("--port", positionalPort ?? "8080"),
  10,
);
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error("--port must be an integer between 1 and 65535.");
}

const contentTypes = new Map([
  [".css", "text/css; charset=utf-8"],
  [".html", "text/html; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".svg", "image/svg+xml"],
  [".txt", "text/plain; charset=utf-8"],
  [".xml", "application/xml; charset=utf-8"],
]);

function sendFile(request, response, filePath, statusCode = 200) {
  response.writeHead(statusCode, {
    "Cache-Control": "no-store",
    "Content-Type":
      contentTypes.get(path.extname(filePath)) ?? "application/octet-stream",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Content-Type-Options": "nosniff",
  });
  if (request.method === "HEAD") {
    response.end();
    return;
  }
  createReadStream(filePath).pipe(response);
}

const server = http.createServer(async (request, response) => {
  if (request.method !== "GET" && request.method !== "HEAD") {
    response.writeHead(405, { Allow: "GET, HEAD" }).end();
    return;
  }

  const url = new URL(request.url ?? "/", `http://${host}:${port}`);
  if (url.pathname === "/health") {
    const payload = JSON.stringify({
      status: "ok",
      service: "syzygy-site-preview",
    });
    response.writeHead(200, {
      "Cache-Control": "no-store",
      "Content-Type": "application/json; charset=utf-8",
    });
    response.end(request.method === "HEAD" ? undefined : payload);
    return;
  }

  let relativePath;
  try {
    relativePath = decodeURIComponent(
      url.pathname === "/" ? "index.html" : url.pathname.slice(1),
    );
  } catch {
    response.writeHead(400).end("Invalid URL");
    return;
  }

  const requestedFile = path.resolve(siteRoot, relativePath);
  if (
    requestedFile !== siteRoot &&
    !requestedFile.startsWith(`${siteRoot}${path.sep}`)
  ) {
    response.writeHead(403).end("Forbidden");
    return;
  }

  try {
    const metadata = await stat(requestedFile);
    if (!metadata.isFile()) throw new Error("Not a file");
    sendFile(request, response, requestedFile);
  } catch {
    sendFile(request, response, path.join(siteRoot, "404.html"), 404);
  }
});

server.on("error", (error) => {
  console.error(`SYZYGY site preview failed: ${error.message}`);
  process.exitCode = 1;
});

server.listen(port, host, () => {
  console.log(`SYZYGY site ready at http://${host}:${port}/`);
});

process.on("SIGINT", () => server.close(() => process.exit(0)));
process.on("SIGTERM", () => server.close(() => process.exit(0)));
