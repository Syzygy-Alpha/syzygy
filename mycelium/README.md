# SYZYGY Mycelium

Mycelium is the distributed mesh module of SYZYGY. Its long-term purpose is to
support device discovery, synchronization, replication, backup, and communication
between user-owned nodes.

This first increment intentionally implements only a local node spine:

- HTTP health, version, and capabilities endpoints
- Mycelium module descriptor
- local Hypha node descriptor
- local peer registry backed by SQLite
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
GET /peers
POST /peers
GET /peers/{node_id}
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
SYZYGY_MYCELIUM_DATABASE_URL
SYZYGY_MYCELIUM_NODE_ID
SYZYGY_MYCELIUM_NODE_NAME
```

## Local Peer Registry

`POST /peers` stores or updates a known peer in Mycelium's local registry. This
is intentionally manual in v0.1: peers are explicitly recorded before any real
network discovery or sync protocol is introduced.

Example payload:

```json
{
  "node_id": "notebook",
  "name": "Notebook",
  "address": "http://192.168.0.11:8030",
  "capabilities": ["sync"]
}
```

`GET /peers` lists known peers, and `GET /peers/{node_id}` returns one stored
peer record.

## Foundation Registration

Mycelium can optionally register its module descriptor with Foundation:

```env
SYZYGY_MYCELIUM_REGISTER_WITH_FOUNDATION=true
SYZYGY_MYCELIUM_FOUNDATION_URL=http://127.0.0.1:8000
SYZYGY_MYCELIUM_FOUNDATION_USERNAME=admin
SYZYGY_MYCELIUM_FOUNDATION_PASSWORD=change-me
```

## Scope Boundary

Mycelium v0.1 does not yet run Syncthing, WireGuard, Tailscale, gRPC, automatic
peer discovery, backup, replication, or distributed sync. Those remain future
integrations after the local node and peer registry contracts are stable.
