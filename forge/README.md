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
python -m uvicorn syzygy_forge.main:app --reload --port 8010
```

For a complete local walkthrough with `curl`, see
[Forge Practical Usage](docs/usage.md).

Useful endpoints:

```text
GET /
GET /health
GET /version
GET /capabilities
GET /events/outbox
GET /events/outbox/summary
POST /events/outbox/publish
POST /events/outbox/requeue-failed
POST /events/outbox/{record_id}/requeue
GET /projects/current
GET /project-templates
GET /project-templates/{name}
GET /projects
POST /projects
POST /projects/create
GET /projects/{name}/commands
GET /projects/{name}/commands/{command_name}/plan
POST /projects/{name}/commands/{command_name}/runs
GET /projects/{name}/command-runs
GET /projects/{name}/git/status
GET /projects/{name}/git/branches
POST /projects/{name}/git/branches
POST /projects/{name}/git/branches/switch
POST /projects/{name}/git/commits
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

The currently supported templates are `python-cli`, `python-package`, and
`static-site`. Project creation writes local files only inside the configured
workspace root. Git initialization is opt-in through the request payload and
does not create commits or push to remotes.

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

`GET /projects/{name}/command-runs` lists persisted command run metadata for a
registered project. Forge stores command, cwd, allow/deny state, return code,
timeout state, and timestamps, but it does not persist stdout or stderr.

## Events

Forge defines command lifecycle event contracts in `forge/docs/events.md` for
future publication through the SYZYGY event infrastructure. Current Forge code
stores generated command lifecycle events in a local SQLite outbox through
`GET /events/outbox`.

`GET /events/outbox/summary` reports local delivery health: total events,
status counts, total attempts, maximum attempts, oldest pending event, and most
recent failed event.

External publication is opt-in. Set
`SYZYGY_FORGE_EVENT_PUBLISHER_ENABLED=true` and call
`POST /events/outbox/publish` with `confirm=true` to publish pending events
through the configured transport. The default transport is `memory` for local
testing; `nats` publishes event envelopes to their `syzygy.forge.<EventName>`
subjects using `SYZYGY_FORGE_NATS_URL`.

Failed deliveries can be requeued manually with
`POST /events/outbox/{record_id}/requeue` or
`POST /events/outbox/requeue-failed`. Both operations require `confirm=true`.
Requeue returns failed events to `pending`, preserves the attempt count, and
clears the last error.

## Git Automation

Forge can inspect Git status, list branches, create/switch branches, and create
local commits for registered projects. Mutating Git operations require
`confirm=true`. Forge does not push to remotes.
