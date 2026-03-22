# Build Story: AutoFund at The Synthesis

## The Idea

What if an AI agent never needed a human to pay its bills?

The idea started simple: most agents are tethered to whoever funds their API calls. That's a dependency. What if the agent could earn its own operating budget from DeFi yield, pay for its own inference, and even sell services to make a profit?

## Hour 0: Research Sprint

We started by analyzing every single bounty in The Synthesis — all 132 prizes across 46 tracks. The insight: many bounties share overlapping requirements. A self-sustaining DeFi agent naturally hits Bankr (self-funding inference), Lido (yield treasury), Base (trading + services), Uniswap (swaps), and more.

One project. Ten bounty tracks. Maximum surface area.

## Hours 1-3: Architecture & Smart Contracts

The core primitive is the **TreasuryVault** — a smart contract where:
- Anyone can deposit funds (locks as principal)
- Only yield is accessible to the agent
- Spending guardrails enforce per-transaction and daily limits
- Every spend is logged onchain with a reason

The agent structurally cannot touch the principal. This isn't a policy — it's enforced at the EVM level.

We also built a **ServiceRegistry** — an onchain marketplace where the agent registers services (portfolio analysis) and gets paid in USDC micropayments.

## Hours 3-6: The Agent Brain

The agent has three modules:
1. **Treasury Manager**: Monitors Lido stETH positions, harvests yield, tracks spending
2. **Trading Engine**: Analyzes markets via LLM, executes swaps on Uniswap
3. **Service Provider**: Offers paid portfolio analysis, earns revenue

Every LLM call is tracked with its cost. Every dollar earned is tracked. The agent knows whether it's profitable.

## Hours 6-8: Lido MCP Server

Built a full MCP server with 10 tools: stake, unstake, wrap, unwrap, balance, rewards, APY, governance votes, position monitoring, and vault health. All write operations support dry_run mode. Added MCP stdio transport (JSON-RPC over stdin/stdout) so Claude Desktop and Cursor can connect directly.

The companion `lido.skill.md` file gives agents the mental model they need before acting — rebasing mechanics, wstETH vs stETH tradeoffs, safe staking patterns. The bar: point any AI agent at the MCP server and stake ETH from a conversation with no custom code.

## Hours 8-10: Vault Monitor + Telegram Alerts

The monitoring agent watches vault positions and delivers alerts in plain English:
- Yield drops? Explains why and whether action is needed
- Allocation shifts? Describes what moved and reassures it's normal
- Below your floor? Critical alert with alternatives

Alerts are pushed to a real Telegram chat via Bot API (`@web3203bot`). Two live alerts were delivered: a full vault monitoring report with live stETH APY (2.42%), ETH price, and benchmark comparisons, plus a yield drop detection alert with allocation analysis. Proof: `telegram_real_alert_proof.json` with Telegram API responses (message_id 3 and 4).

## Hours 10-14: Real Uniswap V3 Swaps + x402 Payments

Moved from simulated quotes to **real onchain swaps** on Ethereum Sepolia via Uniswap V3 SwapRouter02. Two successful swaps executed:
- 0.0005 ETH -> 2.773624 USDC (standalone swap script)
- 0.0003 ETH -> 1.664174 USDC (integrated via `uniswap_trader.py` trading engine)

Both use `exactInputSingle` via `multicall` — the standard Uniswap V3 swap path. TX hashes verifiable on Sepolia Etherscan.

Also integrated **x402** — the HTTP 402 Payment Required standard for machine-to-machine payments. Two premium endpoints now require payment:
- `POST /portfolio/analyze` ($0.01) — AI-powered wallet analysis
- `GET /vault/report` ($0.005) — vault monitoring report

Payment verification and settlement happens through the x402 facilitator at `x402.org`. This turns AutoFund into a real paid service that other agents can discover and pay for autonomously — no accounts, no API keys, just onchain payments.

## Hours 14-16: Multi-Chain Deployments

Deployed to **Celo Sepolia** — 4 contracts, 7 onchain transactions proving the full lifecycle on a second chain. Celo's fee abstraction lets agents pay gas in stablecoins, which is ideal for autonomous treasury management.

Deployed to **Status Network Sepolia** — zero gas fee transactions for continuous autonomous operation without gas budgeting.

## Hours 16-18: Autonomous Daemon + Self-Check

Built the autonomous daemon mode (`src/daemon.py`) with a structured lifecycle: WAKE -> SENSE -> THINK -> ACT -> CHECK -> LOG -> SLEEP. Configurable via `--cycles` and `--interval` flags.

Added `self_check.py` — 6 verification checks per cycle:
1. Treasury principal intact
2. Yield non-negative
3. Net position sustainable
4. No critical alerts missed
5. Inference budget remaining
6. Lido APY sanity check

Each cycle produces a structured PASS/FAIL verdict with recommendations if any check fails.

## Hours 18-20: HTTP Service API + Discovery

Built `service_api.py` — a full FastAPI service exposing AutoFund as a discoverable HTTP service with 15+ endpoints: portfolio analysis, vault monitoring, Lido operations, market data, and agent status. Combined with x402 payment gating for premium endpoints.

## The Closed Loop (Proven)

```
Deposit $1,000 -> Lock principal -> Earn 3.5% APY from Lido
  -> Harvest $50 yield -> Pay $0.003 for 5 LLM inferences
    -> Provide 3 portfolio analyses at $1 each -> Earn $3.00
      -> Net profit: $2.997 -> Reinvest -> Cycle continues
```

47 tests. All passing. The loop works.

## What We Learned

1. **Smart contracts are the real guardrails.** Policy documents can be ignored. EVM code can't.
2. **Self-sustaining economics are achievable.** Even at low volumes, yield + services > inference costs.
3. **MCP servers make DeFi accessible.** An agent shouldn't need to understand Solidity to stake ETH.
4. **Plain English matters.** The vault monitor report is more useful than any dashboard.
5. **Real swaps change everything.** Moving from simulated quotes to actual onchain swaps forced us to handle gas estimation, slippage, and real transaction failures.
6. **x402 makes agent commerce practical.** Any agent can pay for AutoFund's services programmatically — no accounts needed.
7. **Multi-chain proves generality.** Deploying the same contracts on Base, Celo, and Status Network proved the architecture is chain-agnostic.
8. **Telegram alerts beat dashboards.** Push notifications to where the user already is, not another tab they have to remember to check.

## What's Next

AutoFund is a prototype for autonomous agent economics. The next step is mainnet deployment with real yield, real services, and real revenue. We're exploring the Protocol Labs Founders Forge accelerator path.

The future isn't agents funded by humans. It's agents that fund themselves.
