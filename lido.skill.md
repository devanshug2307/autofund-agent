# Lido Skill File for AI Agents

## What is Lido?
Lido is the largest liquid staking protocol on Ethereum. You stake ETH and receive stETH — a token that represents your staked ETH plus accruing rewards. Unlike regular staking, stETH is liquid: you can use it in DeFi, trade it, or hold it.

## Key Concepts

### stETH (Rebasing)
- stETH balance increases daily as staking rewards accrue
- 1 stETH always represents 1 ETH of staked value plus accumulated rewards
- Good for: holding, simple yield earning

### wstETH (Non-Rebasing Wrapper)
- wstETH balance stays constant; its value increases instead
- 1 wstETH = 1.15+ stETH (and growing)
- Good for: DeFi protocols, smart contract integrations, L2s

### Why wstETH on L2s?
Most L2s (Base, Optimism, Arbitrum) use bridged wstETH, not stETH. This is because rebasing tokens create accounting complexity for bridges and DeFi protocols.

## Safe Staking Patterns

1. **Always dry_run first**: Test every operation before executing
2. **Check exchange rates**: wstETH/stETH rate changes daily
3. **Withdrawal queue**: Unstaking takes 1-5 days via the withdrawal queue
4. **Slashing risk**: Very low (<0.01% historically) but non-zero
5. **APY fluctuates**: Based on network activity, typically 3-4%

## Available Operations via AutoFund MCP Server

| Tool | Description |
|------|-------------|
| `stake_eth` | Stake ETH → receive stETH |
| `unstake_steth` | Request withdrawal back to ETH |
| `wrap_steth` | Convert stETH → wstETH |
| `unwrap_wsteth` | Convert wstETH → stETH |
| `get_balance` | Query all balances |
| `get_rewards` | Check yield earnings |
| `get_apy` | Compare APY with benchmarks |
| `monitor_position` | Full plain English report |

All write operations support `dry_run: true` for simulation.

## Example Conversation

**Agent**: "I want to stake 10 ETH"
→ Calls `stake_eth(amount=10, dry_run=true)` first
→ Shows preview: "Would stake 10 ETH → 10 stETH at 3.5% APY"
→ On confirmation: `stake_eth(amount=10)`

**Agent**: "How is my position doing?"
→ Calls `monitor_position()`
→ Returns full report with yield, benchmarks, and recommendations

## Resources
- Lido docs: https://docs.lido.fi
- stETH integration guide: https://docs.lido.fi/guides/steth-integration-guide
- Contract addresses: https://docs.lido.fi/deployed-contracts
- Withdrawal queue: https://docs.lido.fi/contracts/withdrawal-queue-erc721
