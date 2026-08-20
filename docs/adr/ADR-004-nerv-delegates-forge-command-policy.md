# ADR-004 - NERV Delegates Forge Command Policy

## Context

NERV needs to reduce repeated terminal work for known local projects. Forge
already owns the registered-project, command manifest, command plan, and command
execution contracts. Reimplementing those rules in NERV would duplicate safety
policy and create divergent behavior between the two modules.

## Decision

NERV will present Forge project commands through a typed HTTP client and will
delegate planning and execution to Forge. Before execution, NERV will request a
fresh plan and refuse to invoke Forge's run endpoint unless the plan is allowed.
NERV requires explicit confirmation in both the dashboard flow and its own API.

## Alternatives

- Give NERV direct filesystem and subprocess access to project commands.
- Implement a generic remote command console in NERV.
- Display command metadata only and keep all execution outside NERV.

## Consequences

- Forge remains the sole authority for command policy and execution history.
- NERV gains an operational project workbench without becoming a shell runner.
- The contract depends on Forge being reachable locally.
- NERV should not add write operations outside explicit Forge contracts without
  a separate review.

## Status

Accepted
