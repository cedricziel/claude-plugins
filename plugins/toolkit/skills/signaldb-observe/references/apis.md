# SignalDB API reference

Facts verified against the SignalDB source (`~/private/code/signaldb`) as of 2026-07. If a call behaves differently, the deployment may be running an older build — check the repo rather than assuming this file is right.

## Ports (defaults)

| Service  | Protocol                  | Port  | Purpose                                     |
| -------- | ------------------------- | ----- | ------------------------------------------- |
| Acceptor | OTLP gRPC                 | 4317  | Trace/log/metric/profile ingest             |
| Acceptor | OTLP HTTP                 | 4318  | Same, `http/protobuf`                       |
| Router   | HTTP                      | 3000  | All query APIs, admin API, explore UI       |
| Router   | Arrow Flight              | 50053 | Grafana native plugin backend               |
| Querier  | Arrow Flight / Tempo gRPC | 50054 | Internal + Tempo query-frontend integration |
| Writer   | Arrow Flight              | 50061 | Internal                                    |

In monolithic mode (`signaldb` binary, `run-dev.sh`, docker compose) all of these run in one process on localhost. Distributed deployments may put acceptor and router behind different hostnames or remapped ports — on the user's hive deployment the router HTTP API + UI is published on **30200** (mapped to container port 3000; TrueNAS convention favors high ports), while 4317/4318 keep their defaults.

## Authentication

Every tenant-facing request needs:

- `Authorization: Bearer <api-key>`
- `x-tenant-id: <tenant-id>` — always explicit; SignalDB deliberately does not infer the tenant from the key
- `x-dataset-id: <dataset-id>` — optional; resolution order is explicit header → tenant `default_dataset` → first dataset flagged `is_default` → HTTP 400

Error codes: **400** missing/malformed headers, **401** invalid key, **403** key valid but wrong tenant/dataset, **429** rate limit or quota (`quota_exceeded`).

The embedded UI uses a session cookie instead (`POST /ui/session` sets it), so browser access to `/ui` only needs the login form.

## Admin API (router, `/api/v1/admin`)

Requires the **admin** API key (`[auth].admin_api_key` in the server config) as `Authorization: Bearer`.

| Endpoint                                           | Methods          |
| -------------------------------------------------- | ---------------- |
| `/api/v1/admin/tenants`                            | GET, POST        |
| `/api/v1/admin/tenants/{id}`                       | GET, PUT, DELETE |
| `/api/v1/admin/tenants/{id}/api-keys`              | GET, POST        |
| `/api/v1/admin/tenants/{id}/api-keys/{key_id}`     | DELETE (revoke), PATCH ({scopes?, dataset_id?}) |
| `/api/v1/admin/tenants/{id}/datasets`              | GET, POST        |
| `/api/v1/admin/tenants/{id}/datasets/{dataset_id}` | DELETE           |

Request bodies:

```jsonc
// POST /api/v1/admin/tenants
{ "id": "jobradar", "name": "JobRadar", "default_dataset": "production" }  // default_dataset optional

// POST /api/v1/admin/tenants/{id}/api-keys
{ "name": "production key", "scopes": ["traces:write","logs:write","metrics:write"], "dataset_id": "production" }  // name/dataset_id optional; scopes REQUIRED (also *:read, schema:read, schema:write)

// POST /api/v1/admin/tenants/{id}/datasets
{ "name": "staging" }
```

Key-creation response — the `key` field is shown **only at creation**; keys are stored SHA-256-hashed:

```json
{ "id": "…", "key": "sk-…", "name": "production key", "created_at": "…" }
```

A machine-readable OpenAPI spec is served at `GET /api/v1/openapi.json` (public, no auth).

## Tenant self-service API (router, `/api/v1`, tenant auth)

| Endpoint                             | Method | Purpose                                                                                   |
| ------------------------------------ | ------ | ----------------------------------------------------------------------------------------- |
| `/api/v1/whoami`                     | GET    | Authenticated tenant + datasets + default dataset — the canonical "is my key right" check |
| `/api/v1/tenants`                    | GET    | Tenants visible to the caller                                                             |
| `/api/v1/tenants/{id}/tables`        | GET    | List the tenant's tables                                                                  |
| `/api/v1/tenants/{id}/tables/create` | POST   | Pre-create tables                                                                         |
| `/api/v1/tenants/{id}/schemas`       | GET    | Tenant schemas                                                                            |

## Query APIs (router, tenant auth on all)

- **Traces (Tempo-compatible), `/tempo/…`**: `GET /tempo/api/echo` (health), `GET /tempo/api/traces/{trace_id}` (optional `start`/`end` unix-second hints), `GET /tempo/api/search` (params: `q`/TraceQL subset, `tags`, `minDuration`, `maxDuration`, `limit`, `spss`, `start`, `end`), `GET /tempo/api/search/tags`, `GET /tempo/api/search/tag/{tag}/values`. Queryable tags are `service.name`, `name`, `status`; other attribute tags return 501 for values. TraceQL metrics endpoints (`/tempo/api/metrics/*`) return 501.
- **Logs (Loki-compatible), `/loki/…`**: `GET /loki/api/v1/query`, `/query_range`, `/labels`, `/label/{name}/values`, `/series` with LogQL, including the metric-query surface (`rate`, `count_over_time`, aggregations, etc.). Stream selectors match materialized columns like `service_name`; arbitrary attribute matching may fall back to substring matching over the attributes JSON — keep selectors to service/level where possible.
- **Metrics (Prometheus-compatible), `/prometheus/…`**: `GET /prometheus/api/v1/query`, `/query_range`, `/labels`, `/label/{name}/values`, `/series` with PromQL.
- **Profiles (Pyroscope-compatible), `/pyroscope/…`** and trace↔profile correlation under `/api/profiles`.
- **Explore UI**: `<router>/ui` — login with API key + tenant id; browses logs, traces, and metrics without Grafana.

## Grafana

Two options:

1. **Built-in datasources**: point Tempo at `<router>/tempo`, Loki at `<router>/loki`, Prometheus at `<router>/prometheus`; add `Authorization` and `x-tenant-id` as custom HTTP headers on each datasource.
2. **Native SignalDB plugin** (`src/grafana-plugin/` in the repo): talks to the router's Flight port (50053) with key/tenant/dataset in secure JSON config; one datasource covers all three signals.

## Provisioning without the admin API

**CLI** (on the SignalDB host / repo checkout):

```bash
signaldb-cli tenant create jobradar --name "JobRadar" --default-dataset production
signaldb-cli api-key create jobradar --name "production key"
signaldb-cli dataset create jobradar --name staging
signaldb-cli query "SELECT …"   # ad-hoc SQL
```

**Config file** (`signaldb.toml`, requires deploy/restart — static config, no key rotation):

```toml
[auth]
admin_api_key = "sk-admin-…"

[[auth.tenants]]
id = "jobradar"
slug = "jobradar"
name = "JobRadar"
default_dataset = "production"

[[auth.tenants.datasets]]
id = "production"
slug = "prod"
is_default = true

[[auth.tenants.api_keys]]
key = "sk-jobradar-…"
name = "Production Key"
```

## Ingest-to-queryable latency

Write path: OTLP → WAL (durable, acked) → writer flush → Iceberg/Parquet. Data is queryable only after the writer flush, typically seconds to ~1 minute. The 30-day default retention applies per signal type unless the deployment overrides `[compactor.retention]`.
