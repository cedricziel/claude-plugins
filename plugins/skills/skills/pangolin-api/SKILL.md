---
name: pangolin-api
description: 'How to drive a self-hosted Pangolin (fosrl/pangolin) tunnel reverse proxy through its HTTP API with curl — logging in, listing orgs/sites/domains/resources, publishing a service (resource + target), path-routed targets, auth-bypass rules, SSO and IdP settings, and raw TCP/UDP resources. Use whenever a task involves exposing, changing, or inspecting a service behind Pangolin, its newt sites, or its `/api/v1` endpoints. Triggers on: "pangolin", "newt", "gerbil", "badger", "publish this service", "add a resource", a reverse-proxied subdomain served by Pangolin.'
---

# Pangolin API

Everything below comes from the fosrl/pangolin source and live use against a
1.25 community-edition instance. When an endpoint is missing here, see
"Discover endpoints".

## Setup

Keep credentials out of commands and out of this skill. Load them from the user's
secret manager into env vars first:

```bash
export PANGOLIN_URL=...                            # dashboard base URL
export PANGOLIN_EMAIL=...                          # from the secret manager
export PANGOLIN_PASSWORD=...                       # from the secret manager
export PANGOLIN_ORG=...                            # org id, see "orgs" below
```

Examples below also use `UPSTREAM_HOST` / `UPSTREAM_PORT` for the backend
service as seen from the site's newt.

## Auth: session cookie + CSRF header

There are two APIs:

- **`/api/v1`** — the one the dashboard uses. Session cookie auth. This always works.
- **`/v1`** — the integration API for `Bearer <keyId>.<secret>` API keys. It runs
  as a separate server that only starts when the config has
  `flags.enable_integration_api: true`. It listens on `server.integration_port`
  (default 3003), and Traefik doesn't route it by default. Without both, `/v1`
  on the dashboard host hits the Next.js frontend (a 404, or a 200 with the HTML
  app shell, so check the content type, not just the status). A Bearer key on
  `/api/v1` gets 401. Unless the integration API is set up, use the session API.
  To send a key without exposing it in `ps`, pass the header on stdin:
  `printf 'Authorization: Bearer %s\n' "$PANGOLIN_API_KEY" | curl -H @- ...`.

**Every `/api/v1` call needs the header `X-CSRF-Token: x-csrf-protection`** — the
login call too. Without it requests fail with a CSRF error.

```bash
JAR=$(mktemp); H='X-CSRF-Token: x-csrf-protection'; API="$PANGOLIN_URL/api/v1"
jq -n '{email:env.PANGOLIN_EMAIL, password:env.PANGOLIN_PASSWORD}' \
  | curl -s -c "$JAR" -H "$H" -H 'Content-Type: application/json' -d @- "$API/auth/login"
# → {"success":true,"message":"Logged in successfully",...}

pg() { curl -s -b "$JAR" -H "$H" -H 'Content-Type: application/json' "$@"; }
pg "$API/orgs" | jq '.data.orgs[] | {orgId,name}'
```

Reading the values through jq's `env` and piping the body to `curl -d @-` keeps
the password out of `ps` and shell history. Accounts with 2FA need `code` in the login body.

Responses wrap everything: `{data, success, error, message, status}`. List
endpoints return `data.<plural>` plus `data.pagination`, in one of two styles.
Read `data.pagination` to see which one an endpoint uses:

- `{total, pageSize, page}`: query with `?pageSize=200&page=1`. The default page
  size is 20. Orgs, sites, domains and resources use this style.
- `{total, limit, offset}`: query with `?limit=&offset=`. Rules and IdPs use
  this style. These endpoints reject unknown query parameters, so `pageSize`
  makes them return an error.

## Discover endpoints

The tables below cover common tasks only. Don't guess paths for anything else.

**OpenAPI.** The integration API server serves Swagger UI at `/v1/docs` and the
spec at `/v1/openapi.json` (and `/v1/openapi.yaml`). It only covers the `/v1`
API-key routes, and only exists when the integration API is enabled (see Auth).
The dashboard host doesn't serve it: `$PANGOLIN_URL/openapi.json` returns the
SPA shell. If you have shell access to the server, check whether it is running:
`curl -s localhost:3003/v1/openapi.json` inside the pangolin container. The image
has no curl or wget, so use `node -e 'fetch(...)'`.

**Source.** For the `/api/v1` session API, or when the integration API is off,
get the route list from the source for the instance's release:

