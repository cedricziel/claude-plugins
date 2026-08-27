---
name: signaldb-observe
description: Instrument any application with OpenTelemetry and ship its traces, logs, and metrics to the user's SignalDB deployment — provisioning a tenant and API key, configuring OTLP export with SignalDB's auth headers, and verifying data arrives via the query APIs. Use this whenever the user wants to "observe" an app, add telemetry/tracing/logging/metrics to a project, send OpenTelemetry data to SignalDB, set up observability for a service, or connect an app to their SignalDB instance — even if they don't name SignalDB explicitly (it is their default observability backend). Also use when querying SignalDB (TraceQL/LogQL/PromQL), managing SignalDB tenants or API keys, or debugging why telemetry isn't showing up.
---

# Observe an app with SignalDB

SignalDB is the user's own observability backend (github.com/cedricziel/signaldb): an OTLP-native database for traces, logs, and metrics with Tempo-, Loki-, Prometheus-, and Pyroscope-compatible query APIs. This skill walks an app from "no telemetry" to "data visible in SignalDB" in five steps. Do the steps in order; each has a verification gate so failures are caught early instead of at the end.

For exact API payloads, ports, and error codes, read `references/apis.md` when you reach the step that needs it.

## Step 1 — Locate the SignalDB deployment

Figure out which instance to target, in this order:

1. **Existing config in the app** — grep the repo for `OTEL_EXPORTER_OTLP_ENDPOINT`, `signaldb`, or `x-tenant-id` in env files, compose files, and deploy manifests. If found, reuse it.
2. **The user's own deployment** — ask where SignalDB runs (router/UI base URL, OTLP gRPC 4317 and HTTP 4318 endpoints; note the router port may differ from the default 3000) and where the admin and ingest API keys are kept (their secret manager). Prefer this for real apps.
3. **Local dev instance** — for experiments, run SignalDB locally from a checkout of github.com/cedricziel/signaldb: `./scripts/run-dev.sh` (monolithic, SQLite, file storage) or `docker compose up`. Local default endpoints: OTLP gRPC `localhost:4317`, OTLP HTTP `localhost:4318`, HTTP query API `localhost:3000`.

If none of these resolve, ask the user which instance to use rather than guessing a hostname.

**Verify**: `curl -fsS <router-base-url>/health` returns 200. The router (HTTP query API, default port 3000) and the acceptor (OTLP ingest, ports 4317/4318) may be different hostnames/ports on a real deployment — confirm both.

## Step 2 — Provision a tenant and API key

Every request to SignalDB is tenant-scoped. Each app (or environment) should get its own tenant, named after the app (e.g. tenant `jobradar`, dataset `production`).

Check whether the tenant already exists, then create what's missing via the admin API (requires the admin API key):

```bash
BASE=<router-base-url>   # e.g. http://localhost:3000
ADMIN="Authorization: Bearer $ADMIN_KEY"

curl -fsS -H "$ADMIN" $BASE/api/v1/admin/tenants                     # list existing
curl -fsS -H "$ADMIN" -H 'content-type: application/json' \
  -d '{"id":"jobradar","name":"JobRadar","default_dataset":"production"}' \
  $BASE/api/v1/admin/tenants
curl -fsS -H "$ADMIN" -H 'content-type: application/json' \
  -d '{"name":"production key","scopes":["traces:write","logs:write","metrics:write"]}' \
  $BASE/api/v1/admin/tenants/jobradar/api-keys
```

One hard-won gotcha about admin-API tenants (verified 2026-07-29 on hive):

- **`default_dataset` does not create the dataset.** Creating a tenant with `"default_dataset":"production"` only records the name; POST `/api/v1/admin/tenants/{id}/datasets` with `{"name":"production"}` afterwards, or `whoami` fails with 403 "Dataset 'production' not found".

> **Fixed (2026-08-02):** admin-API tenants used to be _ingest-only_ — every query 500'd with `failed to resolve catalog: <tenant>` until a `[[auth.tenants]]` block was added to `signaldb.toml` and the app restarted, because the querier registered catalogs from config only. The querier now resolves a tenant's catalog on demand from a source-agnostic tenant registry (config ∪ database), so an admin-API tenant is queryable the moment it is created — no config block, no restart. If you hit `failed to resolve catalog` on a deployment predating this fix, the old remedy (config block + restart) still works; the durable fix is to upgrade.

The key-creation response contains the raw key **exactly once** — it is stored hashed and can never be retrieved again. Immediately store it where the app will read it (the app's `.env`, 1Password, or the deployment's secret store). Never commit it; if the repo has `.env.example`, add the variable names there with placeholder values.

Alternatives when there is no admin API access: `signaldb-cli tenant create` / `api-key create` on the SignalDB host, or (for self-hosted config-file setups) a `[[auth.tenants]]` block in `signaldb.toml` — see `references/apis.md`.

**Verify**: `curl -fsS -H "Authorization: Bearer $APP_KEY" -H "x-tenant-id: jobradar" $BASE/api/v1/whoami` returns the tenant, its datasets, and the default dataset.

## Step 3 — Instrument the app with OpenTelemetry

