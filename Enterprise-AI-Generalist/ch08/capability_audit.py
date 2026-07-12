"""capability_audit.py — inventory every configured server (book 8.11.2).

Reads a host config, connects to each server, and produces the report a
security review actually needs: what can these things DO, and with what?

This is the catalog's raw material — run it before someone else's
incident review runs it for you.
"""
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

WRITE_HINTS = ("create", "write", "update", "delete", "send", "post",
               "execute", "move", "put", "set", "add", "remove")


def looks_write_capable(tool_name: str, description: str) -> bool:
    """Heuristic triage: which tools can CHANGE things? A human reviews;
    this just sorts the queue — the Ch. 7 review-queue pattern again."""
    haystack = f"{tool_name} {description}".lower()
    return any(hint in haystack for hint in WRITE_HINTS)


async def audit_server(name: str, spec: dict) -> dict:
    params = StdioServerParameters(command=spec["command"],
                                   args=spec.get("args", []))
    try:
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                info = await session.initialize()
                tools = (await session.list_tools()).tools
                return {
                    "server": name,
                    "impl": f"{info.serverInfo.name} v{info.serverInfo.version}",
                    "tool_count": len(tools),
                    "write_capable": sorted(
                        t.name for t in tools
                        if looks_write_capable(t.name, t.description or "")),
                    "read_only": sorted(
                        t.name for t in tools
                        if not looks_write_capable(t.name, t.description or "")),
                    "credential_hint": next(
                        (str(a) for a in spec.get("args", [])
                         if "://" in str(a) or str(a).startswith("/")), "n/a"),
                }
    except Exception as e:
        return {"server": name, "error": f"{type(e).__name__}: {e}"}


async def main(config_path: str) -> None:
    config = json.loads(Path(config_path).read_text())
    servers = config.get("mcpServers", {})
    print(f"auditing {len(servers)} configured server(s)...\n")

    for name, spec in servers.items():
        clean = {k: v for k, v in spec.items() if not k.startswith("_")}
        r = await audit_server(name, clean)
        if "error" in r:
            print(f"x {name}: {r['error']}")
            continue
        print(f"# {r['server']}  ({r['impl']})")
        print(f"  scope/credential: {r['credential_hint']}")
        print(f"  {r['tool_count']} tools — "
              f"{len(r['write_capable'])} write-capable:")
        for t in r["write_capable"]:
            print(f"    ! {t}")
        print(f"  read-only: {', '.join(r['read_only'][:6])}"
              f"{' ...' if len(r['read_only']) > 6 else ''}\n")

    print("Questions this report should trigger (per server):")
    print("  1. Is this in the approved catalog?  2. Is the credential")
    print("  scoped to least privilege?  3. Which write tools need")
    print("  Copilot-grade approval?  4. Who reviewed the server's code?")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1
                     else "config/claude_desktop_config.json"))
