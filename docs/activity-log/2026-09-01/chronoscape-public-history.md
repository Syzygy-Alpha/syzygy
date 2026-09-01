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

- Added a responsive Canvas 2D isometric terrain with commits, churn, reach,
  and documented-state layers.
- Added anonymous historical stratum selection, aggregate charts, rotation,
  and zoom controls.
- Extended the site build to generate a privacy-preserving 365-day snapshot,
  capped at 120 strata.
- Replaced the former home Canvas 2D contour map and Git activity layer with a
  static isometric implementation-state map. Historical readings and graphs
  route to Chronoscape.
- Made Chronoscape retain its implementation-state terrain when a historical
  snapshot is unavailable, while disabling the historical controls.
- Restored the reviewed Medusae particle field only on the home Vision surface
  and Coppermind, MAGI, and Bastion overview surfaces.
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
  respects the existing reduced-motion, visibility, and lower-hardware rules.
- The prototype's per-file manifest is not adopted. The home map contains no
  Git-derived data, and Chronoscape contains aggregate history only.

## Validation

- `npm --prefix site run check`
- `npm --prefix site run build`
- built snapshot availability and public-schema check (`available: true`, 50
  strata, commit fields limited to `date`, `stats`, and `sectors`)
