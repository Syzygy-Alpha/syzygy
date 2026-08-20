# Sprint 002 - NERV Operational Quick Actions

## Context

Sprint 001 gave NERV a lightweight dashboard, module cards, links, and local
launch actions. That already reduced friction, but one recurring operational
gap remained: the user still had to open endpoints manually to inspect the
most useful module data.

The next incremental improvement is to keep NERV local and lightweight while
bringing a small set of known module queries directly into the dashboard.

## Sprint Goal

Add safe quick actions to NERV for frequently used module endpoints.

## In Scope

- quick action catalog per known module surface
- inline execution of known HTTP actions
- inline result console in the dashboard
- tests and documentation

## Out of Scope

- arbitrary free-form HTTP requests
- authenticated write actions for Foundation
- persistent action history
- internal app surfaces
- WebSocket streams

## Technical Direction

Sprint 002 keeps quick actions explicit and catalog-driven. NERV should only
execute known module actions that are declared in code, rather than becoming a
generic HTTP client UI.

This preserves safety, keeps the UX simple, and avoids smuggling uncontrolled
cross-module behavior into the operational center.

## Deliverables

- action catalog entries for known surfaces
- action execution API
- dashboard console for inline results
- updated docs and activity log

## Exit Criteria

- at least one useful quick action exists for each known module surface
- quick actions can be executed from the NERV dashboard
- the latest action result is visible without leaving the dashboard
