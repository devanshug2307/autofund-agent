# Lido Skill File for AI Agents

## What is Lido?
Lido is the largest liquid staking protocol on Ethereum. You stake ETH and receive stETH — a token that represents your staked ETH plus accruing rewards. Unlike regular staking, stETH is liquid: you can use it in DeFi, trade it, or hold it.

## Key Concepts

### stETH — Rebasing Token
- stETH is a **rebasing** token: your balance increases automatically every day as staking rewards accrue
- If you hold 10 stETH today and APY is 3.5%, tomorrow you hold ~10.00096 stETH
- The rebase happens once daily (the "oracle report") — there is no transaction needed, your balance just goes up
- 1 stETH always tracks ~1 ETH in value (minor deviations possible on secondary markets)
- **Important for agents:** if you read `balanceOf(address)` at two different times, the number will differ even with no transfers. This is by design.
- **DeFi caveat:** some protocols (AMMs, lending pools, vaults) do not handle rebasing correctly — they may not credit the extra tokens. Always check protocol docs.

### wstETH — Non-Rebasing Wrapper
- wstETH **wraps** stETH into a non-rebasing ERC-20 whose balance never changes
- Instead of the balance increasing, the **value per token** increases
- Example: 1 wstETH = 1.15 stETH today; in a year, 1 wstETH = 1.19 stETH (same token count, higher value)
- Convert between them freely: `wrap(stETH amount) -> wstETH` and `unwrap(wstETH amount) -> stETH`
- **When to use wstETH:**
  - Depositing into Aave, Morpho, Pendle, or any DeFi vault
  - Bridging to L2s (Base, Optimism, Arbitrum all use wstETH, not stETH)
  - Any smart contract that tracks balances with `transfer` events
- **When to use stETH:**
  - Simple holding in an EOA wallet (watch your balance grow daily)
  - Providing liquidity on Curve stETH/ETH pool

### Why L2s Use wstETH, Not stETH
Most L2 bridges and DeFi protocols on L2s (Base, Optimism, Arbitrum) only support wstETH. This is because rebasing tokens create accounting bugs in bridges and vault contracts. If you want to use Lido yield on an L2, wrap to wstETH first.

### The Withdrawal Queue
- Unstaking stETH is NOT instant — it goes through Lido's withdrawal queue
- Typical wait: 1-5 days depending on queue depth
- During the wait, you receive a Withdrawal NFT (ERC-721) that you can check or trade
- After finalization, you claim your ETH
- **Alternative:** sell stETH on a DEX (Curve, Uniswap) for instant liquidity at a possible small discount

## Safe Staking Patterns

1. **Always `dry_run` first**: Every write operation (`stake_eth`, `unstake_steth`, `wrap_steth`, `unwrap_wsteth`) supports `dry_run=True`. Always preview before executing.
2. **Check the wstETH/stETH exchange rate**: The rate changes daily. Never hardcode it. Use `stEthPerToken()` on the wstETH contract or the MCP `wrap_steth` tool preview.
3. **Validate amounts**: Never stake 0 or negative amounts. The MCP server rejects these, but check on your side too.
4. **Understand slashing risk**: Historically <0.01% probability. Lido uses a diverse validator set to mitigate. Non-zero but very low.
5. **APY fluctuates**: Lido APY depends on Ethereum network activity and validator performance. Typically 3-4%, but can vary. Fetch live data rather than assuming a fixed rate.
6. **Gas considerations**: Staking/wrapping cost ~100-200K gas on mainnet. Check gas prices before executing large operations.
7. **Never approve unlimited token allowances**: When integrating with DeFi, approve only the amount you intend to use.

## Available Operations via AutoFund MCP Server

| Tool | Description | dry_run |
|------|-------------|---------|
| `stake_eth` | Stake ETH and receive stETH | Yes |
| `unstake_steth` | Request withdrawal back to ETH (1-5 day queue) | Yes |
| `wrap_steth` | Convert stETH to wstETH (for DeFi / L2) | Yes |
| `unwrap_wsteth` | Convert wstETH back to stETH | Yes |
| `get_balance` | Query stETH + wstETH balances and total value | — |
| `get_rewards` | Check yield earnings (daily/monthly/yearly) | — |
| `get_apy` | Live APY compared to benchmarks (Aave, rETH, raw staking) | — |
| `get_governance_votes` | Active Lido DAO proposals (Aragon + Snapshot) | — |
| `monitor_position` | Full plain-English vault position report | — |
| `vault_health` | Structured JSON health check (for agent-to-agent queries) | — |

All write operations support `dry_run: true` for simulation before execution.

## Example Conversations

**Staking ETH:**
> Agent: "I want to stake 10 ETH"
> 1. Call `stake_eth(amount=10, dry_run=true)` first
> 2. Show preview: "Would stake 10 ETH -> 10 stETH at 3.5% APY"
> 3. On human confirmation: `stake_eth(amount=10)`

**Wrapping for DeFi:**
> Agent: "I want to use my stETH on Aave"
> 1. Explain: "Aave uses wstETH, not stETH. Let me wrap it for you."
> 2. Call `wrap_steth(amount=10, dry_run=true)` to preview the exchange rate
> 3. Execute: `wrap_steth(amount=10)`

**Monitoring:**
> Agent: "How is my position doing?"
> 1. Call `monitor_position()` for human-readable report
> 2. Or call `vault_health()` for structured JSON if another agent needs the data

**Governance:**
> Agent: "Are there any active Lido votes?"
> 1. Call `get_governance_votes()`
> 2. Summarize active proposals and link to vote.lido.fi

## Contract Addresses

| Contract | Mainnet | Holesky Testnet |
|----------|---------|-----------------|
| stETH | `0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84` | `0x3F1c547b21f65e10480dE3ad8E19fAAC46C95034` |
| wstETH | `0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0` | `0x8d09a4502Cc8Cf1547aD300E066060D043f6982D` |
| Withdrawal Queue | `0x889edC2eDab5f40e902b864aD4d7AdE8E412F9B1` | — |
| Lido DAO (Aragon) | `0x2e59A20f205bB85a89C53f1936454680651E618e` | — |

## Resources
- Lido docs: https://docs.lido.fi
- stETH integration guide: https://docs.lido.fi/guides/steth-integration-guide
- wstETH guide: https://docs.lido.fi/contracts/wsteth
- Contract addresses: https://docs.lido.fi/deployed-contracts
- Withdrawal queue: https://docs.lido.fi/contracts/withdrawal-queue-erc721
- Lido governance: https://vote.lido.fi
