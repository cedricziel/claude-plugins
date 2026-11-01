---
name: pangolin-api
description: 'How to drive a self-hosted Pangolin (fosrl/pangolin) tunnel reverse proxy through its HTTP API with curl — logging in, listing orgs/sites/domains/resources, publishing a service (resource + target), path-routed targets, auth-bypass rules, SSO and IdP settings, and raw TCP/UDP resources. Use whenever a task involves exposing, changing, or inspecting a service behind Pangolin, its newt sites, or its `/api/v1` endpoints. Triggers on: "pangolin", "newt", "gerbil", "badger", "publish this service", "add a resource", a reverse-proxied subdomain served by Pangolin.'
---

# Pangolin API

Pangolin has no published OpenAPI spec on self-hosted instances (`/openapi.json`
returns the SPA shell). Everything below comes from the fosrl/pangolin source and
live use against a 1.25 community-edition instance. When an endpoint is missing
here, read `server/routers/` in https://github.com/fosrl/pangolin — the route
definitions and their zod schemas are the real reference.

## Setup

Keep credentials out of commands and out of this skill. Load them from the user's
secret manager into env vars first:

```bash
export PANGOLIN_URL=https://pangolin.example.com   # dashboard host
export PANGOLIN_EMAIL=...                          # from the secret manager
export PANGOLIN_PASSWORD=...                       # from the secret manager
export PANGOLIN_ORG=...                            # org id, see "orgs" below
```

## Auth: session cookie + CSRF header

There are two APIs:

- **`/api/v1`** — the one the dashboard uses. Session cookie auth. This always works.
- **`/v1`** — the integration API for `Bearer <keyId>.<secret>` API keys. On many
  self-hosted installs it is **not routed** by Traefik: `/v1` hits the Next.js
  frontend (404) and a Bearer key on `/api/v1` gets 401. Exposing it needs a
  Traefik router `PathPrefix(/v1)` → the Pangolin integration port. Unless that is
  set up, use the session API.

**Every `/api/v1` call needs the header `X-CSRF-Token: x-csrf-protection`** — the
login call too. Without it requests fail with a CSRF error.

```bash
JAR=$(mktemp); H='X-CSRF-Token: x-csrf-protection'; API="$PANGOLIN_URL/api/v1"
jq -n --arg e "$PANGOLIN_EMAIL" --arg p "$PANGOLIN_PASSWORD" '{email:$e,password:$p}' \
  | curl -s -c "$JAR" -H "$H" -H 'Content-Type: application/json' -d @- "$API/auth/login"
# → {"success":true,"message":"Logged in successfully",...}

pg() { curl -s -b "$JAR" -H "$H" -H 'Content-Type: application/json' "$@"; }
pg "$API/orgs" | jq '.data.orgs[] | {orgId,name}'
```

Piping the body through `jq ... | curl -d @-` keeps the password out of `ps` and
shell history. Accounts with 2FA need `code` in the login body.

Responses wrap everything: `{data, success, error, message, status}`. List
endpoints return `data.<plural>` plus `data.pagination` `{total, pageSize, page}`;
the default page size is 20, so pass `?pageSize=200&page=1` or loop.

## Read endpoints

| What                    | Call                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------- |
| Orgs                    | `GET /orgs`                                                                           |
| Sites (newt connectors) | `GET /org/{orgId}/sites` — `siteId`, `name`, `type`, `online`                         |
| Domains                 | `GET /org/{orgId}/domains` — `domainId` (e.g. `domain1`), `baseDomain`                |
| Resources               | `GET /org/{orgId}/resources` — `resourceId`, `niceId`, `fullDomain`, `sso`, `targets` |
| One resource            | `GET /resource/{resourceId}`                                                          |
| Targets                 | `GET /resource/{resourceId}/targets`                                                  |
| Rules                   | `GET /resource/{resourceId}/rules`                                                    |
| Roles on a resource     | `GET /resource/{resourceId}/roles`                                                    |
| Users / roles           | `GET /org/{orgId}/users`, `GET /org/{orgId}/roles`                                    |
| IdPs                    | `GET /idp`                                                                            |
| API keys                | `GET /org/{orgId}/api-keys`                                                           |

Find a resource by hostname:

```bash
pg "$API/org/$PANGOLIN_ORG/resources?pageSize=500" \
  | jq '.data.resources[] | select(.fullDomain|test("^app\\.")) | {resourceId,niceId,fullDomain,sso}'
```

## Publish an HTTP service

Three calls. `PUT` creates, `POST` updates.

```bash
# 1. resource → returns data.resourceId
pg -X PUT "$API/org/$PANGOLIN_ORG/resource" \
  -d '{"name":"app","subdomain":"app","domainId":"domain1","mode":"http"}'

# 2. target on a site (the upstream as seen from that site's newt)
pg -X PUT "$API/resource/$RID/target" \
  -d '{"siteId":1,"ip":"10.0.0.5","port":8080,"method":"http","enabled":true}'

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
pg -X PUT "$API/resource/$RID/target" -d '{"siteId":1,"ip":"10.0.0.5","port":8081,
  "method":"http","enabled":true,"path":"/ws","pathMatchType":"prefix","priority":200}'
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
  Use `preferred_username` rather than `sub` if downstream apps expect a readable
  name. **Changing it later re-keys every user from that IdP**: old users are
  orphaned and new ones provision on next login.
- Skip Pangolin's own login form for a resource: `POST /resource/{id}`
  `{"skipToIdpId":<idpId>}`. The final redirect happens client-side, so you only
  see it in a browser, not in curl.
- Login-page branding is a commercial feature; not in community builds.

## Raw TCP/UDP resources

The API call alone is not enough. A TCP/UDP resource on port N needs all three:

1. The resource and target (`mode` `tcp`/`udp`, `proxyPort` N) via API or UI.
2. A static Traefik entrypoint named exactly **`tcp-N`** (or `udp-N`) in the
   Traefik static config. Pangolin's generated dynamic config refers to that name.
3. A `N:N` port mapping on the **gerbil** service in the server's
   `docker-compose.yml` (Traefik runs in gerbil's network namespace).

Then `docker compose up -d` on the server. All public services blip briefly.

## Server-side gotchas

- **DB migrations are forward-only.** Before an upgrade: `docker compose stop
pangolin`, tar `config/` + the compose file (a live sqlite DB tars corrupt),
  then bump tags, `pull`, `up -d`. The tarball is the only rollback.
- After upgrading, check the **badger** plugin version in the Traefik static
  config. Badger 1.8.0 fails Traefik's plugin integrity check and gets disabled
  (traefik/traefik#14115), which silently drops auth; 1.7.0 works.
- Enterprise-only in community builds: SSH/RDP browser resources, login branding,
  HA clustering.
- Some features need a recent newt on the site (private resources via exit nodes,
  the AI gateway). Check `GET /org/{orgId}/sites` and the release notes when a
  feature does nothing.
