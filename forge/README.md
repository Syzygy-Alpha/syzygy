# SYZYGY Forge

Forge is the engineering module of SYZYGY. Its long-term purpose is to support
projects, Git workflows, builds, deploys, templates, containers, CI/CD, and
programming agents.

This first increment intentionally implements only the module bootstrap:

- HTTP health, version, and capabilities endpoints
- Forge module descriptor
- optional registration with Foundation
- local project inspection

## Local Development

```bash
cd forge
python -m pip install -e ".[dev]"
uvicorn syzygy_forge.main:app --reload --port 8010
```

Useful endpoints:

```text
GET /
GET /health
GET /version
GET /capabilities
GET /projects/current
```

## Scope Boundary

Forge v0.1 does not yet automate commits, builds, deployments, templates, CI/CD,
or agent-driven programming. Those features should grow only after the module
contract with Foundation is stable.

## Project Inspection

`GET /projects/current` inspects the configured workspace root and reports
whether it exists, whether it is inside a Git repository, the current branch,
short commit, and dirty state.
