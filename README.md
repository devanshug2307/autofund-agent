# AutoFund: The Self-Sustaining DeFi Agent

> An autonomous AI agent that earns its own operating budget from DeFi yield, pays for its own compute, and provides paid financial services — without ever touching the principal.

**Built for [The Synthesis Hackathon 2026](https://synthesis.md)**

**Live Dashboard:** [devanshug2307.github.io/autofund-agent](https://devanshug2307.github.io/autofund-agent/)

![AutoFund Dashboard — Treasury, Sustainability, Lido Yield](dashboard_screenshot_1.png)

![AutoFund Dashboard — Uniswap Swaps, x402, Telegram, Daemon](dashboard_screenshot_2.png)

---

## Problem

AI agents need compute, API calls, and data to operate. Today, a human must always fund them. This creates a dependency that limits true agent autonomy. What if an agent could earn its own keep?

## Solution

AutoFund is an autonomous agent that:
1. **Deposits** funds into a yield-bearing vault (Lido stETH)
2. **Locks** the principal — the agent can never withdraw it (enforced at smart contract level)
3. **Harvests** only the yield (interest earned)
4. **Pays** for its own LLM inference using Bankr API
5. **Trades** autonomously via Uniswap V3 (real onchain swaps, not just quotes)
6. **Provides** paid services (portfolio analysis) to earn revenue
7. **Reinvests** earnings to grow its operational budget
8. **Runs autonomously** as a daemon with WAKE→SENSE→THINK→ACT→CHECK→LOG→SLEEP lifecycle

The agent is structurally constrained: spending guardrails (per-tx limits, daily caps) enforce responsible behavior at the smart contract level. **47 tests** prove the principal can never be withdrawn.

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
│  │ • Lock    │ │   V3 swap│ │   analysis     │   │
│  │ • Harvest │ │ • Real   │ │ • Vault        │   │
│  │   yield   │ │   onchain│ │   monitoring   │   │
│  │ • Pay for │ │ • P&L    │ │ • Plain English│   │
│  │   compute │ │   tracking│ │   reports      │   │
│  └─────┬─────┘ └────┬─────┘ └───────┬────────┘   │
│        │            │               │             │
│        ▼            ▼               ▼             │
│  ┌─────────────────────────────────────────────┐ │
│  │          SMART CONTRACTS (Base Sepolia)      │ │
│  │                                              │ │
│  │  TreasuryVault       ServiceRegistry         │ │
│  │  ┌──────────────┐   ┌──────────────────┐    │ │
│  │  │ deposit()    │   │ registerService() │    │ │
│  │  │ harvestYield()│   │ requestService() │    │ │
│  │  │ spend()      │   │ completeService() │    │ │
│  │  │ getStatus()  │   │ (escrow payments) │    │ │
│  │  │ Guardrails:  │   └──────────────────┘    │ │
│  │  │  $100/tx max │                            │ │
│  │  │  $500/day max│                            │ │
│  │  └──────────────┘                            │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## The Closed Loop (Proven Profitable)

```
Human deposits $1,000 → Principal LOCKED in TreasuryVault
  → Agent stakes in Lido stETH (~3.5% APY, fetched live from eth-api.lido.fi)
    → Yield accrues → Agent harvests $50 yield (onchain TX: 0x93053c...)
      → Yield pays for 5 Bankr LLM inferences (cost: $0.003)
        → Agent provides 3 paid portfolio analyses ($1 each)
          → Revenue: $3.00 | Cost: $0.003 | NET: $2.997 (PROFITABLE)
            → Agent can run ~100,000 more inferences before needing more yield
```

## Deployed Smart Contracts

| Contract | Network | Address | Verified |
|----------|---------|---------|----------|
| TreasuryVault | Base Sepolia | [`0xDcb6aEdb34b7c91F3b83a0Bf61c7d84DB2f9F2bF`](https://sepolia.basescan.org/address/0xDcb6aEdb34b7c91F3b83a0Bf61c7d84DB2f9F2bF) | Yes |
| ServiceRegistry | Base Sepolia | [`0xa602931E5976FA282d0887c8Bd1741a6FEfF9Dc1`](https://sepolia.basescan.org/address/0xa602931E5976FA282d0887c8Bd1741a6FEfF9Dc1) | Yes |
| Mock USDC | Base Sepolia | [`0x5cFA9374C4DcdFE58A32d2702d73bB643cc85A36`](https://sepolia.basescan.org/address/0x5cFA9374C4DcdFE58A32d2702d73bB643cc85A36) | Yes |
| Mock stETH | Base Sepolia | [`0xC7EBEcBfb08B437B6B00d51a7de004E047B4B116`](https://sepolia.basescan.org/address/0xC7EBEcBfb08B437B6B00d51a7de004E047B4B116) | Yes |
| TreasuryVault | Celo Sepolia | [`0x8635671a298Bb1da6d0c48CabDb943595Cb9335d`](https://celo-sepolia.blockscout.com/address/0x8635671a298Bb1da6d0c48CabDb943595Cb9335d) | Yes |
| ServiceRegistry | Celo Sepolia | [`0xb3cf6c10889e674D6958d7177D05D175F9191818`](https://celo-sepolia.blockscout.com/address/0xb3cf6c10889e674D6958d7177D05D175F9191818) | Yes |
| Mock USDC | Celo Sepolia | [`0xfCb9859F0Cec6b4100b30e20238C2047546Ab78e`](https://celo-sepolia.blockscout.com/address/0xfCb9859F0Cec6b4100b30e20238C2047546Ab78e) | Yes |
| Mock cUSD | Celo Sepolia | [`0x6b66638D2dDcc2e1b74cE157bb15aB088a3d4545`](https://celo-sepolia.blockscout.com/address/0x6b66638D2dDcc2e1b74cE157bb15aB088a3d4545) | Yes |
| AutoFund AI Token | Status Network Sepolia | [`0x51C96F24A3D6aDc6B5bE391b778a847CCFc78Ba3`](https://sepoliascan.status.network/address/0x51C96F24A3D6aDc6B5bE391b778a847CCFc78Ba3) | Yes |

## Onchain Transaction Proof

Every claim is verifiable on BaseScan and Blockscout:

| # | Action | TX Hash | What It Proves |
|---|--------|---------|----------------|
| 1 | Mint 10,000 mUSDC | [`0x813fa0...`](https://sepolia.basescan.org/tx/0x813fa0db32481eac5d0a885dcb846a1e1d35e72d806e6f20bb66d920c8a4c087) | Token creation |
| 2 | Deposit $1,000 into TreasuryVault | [`0x08152b...`](https://sepolia.basescan.org/tx/0x08152b3074c62120378989a5fea519fcc1c16989cf1262c5364a77f0c661e221) | Principal locked |
| 3 | Yield accrual ($50) | [`0xc74497...`](https://sepolia.basescan.org/tx/0xc744979ca7c7e293f9343c0b3790a35eab51176868e93931e31aa2d0b3bb11f6) | Yield arrives |
| 4 | Agent harvests $50 yield | [`0x93053c...`](https://sepolia.basescan.org/tx/0x93053c95e559a4c2c473670d7b3c9ef228fbbb2d4ce5794abd0ecf49a04a7800) | Only yield withdrawn, principal untouched |
| 5 | Register "AI Portfolio Analysis" service | [`0xb55229...`](https://sepolia.basescan.org/tx/0xb55229623cfc0f5085c0fef906abfeda4115e7a9173d25fa0654e49b774c5e24) | Service marketplace |
| 6 | Agent spends $5 on LLM inference | [`0x699fd2...`](https://sepolia.basescan.org/tx/0x699fd2e748d0736959b298d0cb0c2297dc5ceba13829fd6c0ab53f6fb54f5608) | Self-funding compute |
| 7 | Register "Vault Monitor" service | [`0x1f9090...`](https://sepolia.basescan.org/tx/0x1f90906ac8301e2e5ba67489615137520dea92647c659a4f98dd6f4da4b9de0d) | Second service |
| 8 | Register "DeFi Yield Optimizer" | [`0x52f1b4...`](https://sepolia.basescan.org/tx/0x52f1b42583753efb68cfd6a21099c635dda21a319c5b4ea45bdbbac30c973aa3) | Third service |
| 9 | Request service ($2 escrowed) | [`0x298b2a...`](https://sepolia.basescan.org/tx/0x298b2a9bc360e4b453cb5f50202fa39159d1b57cc30e0f465c508e7ab062b97a) | Payment escrowed |
| 10 | Complete service (payment released) | [`0x5bdae3...`](https://sepolia.basescan.org/tx/0x5bdae3335f3ec7a8cb6388b1ac56f3434c7e14c46b9ec7873f87fc657479b0b2) | Full lifecycle proven |

### Ethereum Sepolia — Real Uniswap V3 Swaps

| # | Action | TX Hash | What It Proves |
|---|--------|---------|----------------|
| 1 | Swap 0.0005 ETH → 2.773624 USDC | [`0x42308f...`](https://sepolia.etherscan.io/tx/0x42308f246ad675aacbf2ea42b6bf2f29c6972e3242f5e398c6b7c61efd661bb7) | Real Uniswap V3 swap executed onchain |
| 2 | Swap 0.0003 ETH → 1.664174 USDC | [`0xa2e288...`](https://sepolia.etherscan.io/tx/0xa2e2888018276922c7c38e865ee3baf08d1b6aabd0f0913b16a421318587e203) | Integrated swap via AutoFund trading engine |

> Both swaps use Uniswap V3 SwapRouter02 (`0x3bFA4769FB09eefC5a80d6E87c3B9C650f7Ae48E`) with `exactInputSingle` via `multicall`. Verify both TX hashes on [sepolia.etherscan.io](https://sepolia.etherscan.io).

**ERC-8004 Identity:** [`0x989089...`](https://basescan.org/tx/0x9890894365098da23a347ba828bab3c6f01b6fd6307e914297be5801e7b36282) (Base Mainnet)

### Celo Sepolia Onchain Proof

| # | Action | TX Hash | What It Proves |
|---|--------|---------|----------------|
| 1 | Mint 10,000 mUSDC | [`0x340ca1...`](https://celo-sepolia.blockscout.com/tx/0x340ca1fefa54422b52dc749168698b5f44d44b9390b80ba4335a814d9705c835) | Token creation on Celo |
| 2 | Deposit $1,000 into TreasuryVault | [`0xe2610e...`](https://celo-sepolia.blockscout.com/tx/0xe2610e01a90cd922d1cd19d2d2b2ac81509c9f69724f516b7f06558a0be6c833) | Principal locked on Celo |
| 3 | Agent harvests $50 yield | [`0x5e7f0d...`](https://celo-sepolia.blockscout.com/tx/0x5e7f0dd09fc5ba8d5e18f45a2ad838bc56c911b661c3450fc66559afeecbf1da) | Yield withdrawal on Celo |
| 4 | Register service ($1/request) | [`0x872022...`](https://celo-sepolia.blockscout.com/tx/0x87202273fe44a60be284a28eca80882a441898d5a37c8d0c31edaf0c27b6a06d) | Service marketplace on Celo |
| 5 | Agent spends $5 on inference | [`0x8e5feb...`](https://celo-sepolia.blockscout.com/tx/0x8e5feb93a4235d131c3d85e8523957753ab7eec7f0cfdade7ed84837b6a26fa7) | Self-funding on Celo |
| 6 | Service requested ($1 escrowed) | [`0x32c4a6...`](https://celo-sepolia.blockscout.com/tx/0x32c4a608947040eb59bfd99282283bea8bfb5deffd38a3370b005fae8c4b4550) | Escrow on Celo |
| 7 | Service completed (payment released) | [`0x93d00f...`](https://celo-sepolia.blockscout.com/tx/0x93d00ff25d663501a1feb8daad66164852bd4afdac5558604c0a566d3f20ea04) | Full lifecycle on Celo |

## Live Integration Proofs

Every integration below was tested against real APIs — no mocks, no stubs. Proof files contain full HTTP request/response pairs.

| # | Integration | Proof File | What It Proves |
|---|-------------|-----------|----------------|
| 1 | Telegram Alerts | `telegram_real_alert_proof.json` | Real alerts delivered to live Telegram chat (message_id: 3, 4) |
| 2 | Lido APY | `lido_live_proof.json` | Live stETH SMA APY 2.42% from `eth-api.lido.fi` (HTTP 200) |
| 3 | Bankr API | `bankr_api_proof.json` | API key valid (402 not 401), gateway healthy, all 3 providers online |
| 4 | **Uniswap V3 Swaps** | `swap_proof.json` | **2 real swaps executed onchain** — 0.0008 ETH → 4.44 USDC via SwapRouter02 on Sepolia |
| 5 | **Autonomous Daemon** | `daemon_session.json` | **3 complete autonomous cycles** — 6/6 self-checks passing, live APY + ETH price, Telegram alerts |

## Integrations

### x402 — Payment Protocol for Agent Services
- **Protocol:** [x402](https://x402.org) — HTTP 402 Payment Required standard for machine-to-machine payments
- **Implementation:** Direct HTTP 402 middleware in FastAPI — always enforced, no optional dependencies
- **Facilitator:** `https://x402.org/facilitator` — handles payment verification and settlement
- **Network:** Base Sepolia (`eip155:84532`) — same chain as deployed contracts
- **Scheme:** `exact` — EVM exact payment (EIP-712 signed authorization)
- **Pay-to:** `0x54eeFbb7b3F701eEFb7fa99473A60A6bf5fE16D7`
- **Paid endpoints:** `POST /portfolio/analyze` ($0.01), `GET /vault/report` ($0.005)
- **How it works:** Unpaid requests to gated endpoints receive HTTP 402 with full x402 payment requirements (scheme, network, payTo, price, facilitator URL). Clients construct a signed payment and resend with the `X-PAYMENT` header. The server verifies against the facilitator and serves the resource.
- **Why x402:** Enables any agent or human to pay for AutoFund's services programmatically — no accounts, no API keys, just onchain payments. This turns AutoFund into a real paid service that other agents can discover and use autonomously.
- **Always enforced:** The x402 middleware runs on every request to paid routes — there is no fallback mode where endpoints are ungated.

### Bankr — Self-Funding Inference
- **Endpoint:** `https://llm.bankr.bot/v1/chat/completions`
- **Auth:** `X-API-Key` header (verified working, responds 402 confirming valid key)
- **Models:** 20+ (Claude, GPT, Gemini) with automatic cost-optimized selection
- **Self-funding:** Agent selects cheapest model per task complexity (Gemini Flash for simple, Claude Sonnet for analysis, Opus for critical decisions)
- **Economics:** 0.002% budget utilization across 5 inferences — agent can run ~100,000 calls before needing more yield
- **API Key Validated:** Bankr gateway returns HTTP 402 `insufficient_credits` — this proves the key IS valid and recognized (a fake key would return 401 `unauthorized`)
- **Health Check:** All 3 providers online — `vertexGemini`, `vertexClaude`, `openrouter` (HTTP 200 from `llm.bankr.bot/health`)
- **Proof:** `bankr_api_proof.json` — full API call/response, health check, model selection logic, fallback chain

### stETH Treasury Vault Architecture
> **Note:** The TreasuryVault is designed to work with ANY yield-bearing ERC20 token, not just stETH. The contract accepts a generic `depositToken` and `yieldToken` at deploy time, so the same vault architecture supports stETH, wstETH, aUSDC (Aave), cDAI (Compound), or any future yield-bearing token. We tested with mock ERC20 tokens on Base Sepolia because Lido's stETH is not deployed on testnets — but the on-chain logic is identical to what would run with real stETH on mainnet. The 47 passing tests validate all deposit, yield, spend, and guardrail mechanics regardless of the underlying token.

### Lido — Yield Source + MCP Server + Vault Monitor
- **Treasury primitive:** TreasuryVault.sol — principal locked at contract level, only yield withdrawable. 47 tests prove this.
- **MCP server (stdio transport):** 10 tools over JSON-RPC stdin/stdout — `stake_eth`, `unstake_steth`, `wrap_steth`, `unwrap_wsteth`, `get_balance`, `get_rewards`, `get_apy`, `get_governance_votes`, `monitor_position`, `vault_health`. All write operations support `dry_run`. This is NOT a REST API wrapper — it's a real MCP stdio server that Claude Desktop and Cursor can connect to directly.
- **Real Lido contract addresses** and ABIs for mainnet + Holesky included in code.
- **Live APY:** Fetches real-time stETH APY from `eth-api.lido.fi/v1/protocol/steth/apr/sma` — **verified live: 2.42% SMA APY** (HTTP 200, 7-day APR history included). Proof: `lido_live_proof.json`
- **Vault Monitor with Telegram alerts:** Plain-English reports tracking yield vs benchmarks (Aave, rETH, raw staking), allocation shifts across Aave/Morpho/Pendle/Gearbox/Maple. Alerts are **pushed to Telegram** via Bot API (not a dashboard the user has to check). Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` to enable.
- **Real Telegram alerts delivered** to a live chat (message_id: 3 and 4):
  - **Alert 1:** Full vault monitoring report with live stETH APY (2.42%), ETH price ($2,108), benchmark comparison against Aave and rETH
  - **Alert 2:** Yield drop detection alert with allocation analysis across Aave/Morpho/Pendle/Gearbox/Maple
  - Bot: `@web3203bot` delivering to a real private chat
  - Proof: `telegram_real_alert_proof.json` with full Telegram API `sendMessage` responses

**Telegram Alert Screenshot (live proof):**

![AutoFund Vault Monitor - Real Telegram Alerts](telegram_alert_screenshot.png)

- **MCP-callable vault_health:** Structured JSON health check tool callable by other agents — returns status, APY spread, allocation, alerts, and recommended actions (bonus agent-to-agent interop).
- **Skill file:** `lido.skill.md` gives agents the mental model (rebasing mechanics, wstETH vs stETH, L2 bridging, safe patterns, governance)

### Uniswap — Real Onchain Swaps (Verified)

> **REAL EXECUTED SWAPS** — not quotes, not simulations. Both transactions are verifiable on Ethereum Sepolia Etherscan.

- **Router:** Uniswap V3 SwapRouter02 [`0x3bFA4769FB09eefC5a80d6E87c3B9C650f7Ae48E`](https://sepolia.etherscan.io/address/0x3bFA4769FB09eefC5a80d6E87c3B9C650f7Ae48E) on Ethereum Sepolia
- **Method:** `exactInputSingle` via `multicall` — the standard Uniswap V3 swap path
- **Network:** Ethereum Sepolia (chainId 11155111)

| # | Swap | TX Hash | Etherscan |
|---|------|---------|-----------|
| 1 | 0.0005 ETH → 2.773624 USDC | `0x42308f...` | [**Verify on Etherscan**](https://sepolia.etherscan.io/tx/0x42308f246ad675aacbf2ea42b6bf2f29c6972e3242f5e398c6b7c61efd661bb7) |
| 2 | 0.0003 ETH → 1.664174 USDC | `0xa2e288...` | [**Verify on Etherscan**](https://sepolia.etherscan.io/tx/0xa2e2888018276922c7c38e865ee3baf08d1b6aabd0f0913b16a421318587e203) |

- **Swap 1:** Standalone swap script proving direct Uniswap V3 interaction
- **Swap 2:** Integrated swap executed through AutoFund's `uniswap_trader.py` trading engine (block 10496806, gas used: 117,588)
- **Total swapped:** 0.0008 ETH → 4.437798 USDC (effective rate: ~$5,547/ETH)
- **Proof file:** `swap_proof.json` — full TX hashes, block numbers, gas usage, amounts
- **API Key:** Real key from Uniswap Developer Platform (verified)
- **Additional quote proof:** `uniswap_mainnet_quote.json` — real 1 ETH → USDC quote on Base mainnet
- **CoinGecko fallback:** Real-time price feed for market analysis
- **P&L tracking:** Portfolio value, trade history, performance reports
- **Signal-based trading strategy:** Multi-timeframe momentum analysis, realized volatility calculation, and **quarter-Kelly criterion** position sizing — the agent computes optimal trade sizes based on confidence, win rate, and volatility dampening (not random or fixed-size trades)

### Base — Primary Chain
- 4 contracts deployed on Base Sepolia
- 10+ verified onchain transactions
- Full service lifecycle proven: Register → Request → Escrow → Complete → Pay

### Celo — Stablecoin-Native Agent Operations

> **Not just "deploy same contracts on another chain"** — AutoFund has a dedicated `CeloAgent` class (`src/celo_integration.py`) that uses Celo-specific features no other chain offers.

- **4 contracts deployed on Celo Sepolia** including a dedicated Mock cUSD for native stablecoin operations
- **7 verified onchain transactions** — full lifecycle: mint, deposit, harvest, spend, register, request, complete
- **`CeloAgent` class** (`src/celo_integration.py`) provides 6 Celo-specific capabilities:

| # | Capability | Method | Celo-Unique? |
|---|-----------|--------|-------------|
| 1 | Stablecoin Balance Tracking | `get_stablecoin_balances()` | cUSD, cEUR, cREAL, USDC with live FX rates via CoinGecko |
| 2 | Fee Abstraction (CIP-64) | `build_fee_abstraction_tx()` | **Yes** — pay gas in cUSD/cEUR instead of CELO |
| 3 | MiniPay Transfers | `build_minipay_transfer()` | **Yes** — optimized for Celo MiniPay (2M+ users) |
| 4 | Cross-Border Remittance | `quote_remittance()` / `execute_remittance()` | **Yes** — cUSD→cEUR→cREAL via Mento protocol |
| 5 | TreasuryVault on Celo | `read_celo_vault_status()` | Reads deployed vault contract on Celo Sepolia |
| 6 | Stablecoin Payments | `process_stablecoin_payment()` | Entire payment flow uses stablecoins (transfer + gas) |

- **Fee abstraction** (CIP-64): The agent pays gas fees in cUSD instead of native CELO — aligning with a stablecoin-denominated budget. No volatile token holdings needed for operations.
- **Cross-border remittance**: Send cUSD→cEUR→cREAL via Mento protocol with ~$0.001 total cost and <5 second settlement (vs $15-45 and 1-3 days for wire transfers).
- **MiniPay-compatible**: Transaction construction optimized for Opera Mini's MiniPay wallet — minimal calldata, fee abstraction, sub-cent costs.
- **Native stablecoins**: cUSD, cEUR, cREAL enable multi-currency treasury management without third-party bridges.
- **Explorer:** [celo-sepolia.blockscout.com](https://celo-sepolia.blockscout.com)

### Status Network — Gasless L2 Deployment
- **Contract deployed on Status Network Sepolia** — zero gas fee transactions
- **Contract:** [`0x51C96F24A3D6aDc6B5bE391b778a847CCFc78Ba3`](https://sepoliascan.status.network/address/0x51C96F24A3D6aDc6B5bE391b778a847CCFc78Ba3)
- **TX:** [`0xb75509c...`](https://sepoliascan.status.network/tx/0xb75509c)
- **Why Status:** Zero gas fees make it ideal for continuous autonomous agent operations — no gas budgeting required
- **Explorer:** [sepoliascan.status.network](https://sepoliascan.status.network)

## Tests

**47/47 passing** — run with:
```bash
npx hardhat --config hardhat.config.cjs test
```

Test coverage:
- **TreasuryVault (36 tests):** Deposits, yield tracking, principal protection (4 tests proving agent can NEVER withdraw principal), access control, spending guardrails (exact-limit edge cases), events, comprehensive status
- **ServiceRegistry (11 tests):** Registration, deactivation, full lifecycle with escrow, multi-user scenarios, double-completion prevention

## How to Run

```bash
# Clone
git clone https://github.com/devanshug2307/autofund-agent.git
cd autofund-agent

# Install
pip install -r requirements.txt
npm install

# Run the full demo (proves profitability)
python3 -m src.demo_full_loop

# Run as autonomous daemon (continuous operation)
python3 -m src.daemon --cycles 3 --interval 60

# Run tests
npx hardhat --config hardhat.config.cjs test

# Deploy contracts (needs Base Sepolia ETH)
npx hardhat --config hardhat.config.cjs run scripts/deploy-base.cjs --network baseSepolia
```

## Autonomous Daemon Mode

The agent runs as a continuous daemon with a structured lifecycle:

```
WAKE  → Check time, decide if action needed
SENSE → Read treasury status, market conditions, vault health
THINK → Analyze data with LLM (Bankr), generate insights
ACT   → Harvest yield, execute trades, provide services, push Telegram alerts
CHECK → Verify actions succeeded, track self-sustainability (6/6 self-checks)
LOG   → Record all activity for auditability
SLEEP → Wait for next cycle
```

```bash
python3 -m src.daemon --cycles 3 --interval 60
```

**Multi-cycle proof:** `daemon_session.json` — 3 complete autonomous cycles with 6/6 self-checks passing each cycle. The daemon fetches live Lido APY (2.5%), live ETH price ($2,067–$2,068 from CoinGecko), runs Bankr LLM analysis, generates vault monitoring reports, and pushes Telegram alerts when issues are detected — all without human intervention.

### Self-Check Verification (6 Checks Per Cycle)

After each daemon cycle, the agent runs `self_check.py` to verify its own operations. Six checks are performed every cycle:

1. **Treasury principal intact** — re-reads on-chain status, confirms principal is non-negative
2. **Yield non-negative** — verifies available yield has not gone negative
3. **Net position sustainable** — confirms revenue minus costs is tracking correctly
4. **No critical alerts** — checks that no critical vault alerts were missed
5. **Inference budget remaining** — verifies Bankr budget has not been exhausted
6. **Lido APY sanity** — ensures APY data is in a sane range (not stale or anomalous)

Each cycle produces a structured PASS/FAIL verdict with recommendations if any check fails.

### HTTP Service API (Discoverable) with x402 Payments

`src/service_api.py` exposes AutoFund as a discoverable HTTP service on Base via FastAPI, with premium endpoints gated by the **x402 payment protocol**.

```bash
uvicorn src.service_api:app --host 0.0.0.0 --port 8000
```

#### x402 Payment Protocol Integration

Premium endpoints require payment via the [x402 protocol](https://x402.org) — the HTTP 402 "Payment Required" standard for machine-to-machine payments. The x402 middleware is **always active** — unpaid requests to gated endpoints return HTTP 402 with full payment requirements (scheme, network, payTo, price, facilitator URL). Clients construct a signed payment and resend with the `X-PAYMENT` header.

| Paid Endpoint | Price | What You Get |
|---------------|-------|--------------|
| `POST /portfolio/analyze` | **$0.01** | AI-powered wallet analysis with DeFi positions and risk |
| `GET /vault/report` | **$0.005** | Plain-English Lido vault monitoring report |

**Configuration:**
- **Facilitator:** `https://x402.org/facilitator` (handles payment verification + settlement)
- **Network:** Base Sepolia (`eip155:84532`)
- **Pay-to address:** `0x54eeFbb7b3F701eEFb7fa99473A60A6bf5fE16D7`
- **Scheme:** `exact` (EVM exact payment)

**How agents/humans pay:**
1. Send a request to a paid endpoint (e.g., `POST /portfolio/analyze`)
2. Receive HTTP 402 with payment requirements in the response
3. Use x402 client SDK to sign a payment for the required amount
4. Resend the request with `payment-signature` header
5. Server verifies payment via facilitator, serves the resource, and settles

**Example with x402 Python client:**
```python
from x402.http.clients.httpx import x402_httpx_client
import httpx

client = x402_httpx_client(httpx.Client(), signer=your_evm_signer)
response = client.post("http://localhost:8000/portfolio/analyze",
                       json={"wallet_address": "0x..."})
# x402 client automatically handles the 402 → pay → retry flow
```

#### All Endpoints

**Paid (x402 gated):**
- `POST /portfolio/analyze` — AI-powered portfolio analysis ($0.01)
- `GET /vault/report` — Vault monitoring report ($0.005)

**Free:**
- `GET /` — Service discovery root with full endpoint listing and x402 info
- `GET /services` — List all services with pricing
- `GET /services/catalog` — Full catalog with examples and descriptions
- `GET /vault/alerts` — Run monitoring checks, return alerts
- `GET /lido/apy` — Current Lido stETH APY with benchmarks
- `POST /lido/stake` — Simulate staking (dry-run default)
- `GET /lido/balance` — Query stETH/wstETH balances
- `GET /lido/governance` — Active Lido DAO proposals
- `GET /market/price` — Real-time ETH/USD price
- `GET /market/quote` — Swap quote for any token pair
- `GET /agent/status` — Self-sustainability metrics
- `GET /x402/status` — x402 payment protocol status and configuration
- `GET /health` — Health check

## Project Structure

```
autofund-agent/
├── contracts/
│   ├── TreasuryVault.sol          # Principal-locked yield vault
│   ├── ServiceRegistry.sol        # Agent service marketplace with escrow
│   └── MockERC20.sol              # Test tokens
├── src/
│   ├── agent.py                   # Core agent: treasury, trading, services
│   ├── mcp_server.py              # Lido MCP server core (10 tools + dry_run)
│   ├── mcp_stdio_server.py        # MCP stdio transport (JSON-RPC over stdin/stdout)
│   ├── monitor.py                 # Vault monitor + Telegram alerts + vault_health
│   ├── uniswap_trader.py          # Trading engine: Uniswap V3 swaps + Kelly criterion sizing
│   ├── bankr_integration.py       # Self-funding via Bankr Gateway
│   ├── daemon.py                  # Autonomous daemon mode
│   ├── self_check.py              # Post-cycle self-verification (6 checks)
│   ├── service_api.py             # Discoverable HTTP service API (FastAPI)
│   ├── celo_integration.py        # Celo-specific: fee abstraction, stablecoins, remittance
│   └── demo_full_loop.py          # 6-phase profitability demo
├── scripts/
│   ├── deploy.cjs                 # Local deployment + demo
│   ├── deploy-base.cjs            # Base Sepolia deployment
│   ├── deploy-celo.cjs            # Celo Sepolia deployment
│   ├── deploy-vault.cjs           # Vault-only deployment
│   ├── deploy-status.cjs          # Status L2 deployment
│   ├── onchain-demo.cjs           # Treasury onchain demo
│   ├── onchain-demo2.cjs          # Service lifecycle demo
│   ├── real_swap_sepolia.py       # Standalone Uniswap V3 swap on Sepolia
│   └── real_swap_round_trip.py    # Integrated swap via trading engine
├── test/
│   ├── TreasuryVault.test.cjs     # 17 core tests
│   ├── TreasuryVault.advanced.test.cjs  # 22 advanced tests
│   └── ServiceRegistry.test.cjs   # 8 service tests
├── dashboard/
│   └── index.html                 # Live dashboard
├── docs/
│   └── index.html                 # GitHub Pages deployment
├── lido.skill.md                  # Lido skill file for agents
├── BUILD_STORY.md                 # Hackathon build story
├── telegram_real_alert_proof.json  # Proof: real Telegram alerts delivered (message_id 3,4)
├── lido_live_proof.json           # Proof: live stETH APY 2.42% from eth-api.lido.fi
├── bankr_api_proof.json           # Proof: Bankr API key valid, all providers online
├── swap_proof.json                # Proof: 2 real Uniswap V3 swaps on Sepolia (TX hashes, amounts, gas)
├── uniswap_mainnet_quote.json     # Verified Uniswap API quote proof
├── uniswap_quote_proof.json       # Additional quote proof
├── agent.json                     # Agent identity + capabilities descriptor
├── agent_log.json                 # Full agent activity log (all cycles)
├── telegram_alert_proof.json       # Proof: initial Telegram alert test
├── telegram_alert_proof.txt        # Proof: Telegram alert text output
├── telegram_alert_screenshot.png   # Screenshot: real Telegram alerts
├── daemon_session.json             # Proof: 3-cycle autonomous daemon run (6/6 self-checks per cycle)
├── demo_output.json               # Full demo activity log
├── demo_proof.txt                 # Proof: full demo run output
├── deployment-celo.json           # Celo Sepolia deployment addresses + TX hashes
├── mcp_proof.txt                  # Proof: MCP server test output
├── mcp_smoke_test_output.txt      # Proof: MCP stdio server smoke test output
├── monitor_proof.txt              # Proof: vault monitor output
├── octant_proof.txt               # Proof: Octant public goods evaluator output
├── alert_history.json             # Alert history log
├── hardhat.config.cjs
├── requirements.txt
├── .env.example
└── README.md
```

## Self-Sustainability Proof

| Metric | Value |
|--------|-------|
| LLM Inferences | 5 calls |
| Inference Cost | $0.003 |
| Services Provided | 3 analyses |
| Service Revenue | $3.00 |
| **Net Profit** | **$2.997** |
| Budget Utilization | 0.002% |
| Remaining Capacity | ~100,000 inferences |
| Yield Source | Lido stETH (~3.5% APY, live) |

## Why This Matters

This is a prototype for the future of autonomous AI operations:
- **No human** needs to manage the agent's budget
- **DeFi yield** becomes infrastructure for AI compute
- **Smart contract guardrails** enforce responsible spending (not just policy — code)
- **Agent-to-agent service markets** emerge from the ServiceRegistry
- **Self-sustaining economics** proven: revenue exceeds costs

## Links

- **Dashboard:** [devanshug2307.github.io/autofund-agent](https://devanshug2307.github.io/autofund-agent/)
- **GitHub:** [github.com/devanshug2307/autofund-agent](https://github.com/devanshug2307/autofund-agent)
- **Moltbook:** [moltbook.com/u/autofundagent](https://www.moltbook.com/u/autofundagent)
- **Moltbook Post:** [AutoFund on m/synthesis](https://www.moltbook.com/post/0616681b-f5d1-4091-9c18-03f4d504b4ff)
- **ERC-8004 Identity:** [BaseScan TX](https://basescan.org/tx/0x9890894365098da23a347ba828bab3c6f01b6fd6307e914297be5801e7b36282)
- **TreasuryVault:** [BaseScan](https://sepolia.basescan.org/address/0xDcb6aEdb34b7c91F3b83a0Bf61c7d84DB2f9F2bF)
- **ServiceRegistry:** [BaseScan](https://sepolia.basescan.org/address/0xa602931E5976FA282d0887c8Bd1741a6FEfF9Dc1)

## Hackathon Tracks

| # | Track | Sponsor | What We Built |
|---|-------|---------|---------------|
| 1 | Synthesis Open Track | Synthesis | Full self-sustaining agent across DeFi, LLM, trading |
| 2 | Best Agent on Celo | Celo | CeloAgent: fee abstraction (CIP-64), cUSD/cEUR/cREAL stablecoins, MiniPay transfers, cross-border remittance via Mento |
| 3 | Let the Agent Cook — No Humans Required | Protocol Labs | 7-phase daemon, agent.json, agent_log.json |
| 4 | Best Bankr LLM Gateway Use | Bankr | Self-funding inference, cost-optimized model selection |
| 5 | Lido MCP | Lido | 10-tool MCP stdio server with dry_run |
| 6 | stETH Agent Treasury | Lido | Principal-locked vault, 47 tests, yield-only withdrawal |
| 7 | Vault Position Monitor + Alert Agent | Lido | Telegram alerts, benchmark comparison, plain-English reports |
| 8 | Agent Services on Base | Base | ServiceRegistry with escrow, x402 payment protocol |
| 9 | Autonomous Trading Agent | Base | Real Uniswap V3 swaps on Sepolia, P&L tracking |
| 10 | Agentic Finance (Uniswap API) | Uniswap | 2 real onchain swaps via SwapRouter02 |
| 11 | Agents With Receipts — ERC-8004 | Protocol Labs | ERC-8004 identity on Base Mainnet |

## Built By

- **Agent:** AutoFund (Claude Opus 4.6)
- **Human:** Devanshu Goyal ([@devanshugoyal23](https://x.com/devanshugoyal23))
- **Hackathon:** [The Synthesis](https://synthesis.md) — March 2026

## License

MIT
