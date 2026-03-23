# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoFund is an autonomous DeFi agent built for The Synthesis Hackathon 2026. It earns its own operating budget from DeFi yield, pays for its own LLM inference via Bankr API, provides paid financial services, and trades via Uniswap — all without touching locked principal. A secondary project (project3-vaultguard/) implements private AI reasoning with public verifiable actions.

## Build & Test Commands

```bash
# Install dependencies (both ecosystems)
npm install
pip install -r requirements.txt

# Run all 47 Solidity tests
npx hardhat --config hardhat.config.cjs test

# Run all 63 Python tests
python3 -m pytest tests/ -v

# Compile contracts
npx hardhat --config hardhat.config.cjs compile

# Deploy to Base Sepolia
npx hardhat --config hardhat.config.cjs run scripts/deploy-base.cjs --network baseSepolia

# Run the full profitability demo (6-phase Python demo)
python3 -m src.demo_full_loop

# Run as autonomous daemon (continuous operation)
python3 -m src.daemon --cycles 3 --interval 60

# Start the HTTP service API
uvicorn src.service_api:app --host 0.0.0.0 --port 8000

# Run MCP stdio server (for Claude Desktop / Cursor)
python3 -m src.mcp_stdio_server
# Smoke test: python3 -m src.mcp_stdio_server --test
```

For project3-vaultguard, run from its directory with its own hardhat.config.cjs.

## Architecture

The repo is a **dual-stack** project: Solidity smart contracts (Hardhat/Node) + Python agent logic.

### Smart Contracts (contracts/)
- **TreasuryVault.sol** — Principal-locked yield vault. Deposits lock as principal; only yield is withdrawable. Spending guardrails: $100/tx max, $500/day cap. 31 Solidity tests prove principal can never be withdrawn.
- **ServiceRegistry.sol** — On-chain service marketplace with escrow. Agent registers services, users request them, payment is escrowed until completion. 16 Solidity tests.
- **MockERC20.sol** — Test token (used as mock USDC/stETH on Base Sepolia).

Solidity version: 0.8.20 with optimizer (200 runs). Uses OpenZeppelin 5.x.

### Python Agent (src/)
All Python modules are run as `python3 -m src.<module>` from the repo root.

- **agent.py** — Core `AutoFundAgent` class. Orchestrates treasury management, trading, and services. Calls Bankr for LLM inference, tracks costs/revenue for self-sustainability metrics.
- **daemon.py** — Autonomous daemon with WAKE→SENSE→THINK→ACT→CHECK→LOG→SLEEP lifecycle. Configurable via `--cycles` and `--interval` flags. Outputs `daemon_session.json`.
- **mcp_server.py** — Lido MCP server with 9 tools (stake_eth, unstake_steth, wrap_steth, unwrap_wsteth, get_balance, get_rewards, get_apy, get_governance_votes, monitor_position). All write ops support `dry_run`.
- **mcp_stdio_server.py** — MCP JSON-RPC stdio transport wrapping the Lido MCP server.
- **monitor.py** — `VaultMonitor` that fetches live Lido APY from eth-api.lido.fi, compares against benchmarks (Aave, rETH), detects yield drops/floor breaches/allocation shifts, generates plain-English reports and Telegram-formatted alerts.
- **uniswap_trader.py** — Trading engine using Uniswap API for quotes with CoinGecko price fallback. Signal-based strategy with momentum analysis, volatility calculation, and quarter-Kelly criterion position sizing. Tracks portfolio P&L and trade history.
- **celo_integration.py** — `CeloAgent` class for Celo-specific operations: stablecoin balance tracking (cUSD/cEUR/cREAL), CIP-64 fee abstraction, MiniPay-optimized transfers, cross-border remittance via Mento, and TreasuryVault reads on Celo Sepolia.
- **bankr_integration.py** — `BankrGateway` for self-funding LLM calls. Selects optimal model by task complexity (Gemini Flash for simple → Claude Opus for critical). Fallback chain: Bankr → Anthropic → simulation.
- **self_check.py** — `SelfChecker` runs 6 verification checks per daemon cycle (principal intact, yield non-negative, budget not exhausted, etc.).
- **service_api.py** — FastAPI service with discovery endpoints, portfolio analysis, vault monitoring, Lido operations, and agent status. Premium endpoints (`/portfolio/analyze`, `/vault/report`) are gated by x402 payment protocol middleware (HTTP 402 flow, fail-closed — unpaid requests always get 402) on Base Sepolia via facilitator at `https://x402.org/facilitator`.
- **demo_full_loop.py** — 6-phase demo proving the full profitability loop.

### Key Data Flow
```
User/MCP Client → service_api.py or mcp_stdio_server.py
  → AutoFundAgent (agent.py) orchestrates:
    → BankrGateway (LLM inference, self-funded from yield)
    → UniswapTrader (market quotes, trade execution)
    → VaultMonitor (position monitoring, alerts)
    → SelfChecker (post-cycle verification)
  → Smart Contracts on Base Sepolia (TreasuryVault, ServiceRegistry)
  → External APIs (Lido, CoinGecko, Uniswap, Bankr)
```

### Tests (test/)
- **TreasuryVault.test.cjs** — Core vault tests (deposits, yield, access control, guardrails)
- **TreasuryVault.advanced.test.cjs** — Advanced edge cases (exact-limit spending, multi-day resets)
- **ServiceRegistry.test.cjs** — Full service lifecycle (register, request, escrow, complete, multi-user)

All tests use Hardhat's built-in test runner with Chai assertions (`expect`). CommonJS format (`.cjs`).

## Environment

Requires a `.env` file (see `.env.example`): RPC_URL, PRIVATE_KEY, BANKR_API_KEY, contract addresses. Deployed contract addresses are in README.md.

Networks configured in hardhat.config.cjs: `baseSepolia` (chainId 84532), `statusSepolia`.

## Conventions

- All config files use CommonJS (`.cjs`) — hardhat config, deploy scripts, tests.
- Python modules invoked as `python3 -m src.<name>` from repo root.
- The `lido.skill.md` file at repo root is a skill reference for agents interacting with Lido — not application code.
- Proof files (demo_proof.txt, mcp_proof.txt, etc.) are hackathon judge artifacts.