```bash
V=1.25.3   # instance's Pangolin version (image tag in its compose file); else `main`
curl -sf "https://raw.githubusercontent.com/fosrl/pangolin/$V/server/routers/external.ts" \
  | perl -0777 -ne 'while(/\b\w+\.(get|put|post|delete)\(\s*"([^"]+)"/g){print uc($1)," $2\n"}' \
  | sort -u | grep -E ' /resource/'
```

- `external.ts` is the `/api/v1` session API, about 270 routes. `integration.ts`
  is the `/v1` API-key API.
- Route paths are relative to `/api/v1`. `:orgId`-style segments are parameters.
- `site-resource` routes are a different resource type (private resources that
  clients reach through a site), not public resources. `resource-policy` routes
  are separate too. Grep narrowly.
- To get the request body, open the handler that the route calls. For example,
  `resource.createResource` is in `server/routers/resource/createResource.ts`.
  The zod schemas near the top of that file list the accepted fields. Grep the
  file for `Schema =`. Strict schemas (`z.strictObject`, `.strict()`) reject
  unknown keys.
- Routes under `server/private/` are enterprise-only. Community builds return
  404 or a license error for them.
- Before you write, probe with a `GET` on the same resource. It shows the
  current field names and values.

## Read endpoints

| What                    | Call                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------- |
| Orgs                    | `GET /orgs`                                                                           |
| Sites (newt connectors) | `GET /org/{orgId}/sites` — `siteId`, `name`, `type`, `online`                         |
| Domains                 | `GET /org/{orgId}/domains` — `domainId` (e.g. `domain1`), `baseDomain`                |
| Resources               | `GET /org/{orgId}/resources` — summary only, see below                                |
| One resource            | `GET /resource/{resourceId}` — full settings incl. `applyRules`, `sso`                |
| Targets                 | `GET /resource/{resourceId}/targets` — `ip`, `port`, `method`, path fields            |
| Rules                   | `GET /resource/{resourceId}/rules`                                                    |
| Roles on a resource     | `GET /resource/{resourceId}/roles`                                                    |
| Users on a resource     | `GET /resource/{resourceId}/users`                                                    |
| Users / roles           | `GET /org/{orgId}/users`, `GET /org/{orgId}/roles`                                    |
| IdPs                    | `GET /idp`                                                                            |
| API keys                | `GET /org/{orgId}/api-keys`                                                           |

The resource list is a summary. It has `resourceId`, `niceId`, `name`,
`fullDomain`, `mode`, `enabled`, `sso` and `targets`, but no `applyRules`, and
its targets carry no `method`. In the list, `sso` is `0`/`1`; in
`GET /resource/{id}` it is a boolean. To filter on a setting the list doesn't
have, such as which resources apply rules, call `GET /resource/{id}` for each
resource.

Find a resource by hostname:

```bash
pg "$API/org/$PANGOLIN_ORG/resources?pageSize=500" \
  | jq '.data.resources[] | select((.fullDomain // "") | test("^app\\.")) | {resourceId,niceId,fullDomain,sso}'
```

## Publish an HTTP service

Three calls. `PUT` creates, `POST` updates.

```bash
# 1. resource; stop unless it returns a resourceId
RID=$(pg -X PUT "$API/org/$PANGOLIN_ORG/resource" \
  -d '{"name":"app","subdomain":"app","domainId":"domain1","mode":"http"}' \
  | jq -er 'select(.success) | .data.resourceId') || { echo "create failed"; exit 1; }

# 2. target on a site (the upstream as seen from that site's newt)
pg -X PUT "$API/resource/$RID/target" \
  -d "$(jq -n --arg ip "$UPSTREAM_HOST" --argjson port "$UPSTREAM_PORT" \
        '{siteId:1, ip:$ip, port:$port, method:"http", enabled:true}')"

# 3. optional: turn off Pangolin's login wall (only for apps with their own auth)
pg -X POST "$API/resource/$RID" -d '{"sso":false}'
```

- `method` is `http`, `https`, or `h2c`. Use **`h2c` for gRPC upstreams** (e.g. OTLP
  on 4317): Traefik terminates TLS with its Let's Encrypt cert and speaks
  cleartext HTTP/2 to the backend, so the backend needs no cert.
- Turning off `sso`, adding bypass rules, or removing auth weakens access
  control. **Confirm with the user before doing it** — Claude Code's auto-mode
  classifier blocks it anyway.
- Verify: `curl -sI https://app.<domain>` — an SSO-on resource answers non-browser
  requests with a plain `401`, not a redirect. That 401 means routing works.

