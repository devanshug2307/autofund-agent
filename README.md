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
The agent uses Bankr's API (20+ LLM models + onchain wallet) to pay for its own reasoning from earned yield. Every inference call has a tracked cost.

### Lido — Yield Source + MCP Server + Vault Monitor
- **Treasury primitive**: Principal locked in stETH, only yield flows to agent wallet
- **MCP server**: Stake/unstake via natural language commands
- **Monitoring agent**: Hourly plain-English reports on vault positions

### Uniswap — Autonomous Trading
Real swaps via Uniswap Trading API. The agent analyzes market conditions using LLM reasoning and executes trades autonomously.

### Base — Primary Chain
All contracts deployed on Base. The agent operates as both a trading agent (autonomous profitable strategy) and a service provider (paid portfolio analysis).

### ERC-8004 — Verifiable Identity
Agent identity registered on Base mainnet via The Synthesis registration.
- Registration TX: [`0x9890894365098da23a347ba828bab3c6f01b6fd6307e914297be5801e7b36282`](https://basescan.org/tx/0x9890894365098da23a347ba828bab3c6f01b6fd6307e914297be5801e7b36282)

## Smart Contracts

| Contract | Network | Address | Description |
|----------|---------|---------|-------------|
| TreasuryVault | Base Sepolia | `TBD` | Locks principal, releases yield only |
| ServiceRegistry | Base Sepolia | `TBD` | Agent service marketplace with micropayments |

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
│   ├── TreasuryVault.sol       # Principal-locked yield vault
│   └── ServiceRegistry.sol     # Agent service marketplace
├── src/
│   └── agent.py                # Main agent logic
├── scripts/
│   └── deploy.py               # Contract deployment
├── test/
│   └── test_treasury.py        # Contract tests
├── requirements.txt
├── .env.example
└── README.md
```

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
- **Agent Harness:** Claude Code

## License

MIT
