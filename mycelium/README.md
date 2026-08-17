# SYZYGY Mycelium

Mycelium is the distributed mesh module of SYZYGY. Its long-term purpose is to
support device discovery, synchronization, replication, backup, and communication
between user-owned nodes.

This first increment intentionally implements only a local node spine:

- HTTP health, version, and capabilities endpoints
- Mycelium module descriptor
- local Hypha node descriptor
- optional registration with Foundation

## Local Development

```bash
cd mycelium
python -m pip install -e ".[dev]"
python -m uvicorn syzygy_mycelium.main:app --reload --port 8030
```

Useful endpoints:

```text
GET /
GET /health
GET /version
GET /capabilities
GET /node
```

## Local Node

`GET /node` returns the local Hypha node identity and current local status. This
is the smallest useful contract for future discovery and sync work.

Example:

```bash
curl http://127.0.0.1:8030/node
```

The local node can be configured with:

```text
SYZYGY_MYCELIUM_NODE_ID
SYZYGY_MYCELIUM_NODE_NAME
```

## Foundation Registration

Mycelium can optionally register its module descriptor with Foundation:

```env
SYZYGY_MYCELIUM_REGISTER_WITH_FOUNDATION=true
SYZYGY_MYCELIUM_FOUNDATION_URL=http://127.0.0.1:8000
SYZYGY_MYCELIUM_FOUNDATION_USERNAME=admin
SYZYGY_MYCELIUM_FOUNDATION_PASSWORD=change-me
```

## Scope Boundary

Mycelium v0.1 does not yet run Syncthing, WireGuard, Tailscale, gRPC, backup,
replication, or distributed sync. Those remain future integrations after the
local node contract is stable.
