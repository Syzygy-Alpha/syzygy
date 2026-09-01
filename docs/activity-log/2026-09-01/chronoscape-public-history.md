# Chronoscape and Public Topography

## Context

An offline prototype introduced Chronoscape: an isometric reading of SYZYGY's
Git history. Its central visual idea is useful for the institutional site, but
the prototype carried full commit details, including author names, subjects,
hashes, and changed-file paths. Those details conflict with the existing public
site boundary for Git-derived data. A complete follow-up review also identified
the Medusae particle field and the intended role of the new terrain on the home
page.

## Decision

Keep Chronoscape as a project-level institutional page at
`site/chronoscape.html`, and make the home terrain its concise institutional
counterpart. Neither is a new official module, a NERV operational surface, or
an Observatory dashboard.

## Changed

- Added a shared Canvas 2D renderer faithful to the offline prototype's 18 x 18
  terrain, sector coordinates, projection, elevation model, labels, rotation,
  and zoom controls.
- Kept only the concise topographic map on the home page; commits, churn,
  reach, timeline navigation, readouts, and charts remain on Chronoscape.
- Added anonymous historical stratum selection, aggregate charts, rotation,
  and zoom controls.
- Extended the site build to generate a privacy-preserving 365-day snapshot,
  capped at 120 strata.
- Replaced the former home Canvas 2D contour map with the reviewed isometric
  map. It uses the latest anonymous aggregate snapshot when available and the
  documented implementation state as its fallback.
- Made Chronoscape retain its implementation-state terrain when a historical
  snapshot is unavailable, while disabling the historical controls.
- Restored the reviewed Medusae particle field only on the home Vision surface
  and Coppermind, MAGI, and Bastion overview surfaces.
- Removed the prototype's perpetual touched-sector repaint. Terrain transitions
  now converge and stop, off-screen maps pause, pixel density is bounded, and
  both Medusae renderers are capped at 30 FPS.
- Added checks for the public-page metadata, static assets, and the
  non-identifying historical data boundary.

## Scope Boundary

- The artifact contains no author identity, e-mail address, commit message,
  hash, parent relationship, changed-file path, or working-tree data.
- The `site`, `docs`, and `root` labels are repository support sectors, not
  official SYZYGY modules.
- Chronoscape does not inspect services, devices, events, health, or runtime
  state. Those concerns remain with the appropriate module contracts.
- Medusae is decorative only, uses local WebGL with a Canvas 2D fallback, and
  respects reduced-motion and visibility while remaining capped at 30 FPS.
- The prototype's per-file manifest is not adopted. The home map contains no
  identifying Git data, and Chronoscape contains aggregate history only.

## Validation

- `npm --prefix site run check`
- `npm --prefix site run build`
- built snapshot availability and public-schema check (`available: true`, with
  commit fields limited to `date`, `stats`, and `sectors`)
