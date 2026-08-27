# Institutional Site Review and GitHub Pages

## Context

The local institutional site presented the whole SYZYGY portfolio, but arrived
under a duplicated `site/site/` path together with generated browser profiles,
preview images, and runtime logs. It had no automated validation or publishing
workflow, and several source files were difficult to review because most markup
and styles were compressed into long lines.

## Decision

Keep the site as a project-level static presentation under `site/`. It is not a
new official module, a NERV operational surface, or an Imrryr internal app. The
optional GitHub Pages publication is a delivery concern and does not become a
runtime dependency for the local-first platform.

## Changed

- Flattened the source to `site/` and removed untracked Edge profiles, caches,
  logs, and generated previews.
- Preserved all twelve official module narratives while enforcing the boundary
  between five functional v0.1 modules and seven future concepts.
- Corrected broad stack and openness claims, added canonical/social metadata,
  favicon, sitemap, robots policy, and a custom 404 page.
- Improved keyboard semantics, navigation labels, external-link isolation,
  progressive enhancement, focus visibility, and reduced-motion behavior.
- Paused Canvas animation outside the viewport or while the document is hidden,
  reduced particle work, and lowered the high-DPI Canvas memory ceiling.
- Added dependency-free Node.js checks, an explicit public-asset build, and a
  safe local preview server.
- Added a path-scoped GitHub Actions workflow that validates pull requests and
  deploys `main` to the `github-pages` environment.

## Scope Boundary

- No analytics, cookies, remote fonts, CDN, SaaS runtime, custom domain, or new
  module contract was introduced.
- GitHub Pages remains optional; source review and local preview work without it.
- Canonical technical detail remains in `docs/` and module READMEs.
- Enabling GitHub Actions as the Pages source is a one-time repository setting,
  not a change that can be represented in source control.

## Validation

- `npm --prefix site run check`
- `npm --prefix site run build`
- local preview health, 404, and static-asset requests
- desktop and mobile headless-browser review
- `git diff --check`
