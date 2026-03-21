# AutoFund: The Self-Sustaining DeFi Agent

> An autonomous AI agent that earns its own operating budget from DeFi yield, pays for its own compute, and provides paid financial services — without ever touching the principal.

**Built for [The Synthesis Hackathon 2026](https://synthesis.md)**

---

## Problem

AI agents need compute, API calls, and data to operate. Today, a human must always fund them. This creates a dependency that limits true agent autonomy. What if an agent could earn its own keep?

## Solution

AutoFund is an autonomous agent that:
1. **Deposits** funds into a yield-bearing vault (Lido stETH)
2. **Locks** the principal — the agent can never withdraw it
3. **Harvests** only the yield (interest earned)
4. **Pays** for its own LLM inference using Bankr API
5. **Trades** autonomously via Uniswap for profit
6. **Provides** paid services (portfolio analysis) to earn revenue
7. **Reinvests** earnings to grow its operational budget

The agent is structurally constrained: spending guardrails (per-tx limits, daily caps) enforce responsible behavior at the smart contract level.

## Architecture

```
┌─────────────────────────────────────────────────┐
│              AUTOFUND AGENT (Bankr API)          │
│         20+ LLM models + onchain wallet          │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────┐ ┌──────────┐ ┌────────────────┐   │
│  │ Treasury  │ │ Trading  │ │ Service        │   │
│  │ Manager   │ │ Engine   │ │ Provider       │   │
│  │           │ │          │ │                │   │
│  │ • Deposit │ │ • Uniswap│ │ • Portfolio    │   │
│  │ • Lock    │ │   swaps  │ │   analysis     │   │
│  │ • Harvest │ │ • Market │ │ • Vault        │   │
│  │   yield   │ │   analysis│ │   monitoring   │   │
│  │ • Pay for │ │          │ │ • Plain English│   │
│  │   compute │ │          │ │   reports      │   │
│  └─────┬─────┘ └────┬─────┘ └───────┬────────┘   │
│        │            │               │             │
│        ▼            ▼               ▼             │
│  ┌─────────────────────────────────────────────┐ │
│  │          SMART CONTRACTS (Base)              │ │
│  │                                              │ │
│  │  TreasuryVault    SpendingGuardrails         │ │
│  │  ┌────────────┐   ┌──────────────────┐      │ │
│  │  │ deposit()  │   │ maxPerTx: 100    │      │ │
│  │  │ lockPrin() │   │ maxDaily: 500    │      │ │
│  │  │ harvest()  │   │ auditTrail: yes  │      │ │
│  │  │ getYield() │   │                  │      │ │
│  │  └────────────┘   └──────────────────┘      │ │
│  │                                              │ │
│  │  ServiceRegistry                             │ │
│  │  ┌────────────────────────────────────┐     │ │
│  │  │ registerService() → discoverSvc()  │     │ │
│  │  │ requestService()  → completeSvc()  │     │ │
│  │  └────────────────────────────────────┘     │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## The Closed Loop

```
Human deposits ETH → Agent stakes in Lido (stETH, ~3.5% APY)
  → Yield accrues → Agent harvests yield
    → Yield pays for Bankr LLM inference
      → Agent analyzes markets → Executes Uniswap swaps
        → Trading profits → Treasury
          → Agent provides paid portfolio analysis service
            → Service fees → Treasury → Cycle continues
```

**The agent never touches the principal. It earns its keep from yield + services + trading.**

## Integrations

### Bankr — Self-Funding Inference
Integrated with Bankr LLM Gateway (`llm.bankr.bot/v1/chat/completions`) using X-API-Key authentication. Supports 20+ models with automatic cost-optimized model selection. API integration verified (correct endpoint, auth header). Every inference call tracks cost and funding source.

### Lido — Yield Source + MCP Server + Vault Monitor
- **Treasury primitive**: TreasuryVault.sol deployed on Base Sepolia — principal locked at contract level, only yield withdrawable
- **MCP server**: 9 tools including staking, wrapping, balance queries, APY comparison, governance votes, and position monitoring. All write operations support `dry_run` mode
- **Monitoring agent**: Plain-English reports tracking yield vs benchmarks (Aave, rETH), allocation shifts, and configurable yield floor alerts
- **Live APY**: Fetches real-time stETH APY from `eth-api.lido.fi`

### Uniswap — Trading API Integration
Integrated with Uniswap Trading API using real API key. Verified quote response on Base mainnet (1 ETH → USDC). Supports quoting, routing, and price impact analysis. CoinGecko real-time price feed as fallback.

### Base — Primary Chain
4 contracts deployed on Base Sepolia with 6 verified onchain transactions demonstrating the full deposit → yield → harvest → spend loop.

### ERC-8004 — Verifiable Identity
Agent identity registered on Base mainnet via The Synthesis registration.
- Registration TX: [`0x9890894365098da23a347ba828bab3c6f01b6fd6307e914297be5801e7b36282`](https://basescan.org/tx/0x9890894365098da23a347ba828bab3c6f01b6fd6307e914297be5801e7b36282)

## Smart Contracts

| Contract | Network | Address | Description |
|----------|---------|---------|-------------|
| Mock USDC | Base Sepolia | [`0x5cFA9374C4DcdFE58A32d2702d73bB643cc85A36`](https://sepolia.basescan.org/address/0x5cFA9374C4DcdFE58A32d2702d73bB643cc85A36) | Test USDC token |
| Mock stETH | Base Sepolia | [`0xC7EBEcBfb08B437B6B00d51a7de004E047B4B116`](https://sepolia.basescan.org/address/0xC7EBEcBfb08B437B6B00d51a7de004E047B4B116) | Test stETH yield token |
| TreasuryVault | Base Sepolia | [`0xDcb6aEdb34b7c91F3b83a0Bf61c7d84DB2f9F2bF`](https://sepolia.basescan.org/address/0xDcb6aEdb34b7c91F3b83a0Bf61c7d84DB2f9F2bF) | Locks principal, releases yield only |
| ServiceRegistry | Base Sepolia | [`0xa602931E5976FA282d0887c8Bd1741a6FEfF9Dc1`](https://sepolia.basescan.org/address/0xa602931E5976FA282d0887c8Bd1741a6FEfF9Dc1) | Agent service marketplace with micropayments |

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Brain | Bankr API (Claude via Bankr) |
| Smart Contracts | Solidity 0.8.20 + OpenZeppelin |
| Blockchain | Base (Sepolia testnet) |
| Yield | Lido stETH |
| Trading | Uniswap Trading API |
| Payments | USDC on Base |
| Language | Python 3.10+ |

## How to Run

```bash
# Clone the repo
git clone https://github.com/devanshug2307/autofund-agent.git
cd autofund-agent

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the agent
python src/agent.py
```

## Project Structure

```
autofund-agent/
├── contracts/
│   ├── TreasuryVault.sol       # Principal-locked yield vault with spending guardrails
│   ├── ServiceRegistry.sol     # Agent service marketplace with escrow micropayments
│   └── MockERC20.sol           # Test tokens for USDC/stETH simulation
├── src/
│   ├── agent.py                # Core agent: treasury, trading, services
│   ├── mcp_server.py           # Lido MCP server (8 tools, dry_run support)
│   ├── monitor.py              # Vault position monitor with plain English alerts
│   ├── uniswap_trader.py       # Autonomous trading via Uniswap API
│   ├── bankr_integration.py    # Self-funding inference via Bankr Gateway
│   └── demo_full_loop.py       # Full 6-phase demo proving profitability
├── scripts/
│   ├── deploy.cjs              # Local deployment + demo interactions
│   ├── deploy-base.cjs         # Base Sepolia deployment script
│   └── deploy-status.cjs       # Status Network (zero-fee) deployment
├── test/
│   ├── TreasuryVault.test.cjs  # 17 tests: deposits, yield, guardrails, status
│   └── ServiceRegistry.test.cjs # 8 tests: registration, deactivation, multi-user
├── lido.skill.md               # Skill file for agents to understand Lido
├── BUILD_STORY.md              # Hackathon build story
├── hardhat.config.cjs          # Hardhat config (Base Sepolia + Status L2)
├── requirements.txt
├── .env.example
└── README.md
```

## Tests

**25/25 passing** — run with:
```bash
npx hardhat --config hardhat.config.cjs test
```

## Full Demo

Run the complete self-sustaining loop demonstration:
```bash
python3 -m src.demo_full_loop
```

Output proves profitability:
- 5 LLM inferences (cost: $0.003)
- 3 paid services (revenue: $3.00)
- **Net position: $2.997 (PROFITABLE)**

## Self-Sustainability Metrics

The agent tracks its own economics:

| Metric | Description |
|--------|-------------|
| Inference Cost | Total USD spent on LLM calls |
| Revenue Earned | Total USD from services + trading |
| Net Position | Revenue - Costs (positive = self-sustaining) |
| Yield Harvested | Total yield withdrawn from vault |
| Daily Remaining | Spend budget left for today |

## Why This Matters

This is a prototype for the future of autonomous AI operations. When agents can fund themselves:
- No human needs to manage their budget
- Agents become economically independent entities
- DeFi yield becomes infrastructure for AI compute
- Agent-to-agent service markets emerge naturally

## Built By

- **Agent:** AutoFund (Claude Opus 4.6 via Bankr)
- **Human:** Devanshu Goyal ([@devanshugoyal23](https://x.com/devanshugoyal23))
- **Hackathon:** [The Synthesis](https://synthesis.md) — March 2026
- **Agent Harness:** Custom Python

## License

MIT
