# Forge Event Catalog

Forge event contracts prepare publication through the SYZYGY event
infrastructure. Current Forge code writes generated events to a local SQLite
outbox and can publish pending events through an explicitly enabled transport.

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
GET /events/outbox/summary
```

The summary endpoint reports local delivery health: total events, counts by
status, total attempts, maximum attempts, oldest pending event, and latest
failed event. Its `delivery_status` is `ok`, `pending`, or `attention`.

External publication is disabled by default. When
`SYZYGY_FORGE_EVENT_PUBLISHER_ENABLED=true`, pending events can be published
with:

```text
POST /events/outbox/publish
```

The request must include `confirm=true`. Successful delivery marks events as
`published`, increments `attempts`, clears `last_error`, and stores
`published_at`. Failed delivery marks events as `failed`, increments
`attempts`, and stores `last_error`.

Failed records can be requeued manually with:

```text
POST /events/outbox/{record_id}/requeue
POST /events/outbox/requeue-failed
```

Both requests must include `confirm=true`. Requeue only accepts records with
status `failed`; it changes them back to `pending`, preserves `attempts`, clears
`last_error`, and clears `published_at`.

Supported transports:

- `memory`: local test transport that records publish attempts in process.
- `nats`: publishes the event envelope to the record subject.

Failed events are not retried automatically yet. A future increment should add
a scheduled retry policy only after the manual path is stable.
