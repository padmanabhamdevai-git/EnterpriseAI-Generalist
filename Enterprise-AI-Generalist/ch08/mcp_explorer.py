"""mcp_explorer.py — the client side of MCP, demystified (book 8.11.1).

Launches the reference filesystem server as a child process, speaks the
protocol over stdio, lists its tools, and invokes one. This is what your
host does at startup and on every tool call — no more, no less.

When a server misbehaves in production, this fifty-line pattern IS your
diagnostic harness: connect directly, list, invoke — and you've isolated
whether the fault is the server, the host, or the model's tool selection.
"""
import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# The same server Claude Desktop launches — scoped to a sandbox dir we create.
SANDBOX = Path(__file__).parent / "sandbox"
SANDBOX.mkdir(exist_ok=True)
(SANDBOX / "hello.md").write_text("# Hello from the sandbox\nMCP was here.\n")

SERVER = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", str(SANDBOX)],
)


async def main() -> None:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            # 1 · CONNECT & NEGOTIATE
            init = await session.initialize()
            print(f"connected: {init.serverInfo.name} "
                  f"v{init.serverInfo.version}\n")

            # 2 · DISCOVER — these definitions are what lands in the
            #     model's context; read them the way the model will.
            tools = await session.list_tools()
            print(f"{len(tools.tools)} tools exposed:")
            for t in tools.tools:
                print(f"  {t.name:<22} {(t.description or '')[:60]}")

            # 3 · INVOKE — what the host does after the model asks
            #     and the user approves.
            result = await session.call_tool(
                "read_text_file", {"path": str(SANDBOX / "hello.md")}
            )
            print("\nread_text_file result:")
            print(f"  {result.content[0].text!r}")

            print("\nThat's the whole protocol: initialize, list, call.")
            print("The host adds three things around it: the model, the")
            print("approval policy, and — in an enterprise — the audit log.")


if __name__ == "__main__":
    asyncio.run(main())
