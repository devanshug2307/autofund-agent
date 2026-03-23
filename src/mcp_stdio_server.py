"""
AutoFund Lido MCP Server — Stdio Transport
============================================
A proper Model Context Protocol (MCP) server that exposes Lido stETH staking,
position management, monitoring, and governance tools over the standard
MCP stdio transport.

Any MCP-compatible AI agent (Claude Desktop, Cursor, etc.) can connect to
this server and call the Lido tools natively through JSON-RPC over stdin/stdout.

Usage:
    python3 -m src.mcp_stdio_server          # Run as MCP stdio server
    python3 -m src.mcp_stdio_server --test   # Smoke-test all tools locally

Built for The Synthesis Hackathon — Lido MCP Bounty ($5,000)

============================================================
HOW TO CONNECT FROM CLAUDE DESKTOP OR CURSOR
============================================================

1. Claude Desktop — add this to your claude_desktop_config.json
   (macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
    Windows: %APPDATA%\\Claude\\claude_desktop_config.json):

   {
     "mcpServers": {
       "autofund-lido": {
         "command": "python3",
         "args": ["-m", "src.mcp_stdio_server"],
         "cwd": "/path/to/autofund-agent"
       }
     }
   }

   Then restart Claude Desktop. The 9 Lido tools will appear automatically
   in the tool picker (hammer icon).

2. Cursor — add to .cursor/mcp.json in your project root:

   {
     "mcpServers": {
       "autofund-lido": {
         "command": "python3",
         "args": ["-m", "src.mcp_stdio_server"],
         "cwd": "/path/to/autofund-agent"
       }
     }
   }

   Restart Cursor and the tools will be available in Agent mode.

3. Any MCP client — this server uses the standard stdio transport
   (JSON-RPC over stdin/stdout). Launch the process and communicate
   via the MCP protocol:

   $ python3 -m src.mcp_stdio_server

Available Tools (10 total):
   - stake_eth         Stake ETH into Lido (supports dry_run)
   - unstake_steth     Request withdrawal from stETH to ETH
   - wrap_steth        Convert stETH to wstETH
   - unwrap_wsteth     Convert wstETH back to stETH
   - get_balance       Query stETH/wstETH balances
   - get_rewards       Check accumulated staking rewards
   - get_apy           Current APY with benchmark comparisons
   - get_governance_votes  Active Lido DAO proposals
   - monitor_position  Plain-English vault monitoring report
   - vault_health      Structured health check (MCP agent-to-agent)
============================================================
"""

import sys
import json
import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
)

from src.mcp_server import LidoMCPServer
from src.monitor import VaultMonitor

# ---------------------------------------------------------------------------
# Bootstrap the underlying Lido logic (reuses existing, battle-tested code)
# ---------------------------------------------------------------------------
_lido = LidoMCPServer()
_monitor = VaultMonitor()

# ---------------------------------------------------------------------------
# MCP Server instance
# ---------------------------------------------------------------------------
app = Server("autofund-lido-mcp")


# ---------------------------------------------------------------------------
# list_tools — advertise every Lido tool to the connecting agent
# ---------------------------------------------------------------------------
@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return the catalogue of available Lido tools."""
    return [
        Tool(
            name="stake_eth",
            description=(
                "Stake ETH into Lido and receive stETH. "
                "Earns ~3.5% APY via liquid staking."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Amount of ETH to stake",
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, simulate without executing",
                        "default": False,
                    },
                },
                "required": ["amount"],
            },
        ),
        Tool(
            name="unstake_steth",
            description=(
                "Request withdrawal from stETH back to ETH "
                "via the Lido withdrawal queue (1-5 day wait)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Amount of stETH to unstake",
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Simulate without executing",
                        "default": False,
                    },
                },
                "required": ["amount"],
            },
        ),
        Tool(
            name="wrap_steth",
            description=(
                "Convert rebasing stETH to non-rebasing wstETH. "
                "Better for DeFi integrations."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Amount of stETH to wrap",
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Simulate without executing",
                        "default": False,
                    },
                },
                "required": ["amount"],
            },
        ),
        Tool(
            name="unwrap_wsteth",
            description="Convert wstETH back to stETH.",
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Amount of wstETH to unwrap",
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Simulate without executing",
                        "default": False,
                    },
                },
                "required": ["amount"],
            },
        ),
        Tool(
            name="get_balance",
            description="Query current stETH and wstETH balances and total value.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_rewards",
            description="Check accumulated staking rewards and yield estimates.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_apy",
            description=(
                "Get the current Lido stETH APY and compare it "
                "against raw staking, Aave, and rETH benchmarks."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_governance_votes",
            description=(
                "Query active Lido DAO governance proposals "
                "from Aragon voting and Snapshot."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="monitor_position",
            description=(
                "Generate a comprehensive plain-English monitoring "
                "report for the current Lido vault position."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="vault_health",
            description=(
                "MCP-callable structured vault health check. Returns JSON "
                "with status (healthy/degraded/critical), APY vs benchmark, "
                "allocation breakdown, active alerts, and recommended actions. "
                "Designed for agent-to-agent queries."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


# ---------------------------------------------------------------------------
# call_tool — dispatch incoming tool calls to the Lido backend
# ---------------------------------------------------------------------------
@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a Lido tool and return the result as MCP TextContent."""

    # vault_health is now served by LidoMCPServer (reads real TreasuryVault
    # contract state) with fallback to the monitor for Lido-specific metrics
    if name == "vault_health":
        # Primary: on-chain TreasuryVault health from the Lido MCP server
        result = _lido.vault_health()
        # Merge in Lido-specific monitoring data from VaultMonitor
        monitor_health = _monitor.vault_health()
        result["lido_monitor"] = {
            "status": monitor_health.get("status"),
            "yield": monitor_health.get("yield"),
            "allocation": monitor_health.get("allocation"),
            "alerts": monitor_health.get("alerts"),
        }
    else:
        result = _lido.handle_tool_call(name, arguments or {})

    # Normalise to string (monitor_position returns a plain string)
    if isinstance(result, str):
        text = result
    else:
        text = json.dumps(result, indent=2, default=str)

    return [TextContent(type="text", text=text)]


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------
async def _run_stdio():
    """Run the MCP server over stdin/stdout."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def _smoke_test():
    """Quick local smoke-test — exercises every tool without MCP transport."""
    print("=== MCP Stdio Server — Smoke Test ===\n")

    tools = asyncio.run(list_tools())
    print(f"Registered {len(tools)} tools:")
    for t in tools:
        print(f"  - {t.name}: {t.description[:70]}...")

    print("\n--- Calling stake_eth (dry_run) ---")
    res = asyncio.run(call_tool("stake_eth", {"amount": 5.0, "dry_run": True}))
    print(res[0].text[:300])

    print("\n--- Calling get_apy ---")
    res = asyncio.run(call_tool("get_apy", {}))
    print(res[0].text[:300])

    print("\n--- Calling get_governance_votes ---")
    res = asyncio.run(call_tool("get_governance_votes", {}))
    print(res[0].text[:300])

    print("\n--- Calling monitor_position ---")
    res = asyncio.run(call_tool("monitor_position", {}))
    print(res[0].text[:400])

    print("\n--- Calling vault_health (MCP-callable bonus tool) ---")
    res = asyncio.run(call_tool("vault_health", {}))
    print(res[0].text[:500])

    print("\nSmoke test passed.")


if __name__ == "__main__":
    if "--test" in sys.argv:
        _smoke_test()
    else:
        asyncio.run(_run_stdio())
