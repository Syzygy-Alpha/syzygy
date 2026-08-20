# SYZYGY Roadmap

This roadmap is intentionally incremental. Future vision does not imply current
implementation.

## Now

- Maintain project-level documentation.
- Stabilize Foundation v0.1.
- Keep tests, lint, type checks, and activity logs current.
- Avoid implementing future modules before their contracts are clear.
- Use the Foundation module registry as the first integration contract for
  future modules.
- Keep Foundation, Forge, and Observatory contracts stable.
- Keep Mycelium's first local node contract minimal until discovery is designed.
- Keep NERV Sprint 001 lightweight until its operational contract stabilizes.
- Balance vertical evolution: avoid more than five consecutive feature commits
  in one module without reassessing whether another official module should get
  a minimal functional increment.

## Next

- Add basic configuration update events.
- Validate Docker locally once Docker is available.
- Add a scheduled retry policy for Forge outbox events after the manual path is stable.
- Add Observatory status change events from stored health observations.
- Add Mycelium peer status updates before attempting real network discovery.
- Extend NERV from the Forge project workbench into internal app surfaces after
  their lifecycle contract is designed.

## Later

- Mycelium device discovery and sync experiments.
- Observatory health/log visibility beyond manual observations.
- Tungsten secrets and trust model.
- Coppermind knowledge storage.
- MAGI persona prototypes.
- Balance rule engine.
- Elric profile.
- Imrryr internal apps.
- Bastion isolated labs.

## Guardrails

- Do not add cloud as a mandatory dependency.
- Do not add AI where it is not needed.
- Do not move responsibilities between modules silently.
- Do not implement large cross-module flows before their contracts exist.
