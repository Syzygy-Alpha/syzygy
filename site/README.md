# SYZYGY institutional site

Public, project-level presentation of the SYZYGY platform. It explains the
vision, architectural principles, current modules, declared future portfolio,
and roadmap without redefining the technical contracts documented in `docs/`
and in each module README.

The site belongs at repository level because it represents the whole ecosystem.
It is not a NERV operational surface or an Imrryr application. GitHub Pages is
an optional publishing extension; the source and preview remain fully local.

## Runtime and privacy

The published site uses semantic HTML, local CSS, Canvas 2D, and vanilla
JavaScript. It has no frontend framework, analytics, cookies, remote fonts,
CDNs, or runtime API calls. The Node.js scripts are development utilities only:
the Pages artifact is static and has no server-side runtime.

## Requirements

- Node.js 22 or newer for checks, packaging, and the local preview;
- PowerShell only if using the Windows launcher.

No `npm install` step is required because the project has no package
dependencies.

## Local preview

From the repository root:

```powershell
.\site\start-site.ps1
```

To avoid opening the browser automatically or to select another port:

```powershell
.\site\start-site.ps1 -NoBrowser -Port 8081
```

The cross-platform command is:

```bash
npm --prefix site run preview -- --port 8080
```

The preview rebuilds `site/dist/`, binds to `127.0.0.1` by default, exposes only
the public artifact, serves no directory listings, and provides `GET /health`
for launcher diagnostics.

## Quality and build

```bash
npm --prefix site run check
npm --prefix site run build
```

`check` validates JavaScript syntax, page metadata, local links and fragments,
accessibility invariants, sitemap coverage, all twelve module pages, and the
boundary between functional and future modules. `build` copies only public
assets to the ignored `site/dist/` directory.

## Visual themes

The default direction is **Eclipse Bloom**. Two preserved review variants are
available without changing stored state:

- `?theme=orbital` selects Orbital Cartography;
- `?theme=clean` selects the original clean baseline.

All themes use local system fonts and respect `prefers-reduced-motion`.

## GitHub Pages

The path-scoped workflow in `.github/workflows/site-pages.yml` performs the
same checks and build on pull requests. Pushes to `main` package `site/dist/`
and deploy it through the protected `github-pages` environment.

One repository setting must be enabled by an administrator before the first
deployment:

1. open **Settings → Pages**;
2. under **Build and deployment**, select **GitHub Actions** as the source.

The expected project URL is:

```text
https://syzygy-alpha.github.io/syzygy/
```

Relative asset and navigation URLs keep the site compatible with the `/syzygy/`
project subpath. A custom domain can be added later through repository settings;
it is not required by the site.

## Content boundaries

The functional v0.1 pages are Foundation, Forge, Mycelium, Observatory, and
NERV. Tungsten, Coppermind, MAGI, Balance, Elric, Imrryr, and Bastion are
explicitly labeled as conceptual and not implemented.

When module status changes, update together:

1. canonical documentation under `docs/` and the module README;
2. home-page status and roadmap copy;
3. the corresponding module page;
4. `sitemap.xml` only when adding or removing a public page;
5. the site checks if the current/future boundary changes.