Use the standard OpenTelemetry SDK for the app's language — SignalDB speaks plain OTLP, so nothing vendor-specific is needed in code. If a language-specific OpenTelemetry skill is available in this session (e.g. `opentelemetry-js`, `opentelemetry-go`, `opentelemetry-rust`, `opentelemetry-java`), use it for this step; otherwise follow current OTel docs for the language.

Guidelines that matter regardless of language:

- Set a meaningful `service.name` (e.g. `jobradar-api`, `jobradar-worker` — one per deployable unit). This is the primary search dimension in SignalDB.
- Start with auto-instrumentation (HTTP server/client, DB drivers) before hand-writing spans; add manual spans only around domain logic worth seeing.
- Export **traces, logs, and metrics** over OTLP unless the user scopes it down. Route application logs through the OTel log bridge/appender so they carry trace context.
- Prefer configuring the exporter via standard `OTEL_*` environment variables (Step 4) over hardcoding endpoints in code — it keeps dev/prod differences out of the codebase.

## Step 4 — Point OTLP export at SignalDB

SignalDB authenticates ingest with two required headers: the API key and an **explicit tenant id** (the tenant is intentionally never inferred from the key). Dataset is optional and falls back to the tenant's default.

Environment-variable configuration (works with every OTel SDK):

```bash
OTEL_SERVICE_NAME=jobradar-api
OTEL_EXPORTER_OTLP_ENDPOINT=http://<acceptor-host>:4317     # gRPC (default protocol)
# or: OTEL_EXPORTER_OTLP_ENDPOINT=http://<acceptor-host>:4318 with OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_HEADERS=authorization=Bearer sk-...,x-tenant-id=jobradar
# optional third header: x-dataset-id=production
```

Pitfalls to steer around:

- Header keys must be **lowercase** (`authorization`, `x-tenant-id`) — gRPC metadata rejects uppercase keys.
- In `OTEL_EXPORTER_OTLP_HEADERS` the value is `key=value` pairs comma-separated; the space in `Bearer sk-...` is fine, but some SDKs require it URL-encoded (`Bearer%20sk-...`) — if auth fails with a well-known-good key, try that.
- gRPC (4317) and HTTP (4318) are different ports; don't send HTTP protobuf to 4317 or vice versa.
- If the app already has an OTel Collector in front, add the headers in the collector's `exporters.otlp` config instead of the app.

## Step 5 — Generate traffic and verify end to end

Run the app, exercise a few endpoints (or wait for its normal workload), then confirm data landed. Ingested data flows OTLP → WAL → writer → Iceberg tables, so it can take on the order of **seconds up to a minute** to become queryable — an immediately-empty search result is not a failure; retry briefly before diagnosing.

All queries hit the router with the same auth headers as ingest:

```bash
AUTH=(-H "Authorization: Bearer $APP_KEY" -H "x-tenant-id: jobradar")

curl -fsS "${AUTH[@]}" "$BASE/tempo/api/search?limit=5"                                  # recent traces
curl -fsS "${AUTH[@]}" "$BASE/tempo/api/search/tag/service.name/values"                  # services seen
curl -fsS "${AUTH[@]}" -G "$BASE/loki/api/v1/query_range" \
  --data-urlencode 'query={service_name="jobradar-api"}' --data-urlencode 'limit=10'     # logs
curl -fsS "${AUTH[@]}" -G "$BASE/prometheus/api/v1/label/__name__/values"                # metric names
```

Also point the user at the built-in explore UI at `<router-base-url>/ui` (log in with the API key + tenant) for interactive browsing, and mention that Grafana works out of the box: the Tempo datasource against `$BASE/tempo`, Loki against `$BASE/loki`, Prometheus against `$BASE/prometheus`, with the auth headers set as custom HTTP headers.

**Done when**: at least one signal type the user asked for is visible via a query API or the UI, and the app's telemetry config is committed (endpoints and variable names — never the key itself).

## Troubleshooting quick table

| Symptom                                      | Likely cause                                                                                                                                                                                       |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| HTTP 400 on ingest/query                     | Missing/malformed `authorization` or `x-tenant-id` header                                                                                                                                          |
| HTTP 401                                     | Wrong or revoked API key                                                                                                                                                                           |
| HTTP 403                                     | Key is valid but belongs to a different tenant than `x-tenant-id` claims                                                                                                                           |
| HTTP 429 / gRPC RESOURCE_EXHAUSTED           | Per-tenant rate limit or storage quota hit                                                                                                                                                         |
| Exporter connect errors                      | Wrong port for protocol (4317 gRPC vs 4318 HTTP), or acceptor not reachable from the app's network                                                                                                 |
| 200 on ingest but queries empty              | Wait ~1 min for WAL flush; then check the tenant/dataset headers match between ingest and query                                                                                                    |
| 500 `failed to resolve catalog: <tenant>`    | Fixed 2026-08-02 (querier resolves admin-API tenants on demand), so this no longer occurs. On a deployment predating the fix: add a `[[auth.tenants]]` block and restart, or upgrade (see Step 2). |
| Expected metric missing from `__name__` list | Names are stored in dotted OTel form (`app.requests`), not Prometheus underscore form (`app_requests_total`) — grep for the dotted name                                                            |

For deeper API details (admin API payloads, full endpoint list, ports, config-file tenant blocks): `references/apis.md`.
