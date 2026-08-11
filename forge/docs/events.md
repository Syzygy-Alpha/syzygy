# Forge Event Catalog

Forge event contracts prepare publication through the SYZYGY event
infrastructure. Current Forge code writes generated events to a local SQLite
outbox and does not publish them to an external transport yet.

Subjects follow:

```text
syzygy.forge.<EventName>
```

## CommandRunStarted

- Producer: Forge command execution
- Consumers: Future Observatory, NERV, audit components
- Payload:

```json
{
  "run_id": 1,
  "project": "hello-tool",
  "command_name": "test",
  "command": "python -m pytest",
  "cwd": "C:/workspace/hello-tool",
  "allowed": true,
  "reason": "allowed",
  "started_at": "2026-08-08T00:00:00+00:00"
}
```

- Purpose: Announce that a confirmed Forge command run started.
- Version: `1.0`

## CommandRunCompleted

- Producer: Forge command execution
- Consumers: Future Observatory, NERV, audit components
- Payload:

```json
{
  "run_id": 1,
  "project": "hello-tool",
  "command_name": "test",
  "command": "python -m pytest",
  "cwd": "C:/workspace/hello-tool",
  "allowed": true,
  "reason": "allowed",
  "returncode": 0,
  "timed_out": false,
  "started_at": "2026-08-08T00:00:00+00:00",
  "completed_at": "2026-08-08T00:00:03+00:00"
}
```

- Purpose: Announce that a Forge command run finished.
- Version: `1.0`

## Scope Boundary

Forge event payloads do not include stdout or stderr. Command output can contain
secrets or sensitive local data, so it remains outside the event contract.

## Current Routing

When a confirmed command run finishes, Forge stores `CommandRunStarted` and
`CommandRunCompleted` in the local event outbox. The outbox can be inspected
with:

```text
GET /events/outbox
GET /events/outbox?status=pending
```

Future work should add an external publisher that reads from this outbox and
marks events as published after successful delivery.
