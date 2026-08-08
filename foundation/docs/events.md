# Foundation Event Catalog

Events use versioned payloads and are published through the internal EventBus
abstraction. NATS subjects follow:

```text
syzygy.foundation.<EventName>
```

## ModuleStarted

- Producer: Foundation or future module lifecycle manager
- Consumers: Observatory, NERV, future audit components
- Payload:

```json
{
  "module": "foundation",
  "version": "0.1.0"
}
```

- Purpose: Announce that a module became available.
- Version: `1.0`

## ModuleStopped

- Producer: Foundation or future module lifecycle manager
- Consumers: Observatory, NERV, future audit components
- Payload:

```json
{
  "module": "foundation"
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

- Producer: Foundation health service or future module health reporters
- Consumers: Observatory, NERV
- Payload:

```json
{
  "module": "foundation",
  "status": "degraded"
}
```

- Purpose: Announce a health state transition.
- Version: `1.0`

