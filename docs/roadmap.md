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

## Next

- Improve Foundation persistence migrations.
- Add basic configuration update events.
- Validate Docker locally once Docker is available.
- Start Forge only when development automation becomes the next concrete need.

## Later

- Mycelium device discovery and sync experiments.
- Observatory health/log visibility.
- Tungsten secrets and trust model.
- Coppermind knowledge storage.
- MAGI persona prototypes.
- Balance rule engine.
- NERV operational dashboard.
- Elric profile.
- Imrryr internal apps.
- Bastion isolated labs.

## Guardrails

- Do not add cloud as a mandatory dependency.
- Do not add AI where it is not needed.
- Do not move responsibilities between modules silently.
- Do not implement large cross-module flows before their contracts exist.
