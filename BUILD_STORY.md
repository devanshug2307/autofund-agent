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

Built a full MCP server with 8 tools: stake, unstake, wrap, unwrap, balance, rewards, APY comparison, and position monitoring. All support dry_run mode.

The companion `lido.skill.md` file gives agents the mental model they need before acting — rebasing mechanics, wstETH vs stETH tradeoffs, safe staking patterns. The bar: point any AI agent at the MCP server and stake ETH from a conversation with no custom code.

## Hours 8-10: Vault Monitor

The monitoring agent watches vault positions and delivers alerts in plain English:
- Yield drops? Explains why and whether action is needed
- Allocation shifts? Describes what moved and reassures it's normal
- Below your floor? Critical alert with alternatives

Formatted for Telegram delivery. Designed for humans who don't speak DeFi.

## The Closed Loop (Proven)

```
Deposit $1,000 → Lock principal → Earn 3.5% APY from Lido
  → Harvest $50 yield → Pay $0.003 for 5 LLM inferences
    → Provide 3 portfolio analyses at $1 each → Earn $3.00
      → Net profit: $2.997 → Reinvest → Cycle continues
```

17 tests. All passing. The loop works.

## What We Learned

1. **Smart contracts are the real guardrails.** Policy documents can be ignored. EVM code can't.
2. **Self-sustaining economics are achievable.** Even at low volumes, yield + services > inference costs.
3. **MCP servers make DeFi accessible.** An agent shouldn't need to understand Solidity to stake ETH.
4. **Plain English matters.** The vault monitor report is more useful than any dashboard.

## What's Next

AutoFund is a prototype for autonomous agent economics. The next step is mainnet deployment with real yield, real services, and real revenue. We're exploring the Protocol Labs Founders Forge accelerator path.

The future isn't agents funded by humans. It's agents that fund themselves.
