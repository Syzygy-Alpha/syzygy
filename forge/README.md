# SYZYGY Forge

Forge is the engineering module of SYZYGY. Its long-term purpose is to support
projects, Git workflows, builds, deploys, templates, containers, CI/CD, and
programming agents.

This first increment intentionally implements only the module bootstrap:

- HTTP health, version, and capabilities endpoints
- Forge module descriptor
- optional registration with Foundation
- local project inspection
- local project registry backed by SQLite

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
GET /projects
POST /projects
GET /projects/{name}
```

## Scope Boundary

Forge v0.1 does not yet automate commits, builds, deployments, templates, CI/CD,
or agent-driven programming. Those features should grow only after the module
contract with Foundation is stable.

## Project Inspection

`GET /projects/current` inspects the configured workspace root and reports
whether it exists, whether it is inside a Git repository, the current branch,
short commit, and dirty state.

## Project Registry

`POST /projects` registers an existing local project path under a stable name.
`GET /projects` lists registered projects, and `GET /projects/{name}` returns
the stored record plus a fresh read-only inspection.

Forge stores project records in SQLite through `SYZYGY_FORGE_DATABASE_URL`. The
registry does not mutate repositories; it only records known local paths.
