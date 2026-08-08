# Foundation Event Catalog

Events use versioned payloads and are published through the internal EventBus
abstraction. NATS subjects follow:

```text
syzygy.foundation.<EventName>
```

## ModuleStarted

- Producer: Foundation module registry
- Consumers: Observatory, NERV, future audit components
- Payload:

```json
{
  "module": "foundation",
  "version": "0.1.0",
  "status": "online",
  "health": "ok"
}
```

- Purpose: Announce that a module became available.
- Version: `1.0`

## ModuleStopped

- Producer: Foundation module registry
- Consumers: Observatory, NERV, future audit components
- Payload:

```json
{
  "module": "foundation",
  "version": "0.1.0",
  "status": "stopped",
  "health": "ok"
}
```

- Purpose: Announce a controlled module shutdown.
- Version: `1.0`

## ConfigUpdated

- Producer: Foundation configuration service
- Consumers: Future modules that subscribe to configuration changes
- Payload:

```json
{
  "key": "log_level"
}
```

- Purpose: Announce configuration changes without exposing secret values.
- Version: `1.0`

## HealthChanged

- Producer: Foundation health service or Foundation module registry
- Consumers: Observatory, NERV
- Payload:

```json
{
  "module": "foundation",
  "version": "0.1.0",
  "status": "degraded",
  "health": "error"
}
```

- Purpose: Announce a health state transition.
- Version: `1.0`

## Current Routing

Foundation publishes module lifecycle events through the EventBus when the bus is
connected. If NATS is unavailable in local development, module API operations
still persist state, but event publication is skipped.