Update a target: `POST /target/{targetId}`. Delete: `DELETE /target/{targetId}`,
`DELETE /resource/{resourceId}`.

## Path-routed targets

`PUT /resource/{id}/target` also accepts:

| Field             | Values                                    |
| ----------------- | ----------------------------------------- |
| `path`            | e.g. `/app`                               |
| `pathMatchType`   | `exact`, `prefix`, `regex`                |
| `rewritePath`     | replacement path                          |
| `rewritePathType` | `exact`, `prefix`, `regex`, `stripPrefix` |
| `priority`        | 1–1000, higher wins                       |

Pattern: a default target with no path at priority 100, path targets at 200.

```bash
pg -X PUT "$API/resource/$RID/target" \
  -d "$(jq -n --arg ip "$UPSTREAM_HOST" '{siteId:1, ip:$ip, port:8081, method:"http",
        enabled:true, path:"/ws", pathMatchType:"prefix", priority:200}')"
```

## Rules (auth bypass / blocking)

Rules only apply when the resource has `applyRules:true`:

```bash
pg -X POST "$API/resource/$RID" -d '{"applyRules":true}'
pg -X PUT  "$API/resource/$RID/rule" \
  -d '{"action":"ACCEPT","match":"PATH","value":"/webhooks/*","priority":1,"enabled":true}'
```

`action`: `ACCEPT` (skip auth), `DROP` (block), `PASS` (fall through to auth).
`match`: `PATH`, `IP`, `CIDR`, `COUNTRY`, `ASN`, `REGION`, `METHOD`, …
An `ACCEPT` rule is an auth bypass — confirm first.

## SSO and identity providers

- Create an OIDC IdP: `PUT /idp/oidc` with `name, clientId, clientSecret, authUrl,
tokenUrl, identifierPath, emailPath, namePath, scopes, autoProvision`.
- Map it into an org: `PUT /idp/{idpId}/org/{orgId}` with `{roleMapping, orgMapping}`
  (JMESPath over the id_token claims).
- Dry-run the login URL: `POST /auth/idp/{idpId}/oidc/generate-url`.
- `identifierPath` decides the user key and the forwarded `Remote-User` header.
  Pangolin finds an existing user by this value (case-folded) and the IdP, and
  logs the person in as that user. So it must be unique and never reassigned.
  `sub` is the safe default. Only use `preferred_username` when the IdP
  guarantees it is unique and immutable, and ask the user first. **Changing it
  later re-keys every user from that IdP**: old users are orphaned and new ones
  provision on next login.
- Skip Pangolin's own login form for a resource: `POST /resource/{id}`
  `{"skipToIdpId":<idpId>}`. The final redirect happens client-side, so you only
  see it in a browser, not in curl.
- Login-page branding is a commercial feature; not in community builds.

## Raw TCP/UDP resources

The API call alone is not enough. A TCP/UDP resource on port N needs all three:

1. The resource and target (`mode` `tcp`/`udp`, `proxyPort` N) via API or UI.
2. A static Traefik entrypoint named exactly **`tcp-N`** (address `:N`) or
   **`udp-N`** (address `:N/udp`) in the Traefik static config. Pangolin's
   generated dynamic config refers to that name.
3. A port mapping on the **gerbil** service in the server's `docker-compose.yml`
   (Traefik runs in gerbil's network namespace): `N:N` for TCP, `N:N/udp` for
   UDP. Compose publishes TCP only unless you add `/udp`.

Then `docker compose up -d` on the server. All public services blip briefly.

## Server-side gotchas

- **DB migrations are forward-only.** A verified database backup is the only
  rollback, so find out which backend the instance uses before an upgrade:
  - SQLite (default, `config/db/`): `docker compose stop pangolin`, then tar
    `config/` and the compose file. A live SQLite DB tars corrupt.
  - PostgreSQL: the database isn't in `config/`. Take a `pg_dump` and check it
    restores before upgrading.

  Then bump tags, `pull`, `up -d`.
- After upgrading, check the **badger** plugin version in the Traefik static
  config. Badger 1.8.0 fails Traefik's plugin integrity check and gets disabled
  (traefik/traefik#14115), which silently drops auth; 1.7.0 works.
- Enterprise-only in community builds: SSH/RDP browser resources, login branding,
  HA clustering.
- Some features need a recent newt on the site (private resources via exit nodes,
  the AI gateway). Check `GET /org/{orgId}/sites` and the release notes when a
  feature does nothing.
