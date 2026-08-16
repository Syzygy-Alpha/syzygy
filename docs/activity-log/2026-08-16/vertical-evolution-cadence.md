# Vertical Evolution Cadence

## Context

The project was gaining useful depth in Foundation, Forge, and Observatory, but
there was a risk of staying too long inside one module through small local
refinements while other official modules remained unstarted.

The user explicitly requested a more vertical evolution strategy: continue
improving existing modules, but also create new official modules when the
current module already has enough functional spine.

## Created

- Added a permanent rule to `AGENTS.md` for vertical evolution.
- Defined an acceptable commit cadence per module before reassessing whether to
  move to another official module.
- Added exceptions for staying in the same module when a blocker, contract,
  security issue, or explicit user request requires it.
- Updated the roadmap to include this cadence as an active guardrail.

## Commit Cadence

The recommended window before switching modules is:

- 1 to 2 bootstrap commits;
- 3 to 5 vertical MVP commits;
- 1 to 2 stabilization or documentation commits.

After five consecutive feature commits in one module, the agent should reassess
whether the next step should be another official module.

## What It Changes

This does not force premature modules. It adds a checkpoint so the platform
keeps growing as an ecosystem instead of becoming one very deep module plus many
empty names.

## Validation

Documentation/process change only.

- `git diff --check` passed.
- `AGENTS.md` section numbering was reviewed after adding the new rule.
