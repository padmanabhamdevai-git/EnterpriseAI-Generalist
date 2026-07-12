# Chapter 8 — The Model Context Protocol (MCP)

Client-side code and host configurations: this chapter *uses and audits*
servers; Chapter 9 *builds* them.

| File | Book section | Purpose |
|---|---|---|
| `mcp_explorer.py` | 8.11.1 | The protocol from the client side: connect over stdio, list capabilities, invoke a tool |
| `capability_audit.py` | 8.11.2 | Inventory every configured server → the governance report (write-capable tools flagged) |
| `config/claude_desktop_config.json` | 8.9 | The three-server walkthrough config, annotated |
| `config/cursor_mcp.json` | 8.12 | The Cursor equivalent |

## Prerequisites

- Node.js (the reference servers run via `npx`)
- Python 3.10+ with the MCP SDK: `pip install -r ../requirements.txt`
- For the knowledge-db server: the ch06 stack running, with a read-only role:

```sql
CREATE ROLE readonly_user LOGIN PASSWORD 'readonly';
GRANT SELECT ON documents, chunks TO readonly_user;
```

## Run

```bash
cd ch08
python mcp_explorer.py                 # no host needed; creates ./sandbox
python capability_audit.py config/claude_desktop_config.json
```

For the host walkthrough (book §8.9): copy the relevant config into your
platform's Claude Desktop config location (see the official docs — paths
differ by OS and change across releases), edit the filesystem path and
database URL, restart the host.

## Notes

- JSON has no comments: the config files use `_comment` keys, which hosts
  ignore. Each `_comment` justifies that server's scope — keep the
  convention; it makes security reviews instant.
- Package names (`@modelcontextprotocol/server-*`), SDK APIs, and host
  config paths move quickly in this young ecosystem. If something fails,
  check the official MCP docs first — the *concepts* (initialize → list →
  call) are stable; the specifics drift.
- The filesystem server in every config here is scoped to a project or
  sandbox directory, never `$HOME`. That is not an example simplification;
  it is the point.

All companies and systems are fictional.
