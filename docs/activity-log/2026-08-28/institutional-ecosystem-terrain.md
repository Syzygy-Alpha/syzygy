# Institutional Ecosystem Terrain

## Context

The institutional site already explained SYZYGY through editorial sections,
module pages, particle identities, and a conceptual architecture diagram. A
topographic language can make relationships and change easier to explore, but
the public static site must not pretend to be the live operational dashboard
owned by NERV or create another official module.

## Decision

Add a lightweight ecosystem terrain to the project-level site. Native HTML
controls represent the twelve official modules and three explicit views:
architecture, documented implementation state, and aggregate Git activity.
Canvas 2D renders deterministic contour lines through a scalar field and
Marching Squares. The build, rather than the browser, derives commit counts.

## Changed

- Added accessible module and layer controls with a responsive readout.
- Added static contour generation with eight levels, adaptive grid resolution,
  and redraws only after interaction or resize.
- Added a reproducible 90-day Git snapshot based on the artifact revision.
- Added full-history Pages checkout and site rebuilds for every `main` push so
  the deployed activity snapshot follows repository evolution.
- Kept the terrain implementation in a dedicated, dependency-free script and
  extended static checks and performance budgets to cover it.

## Scope Boundary

- The terrain is a site visualization, not an `Atlas` module or another module
  equivalent to Foundation, NERV, or the official portfolio.
- Architecture relief is explanatory and does not introduce module contracts.
- State relief follows documented functional/future labels; it is not runtime
  health telemetry.
- Commit relief contains aggregate directory counts only. It publishes no
  author identity, e-mail, message, file path, secret, or working-tree data.
- Live state, devices, events, services, and operations remain future NERV
  concerns that must use explicit contracts when implemented.

## Validation

- `npm --prefix site run check`
- `npm --prefix site run build`
- generated snapshot schema and aggregate-count review
- `git diff --check`
