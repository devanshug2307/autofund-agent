# PROJECT 1: AutoFund - The Self-Sustaining DeFi Agent

> **The agent that earns its own keep.**

---

## Elevator Pitch
AutoFund is an autonomous AI agent that deposits funds into DeFi yield protocols, earns interest, uses that yield to pay for its own compute and LLM inference, executes profitable trades, and offers paid financial services to other agents and humans. The principal is structurally locked - the agent can only spend what it earns.

---

## Problem Statement
AI agents need compute, API calls, and data to operate. Today, a human must always fund them. This creates a dependency that limits agent autonomy. What if an agent could earn its own operating budget from DeFi yield, trade for profit, and reinvest its earnings?

---

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
│  │ • Harvest │ │ • GMX    │ │ • Vault        │   │
│  │   yield   │ │   perps  │ │   monitoring   │   │
│  │ • Pay for │ │ • MoonPay│ │ • Plain English│   │
│  │   compute │ │   bridge │ │   reports      │   │
│  └─────┬─────┘ └────┬─────┘ └───────┬────────┘   │
│        │            │               │             │
├────────┼────────────┼───────────────┼─────────────┤
│        ▼            ▼               ▼             │
│  ┌─────────────────────────────────────────────┐ │
│  │          SMART CONTRACTS (Base)              │ │
│  │                                              │ │
│  │  Treasury Vault    Spending       Service    │ │
│  │  ┌────────────┐   Guardrails    Registry    │ │
│  │  │ deposit()  │   ┌──────────┐  ┌────────┐ │ │
│  │  │ lockPrin() │   │ txLimit  │  │register│ │ │
│  │  │ harvest()  │   │ dailyCap │  │discover│ │ │
│  │  │ getYield() │   │ audit()  │  │pay()   │ │ │
│  │  └────────────┘   └──────────┘  └────────┘ │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## Smart Contracts

### 1. TreasuryVault.sol
```solidity
// Core functions:
function deposit(uint256 amount) external          // Deposit funds (USDC/ETH)
function stakeInLido() external                    // Stake ETH → stETH
function harvestYield() external onlyAgent         // Withdraw only yield
function getAvailableYield() public view returns (uint256)
function getPrincipal() public view returns (uint256)  // Always locked

// Guardrails:
uint256 public maxDailySpend;
uint256 public maxPerTransaction;
mapping(uint256 => uint256) public dailySpent;     // day => amount
event YieldHarvested(uint256 amount, uint256 timestamp);
event SpendExecuted(address to, uint256 amount, string reason);
```

### 2. ServiceRegistry.sol
```solidity
function registerService(string memory name, uint256 price) external
function discoverServices() external view returns (Service[] memory)
function requestService(uint256 serviceId) external payable
function completeService(uint256 requestId, bytes memory result) external
event ServiceRequested(uint256 id, address requester, uint256 price);
event ServiceCompleted(uint256 id, bytes result);
```

---

## Bounty-Specific Implementation

### Bankr ($5,000) - Self-Funding Inference
```python
# Agent pays for its own LLM calls using onchain earnings
from bankr import BankrClient

client = BankrClient(api_key="...", wallet_address="0x...")

# Agent generates revenue from services
revenue = collect_service_payments()

# Agent uses revenue to pay for inference
response = client.chat(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": "Analyze ETH/USDC price action"}],
    payment_source="onchain_wallet"  # Pays from earned yield
)
```

### Lido ($9,500) - Treasury + MCP Server + Monitor
```python
# MCP Server for staking
@mcp_tool("stake_eth")
def stake_eth(amount: float):
    """Stake ETH into Lido stETH via natural language"""
    tx = lido_contract.submit(amount, {"from": agent_wallet})
    return f"Staked {amount} ETH. stETH received. TX: {tx.hash}"

@mcp_tool("check_yield")
def check_yield():
    """Check current yield and available balance"""
    steth_balance = steth.balanceOf(treasury_vault)
    yield_available = treasury.getAvailableYield()
    return f"stETH balance: {steth_balance}. Available yield: {yield_available}"

# Monitoring agent
@scheduled(interval="1h")
def monitor_vaults():
    """Generate plain English vault report"""
    positions = get_all_positions()
    report = llm.generate(f"Explain these vault positions in plain English: {positions}")
    publish_report(report)
```

### Uniswap ($5,000) - Real Swaps
```python
# Real swap execution via Uniswap Trading API
import requests

def execute_swap(token_in, token_out, amount):
    quote = requests.get(
        "https://trade-api.gateway.uniswap.org/v1/quote",
        params={"tokenIn": token_in, "tokenOut": token_out, "amount": amount}
    )
    # Execute the swap onchain
    tx = sign_and_send(quote.json()["transaction"])
    return {"tx_hash": tx.hash, "amount_out": quote.json()["amountOut"]}
```

### Base - Trading Agent ($5,000) + Service ($5,000)
```python
# Autonomous trading strategy
class TradingAgent:
    def analyze_market(self):
        # Use Bankr LLM to analyze price data
        analysis = bankr.chat("Analyze ETH/USDC 4h chart. Buy/sell/hold?")
        return parse_signal(analysis)

    def execute_trade(self, signal):
        if signal == "BUY":
            return uniswap_swap("USDC", "ETH", self.position_size)
        elif signal == "SELL":
            return uniswap_swap("ETH", "USDC", self.eth_balance)

    def track_pnl(self):
        # Prove profitability onchain
        return {"initial": self.starting_balance, "current": self.current_balance,
                "pnl": self.current_balance - self.starting_balance}
```

---

## The Closed Loop

```
Human deposits 0.5 ETH into TreasuryVault
  → Agent stakes in Lido (stETH)
    → Yield accrues (~3.5% APY)
      → Agent harvests yield weekly
        → Yield pays for Bankr LLM inference
          → Agent analyzes markets, executes Uniswap swaps
            → Trading profits flow back to treasury
              → Agent offers portfolio analysis service
                → Service fees = additional revenue
                  → Revenue reinvested → cycle continues
```

**The agent never touches the principal. It earns its keep from yield + services + trading.**

---

## Deliverables Checklist

- [ ] TreasuryVault.sol deployed on Base (testnet first, then mainnet if possible)
- [ ] ServiceRegistry.sol deployed on Base
- [ ] Bankr API integration with onchain payment
- [ ] Lido stETH staking integration
- [ ] MCP server for Lido staking (natural language commands)
- [ ] Monitoring agent with hourly plain English reports
- [ ] Uniswap v4 swap execution with real receipts
- [ ] MoonPay CLI integration for bridging
- [ ] Trading strategy with provable P&L
- [ ] Dashboard showing treasury state, yield earned, compute spent
- [ ] All tx hashes documented in README
- [ ] Demo video showing the full closed loop

---

## README Structure (AI Judge Optimized)

```
# AutoFund: The Self-Sustaining DeFi Agent

## Problem → Solution → How It Works → Integrations (with tx hashes)
## Onchain Proof Table → Architecture → How to Run → Technical Decisions
```

See WINNING_STRATEGY.md for full README template.
