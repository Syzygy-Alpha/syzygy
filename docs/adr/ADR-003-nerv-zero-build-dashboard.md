# ADR-003 - NERV Zero-Build Dashboard For Sprint 001

## Context

NERV is intended to become the operational center of SYZYGY, and the preferred
long-term frontend direction for the ecosystem includes React and Material UI.

However, the first NERV increment needs to be:

- lightweight
- fast to bootstrap
- local-first
- minimally dependent on machine-specific tooling
- easy to evolve after the operational contract is proven useful

At this stage, the higher risk is not visual simplicity. The higher risk is
locking the first operational dashboard behind a frontend toolchain before the
NERV contract itself is stable.

## Decision

Sprint 001 of NERV will use a zero-build frontend served directly by FastAPI
with static HTML, CSS, and JavaScript.

This first dashboard will prioritize:

- local rendering
- explicit API contracts
- lightweight launch actions
- simple upgrade paths

## Alternatives

- Start NERV immediately with React and Material UI.
- Build no UI and leave NERV as API-only bootstrap.
- Use a separate frontend build pipeline from the first commit.

## Consequences

- NERV can ship a usable command center quickly.
- The first dashboard remains very lightweight and local.
- Frontend complexity stays proportional to the current contract maturity.
- A later migration to React remains possible once the UI and API stabilize.

## Status

Accepted
