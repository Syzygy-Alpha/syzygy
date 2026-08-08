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
- local project creation from built-in templates

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
GET /project-templates
GET /project-templates/{name}
GET /projects
POST /projects
POST /projects/create
GET /projects/{name}/commands
GET /projects/{name}/commands/{command_name}/plan
POST /projects/{name}/commands/{command_name}/runs
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

## Project Creation

`POST /projects/create` creates a new local project inside
`SYZYGY_FORGE_WORKSPACE_ROOT` from a built-in template and registers it in the
project registry.

The first supported template is `python-cli`. Project creation writes local
files only inside the configured workspace root. Git initialization is opt-in
through the request payload and does not create commits or push to remotes.

## Command Discovery

`GET /projects/{name}/commands` reads `syzygy.project.toml` from a registered
project and returns the `[commands]` table as declarative command names and
strings.

Forge does not execute these commands yet. This endpoint is intentionally
read-only so future command execution can be designed with explicit safety
rules.

`GET /projects/{name}/commands/{command_name}/plan` validates one declared
command against the current safety policy and returns the planned working
directory, parsed arguments, allow/deny status, and reason. It also does not
execute anything.

`POST /projects/{name}/commands/{command_name}/runs` executes an allowed command
only when the request includes `confirm=true`. Commands are executed without a
shell, inside the registered project path, and with a bounded timeout.
