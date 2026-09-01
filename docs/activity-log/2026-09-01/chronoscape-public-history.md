# Public Chronoscape History

## Context

An offline prototype introduced Chronoscape: an isometric reading of SYZYGY's
Git history. Its central visual idea is useful for the institutional site, but
the prototype carried full commit details, including author names, subjects,
hashes, and changed-file paths. Those details conflict with the existing public
site boundary for Git-derived data.

## Decision

Add Chronoscape as a project-level institutional page at
`site/chronoscape.html`. It remains a static, historical visualization and not
a new official module, a NERV operational surface, or an Observatory dashboard.

## Changed

- Added a responsive Canvas 2D isometric terrain with commits, churn, reach,
  and documented-state layers.
- Added anonymous historical stratum selection, aggregate charts, rotation,
  and zoom controls.
- Extended the site build to generate a privacy-preserving 365-day snapshot,
  capped at 120 strata.
- Linked the page from the existing home terrain and added it to the sitemap.
- Added checks for the public-page metadata, static assets, and the
  non-identifying historical data boundary.

## Scope Boundary

- The artifact contains no author identity, e-mail address, commit message,
  hash, parent relationship, changed-file path, or working-tree data.
- The `site`, `docs`, and `root` labels are repository support sectors, not
  official SYZYGY modules.
- Chronoscape does not inspect services, devices, events, health, or runtime
  state. Those concerns remain with the appropriate module contracts.
- Decorative WebGL and the prototype's per-file manifest were intentionally
  not adopted; Canvas 2D and aggregate data meet the institutional need with a
  smaller, more compatible public artifact.

## Validation

- `npm --prefix site run check`
- `npm --prefix site run build`
- local preview checks for the public page, snapshot, and unknown route
- desktop and mobile headless-browser review
