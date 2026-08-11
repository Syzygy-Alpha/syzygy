# 2026-08-11 - Forge Practical Usage Guide

## Context

Forge had endpoint documentation, but it lacked a practical end-to-end guide
showing how to use the module locally.

## Created

- `forge/docs/usage.md` with a complete local `curl` workflow.
- README link from `forge/README.md`.
- Examples for service checks, project creation, command planning, command
  execution, event inspection, event publishing, event requeue, and optional
  Foundation registration.

## What It Does Now

The repository now documents how to actually drive Forge as a local service
without reading the implementation or guessing endpoint payloads.

## Scope Boundary

This is documentation only. It does not add authentication, a CLI, or a UI.

## Validation

Documentation-only change. Reviewed paths and examples manually.
