# SYZYGY institutional site

Public, project-level presentation of the SYZYGY platform. It explains the
vision, architectural principles, current modules, declared future portfolio,
and roadmap without redefining the technical contracts documented in `docs/`
and in each module README.

The site belongs at repository level because it represents the whole ecosystem.
It is not a NERV operational surface or an Imrryr application. GitHub Pages is
an optional publishing extension; the source and preview remain fully local.

## Runtime and privacy

The published site uses semantic HTML, local CSS, Canvas 2D, vanilla
JavaScript, and an optional local WebGL particle field with a Canvas 2D
fallback. It has no frontend framework, analytics, cookies, remote fonts,
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

## Adaptive rendering

Canvas and Medusae animations automatically use a lighter profile on devices
reporting up to 4 GB of memory or up to four logical processors. The lighter
profile caps animation at 30 FPS, renders canvases at 1x pixel density, reduces
ambient Hero and Mycelium particle counts, samples fewer Mycelium links, and
uses a smaller Medusae field. The module-logo field preserves a higher particle
density, uses tighter shape targets, and batches Canvas drawing operations so
every symbol remains complete and crisp. Off-screen and background-tab
animations remain paused.

Use `?quality=low` to force the lighter profile or `?quality=high` to override
the hardware heuristic when comparing rendering quality.

## Ecosystem terrain

The home page uses a dependency-free isometric topographic view of the twelve
official modules. `terrain.js` renders a documented implementation-state field
on Canvas 2D and redraws only on a debounced viewport resize. It has no
continuous animation, Git fetch, operational call, or runtime dependency.

Functional v0.1 modules have a high field weight and declared future modules a
low field weight. This is an explanatory status view: proximity does not declare
a direct runtime dependency, and elevation does not infer health or readiness.

The historical layers and charts intentionally remain on Chronoscape. The home
map is therefore always available, including when a historical snapshot cannot
be generated.


## Chronoscape

`chronoscape.html` is a separate public reading of repository evolution. It is
an institutional page, not a NERV dashboard, an Observatory surface, or a new
official module. It renders a dependency-free Canvas 2D isometric terrain,
aggregate charts, and a documented implementation-state layer.

The build derives `chronoscape-snapshot.json` from up to 120 commits in the
365 days preceding the artifact revision. Each stratum includes only its date,
aggregate additions, removals, file count, and aggregate totals per official
module or repository support sector (`site`, `docs`, and `root`). It never
publishes authors, e-mail addresses, commit messages, hashes, parent links,
file paths, or working-tree state. If Git history is unavailable, the page keeps
its static implementation-state terrain visible, disables historical layers,
and labels the missing snapshot instead of inferring data.

The home terrain remains the concise ecosystem overview. Chronoscape is linked
from that section when a visitor needs a deeper historical reading. Both views
are static: they make no operational calls and do not claim live health.

## GitHub Pages

The workflow in `.github/workflows/site-pages.yml` performs the same checks and
build for site-related pull requests. Every push to `main` refreshes the Git
snapshot, packages `site/dist/`, and deploys it through the protected
`github-pages` environment.

One repository setting must be enabled by an administrator before the first
deployment:

1. open **Settings → Pages**;
2. under **Build and deployment**, select **GitHub Actions** as the source.

After changing the source, run the **Institutional site** workflow manually or
push a change under `site/` to create a fresh deployment. The published artifact
contains `.nojekyll`, making the static-site boundary explicit.

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
