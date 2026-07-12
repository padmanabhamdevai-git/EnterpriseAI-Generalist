# Chapter 9 — Building and Securing MCP Servers

Two server shapes done the way that passes a review board: the MEDIATOR
(the server is the security boundary) and the WRAPPER (delegate to an
already-governed service). Plus a teaching MCP-aware gateway.

| File | Book section | Purpose |
|---|---|---|
| `orders_server.py` | 9.11.1 | MEDIATOR: service identity, task-grain tools, server-side cost-center authz |
| `knowledge_server.py` | 9.11.2 | WRAPPER: delegated identity (token exchange) into ch06 /ask; RLS does the authz |
| `gateway.py` | 9.11.3 | Teaching MCP-aware gateway: validate, coarse-authorize, exchange, throttle, log |
| `auth.py` | 9.11.3 | JWT validation + scope inspection — the four verbs (validate/inspect/exchange) |
| `audit.py` | — | Structured invocation log: the human's identity, args, decision, result |
| `erp_client.py` | — | Stub ERP behind a "read-only replica" with the SCOPED service credential |
| `knowledge_client.py` | — | Stub of the ch06 /ask call with a bearer token |
| `client_test.py` | 9.10 | Runs both servers in-process with mock tokens — entitled and under-entitled |

## Run (no IdP or ERP required)

```bash
cd ch09
cp ../ch01/.env .
pip install -r ../requirements.txt     # adds mcp, pyjwt
python client_test.py
```

`client_test.py` uses mock tokens and stubs so it runs standalone. The
*shape* is production: swap the stubs for your IdP's JWKS endpoint and your
system's API, and the identity/authorization/logging logic is unchanged.
That separability is the design lesson.

## Important teaching-code caveats

- **`gateway.py` is a teaching model, not production middleware.** In a
  real enterprise you extend your API-management platform (Apigee, SAP API
  Management, Kong) with MCP awareness — you do not ship this file.
- **The `Caller`-as-parameter pattern** in the servers is pedagogical: it
  makes the identity flow visible in one function signature. The real MCP
  SDK passes request context differently; see the SDK docs and the adapter
  note at the top of each server file.
- **Never hand-roll JWT crypto.** `auth.py` wraps PyJWT and validates all
  four claims (signature, issuer, audience, expiry). The mock verifier is
  clearly marked; swap in real JWKS validation for anything real.

## The first law (framed on the wall)

> A server can do only what its credential permits — never what the model
> requests, and never what the user hopes.

Every design choice here answers one question per tool: *what is the
smallest credential that lets this tool do its job?*

All companies, systems, and credentials are fictional.
