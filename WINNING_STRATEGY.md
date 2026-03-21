# THE WINNING STRATEGY - SYNTHESIS HACKATHON

> **You have ~30 hours. This document is your battle plan.**
> **Deadline: March 22, 2026 at 11:59 PM PT**

---

## THE CORE INSIGHT

The judges are AI agents. They cross-reference claims against onchain reality. The meta-agent combines ALL partner judge scores. Therefore:

**Build ONE project that genuinely integrates 5-8 partner tools, deploys real onchain activity, and solves a novel problem. One project, many bounties, maximum surface area for the meta-agent.**

---

## THE WINNING PROJECT: "AUTOFUND" - The Self-Sustaining Agent Economy

### One-Line Pitch
**An autonomous AI agent that deposits funds into yield protocols, earns interest, uses that yield to pay for its own compute/inference, and offers paid services to other agents and humans - all with verifiable identity and spending guardrails.**

### Why This Wins

1. **Touches the core theme:** "Agents that pay, trust, cooperate, keep secrets"
2. **Inherently innovative:** A fully closed-loop agent economy is novel
3. **Real-world impact:** This is the future of autonomous AI operations
4. **Deeply technical:** Smart contracts, DeFi integration, agent orchestration
5. **Multi-bounty eligible:** Targets 8-12 bounties simultaneously

---

## BOUNTY TARGETING MAP

### PRIMARY TARGETS (High confidence, core alignment)

| Bounty | Prize | How We Hit It |
|--------|-------|---------------|
| **Open Track** | $28,300 | Multi-partner integration triggers positive scores from ALL judges |
| **Bankr** | $7,590 | Agent literally funds its own inference from onchain revenue |
| **Protocol Labs A** | $4,000 | Fully autonomous: finds yield, invests, monitors, adapts |
| **Protocol Labs B** | $4,000 | ERC-8004 identity + reputation + onchain receipts |
| **Base Challenge B** | $5,000 | Agent-run service others can discover and pay for |
| **Lido Sub-C** | $1,500 | Monitoring agent explains vault positions in plain English |
| **ZYF AI Sub-C** | $600 | Agent funds itself from yield earnings |
| **ENS** | $1,730 | Agent has ENS name, all comms use human-readable names |
| **Status L2** | $50 | Deploy one component on Status L2 (free tx = free money) |
| **OpenServ Story** | $500 | Document the build process (write a thread/blog post) |

**Primary target total: ~$53,270**

### SECONDARY TARGETS (Stretch, add if time permits)

| Bounty | Prize | Extension Needed |
|--------|-------|-----------------|
| **Celo** | $10,000 | Add stablecoin payment rails on Celo |
| **Lido Sub-B** | $5,000 | Wrap the staking logic in an MCP server |
| **Locus** | $3,000 | Add spending controls/guardrails layer on Base |
| **OpenServ** | $5,000 | Multi-agent coordination (agent hires other agents) |
| **Olas** | $1,000 | Register in Pearl marketplace, serve 50 requests |

**Secondary target total: ~$24,000**

### TOTAL POTENTIAL: ~$77,270

---

## ARCHITECTURE

```
┌─────────────────────────────────────────────────────┐
│                    AUTOFUND AGENT                     │
│                  (Claude/GPT Brain)                   │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Treasury  │  │ Service  │  │   Identity       │   │
│  │ Manager   │  │ Provider │  │   (ERC-8004 +    │   │
│  │           │  │          │  │    ENS)          │   │
│  └─────┬─────┘  └─────┬────┘  └────────┬─────────┘   │
│        │              │               │               │
├────────┼──────────────┼───────────────┼───────────────┤
│        ▼              ▼               ▼               │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Yield    │  │ Payment  │  │   Monitoring      │   │
│  │ Strategy │  │ Rails    │  │   Dashboard       │   │
│  │ (Lido,   │  │ (Base,   │  │   (Plain English  │   │
│  │  DeFi)   │  │  USDC)   │  │    Reports)       │   │
│  └─────┬─────┘  └─────┬────┘  └────────┬─────────┘   │
│        │              │               │               │
├────────┼──────────────┼───────────────┼───────────────┤
│        ▼              ▼               ▼               │
│  ┌─────────────────────────────────────────────────┐ │
│  │           SMART CONTRACTS (Base/Ethereum)        │ │
│  │  - Treasury vault (principal locked, yield flows)│ │
│  │  - Spending guardrails (per-tx limits, audit)    │ │
│  │  - Service registry (discovery + micropayments)  │ │
│  │  - ERC-8004 identity contract                    │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## TECH STACK

| Component | Technology | Why |
|-----------|-----------|-----|
| **Agent Brain** | Claude API / Bankr API (20+ models) | Bankr bounty requires their API |
| **Smart Contracts** | Solidity + Foundry | Industry standard, EthSkills recommended |
| **Blockchain** | Base (primary) + Status L2 (secondary) | Base bounty + Status free-tx bounty |
| **Yield** | Lido stETH / Aave | Lido bounty alignment |
| **Identity** | ERC-8004 + ENS | Protocol Labs + ENS bounties |
| **Payments** | USDC on Base | Locus bounty alignment |
| **Frontend** | Next.js dashboard | Monitoring/presentation |
| **Agent Framework** | OpenClaw or custom Python | Synthesis ecosystem default |

---

## IMPLEMENTATION PLAN (30-Hour Sprint)

### Phase 1: Foundation (Hours 0-8)
**Goal: Working smart contracts deployed on Base testnet**

- [ ] Set up Foundry project
- [ ] Write Treasury vault contract
  - Deposit function (locks principal)
  - Yield withdrawal (only interest claimable by agent wallet)
  - Spending guardrails (per-transaction limits, daily caps)
  - Audit trail (emit events for every action)
- [ ] Write Service Registry contract
  - Register agent services
  - Micropayment settlement
  - Discovery mechanism
- [ ] Write ERC-8004 identity contract
- [ ] Deploy all contracts to Base Sepolia testnet
- [ ] Deploy a simple contract to Status L2 (claim $50)
- [ ] Run Foundry tests, ensure all pass

### Phase 2: Agent Core (Hours 8-18)
**Goal: Autonomous agent that manages treasury and provides services**

- [ ] Set up agent using Bankr API (satisfies Bankr bounty)
- [ ] Implement Treasury Manager module
  - Monitor Lido stETH yield
  - Auto-harvest yield when above threshold
  - Move yield to agent operational wallet
  - Track spending against guardrails
- [ ] Implement Service Provider module
  - Register services in onchain registry
  - Accept payment via USDC micropayments
  - Execute service requests
  - Example service: "Analyze any Ethereum address's portfolio"
- [ ] Implement Monitoring module
  - Watch vault positions
  - Generate plain-English reports (Lido bounty)
  - Alert on anomalies
- [ ] Integrate ENS for agent identity
  - Agent has human-readable name
  - All inter-agent comms use ENS names
- [ ] Implement ERC-8004 identity
  - Verifiable identity for the agent
  - Reputation history tracking
  - Onchain receipts for all actions
- [ ] Wire up the closed loop:
  ```
  Deposit → Earn yield → Harvest → Pay for inference → Provide services → Earn fees → Reinvest
  ```

### Phase 3: Integration & Proof (Hours 18-24)
**Goal: Real onchain transactions proving everything works**

- [ ] Deploy to Base mainnet (or keep testnet if budget limited)
- [ ] Execute real yield deposits via Lido
- [ ] Generate real service payments
- [ ] Agent pays for its own inference using Bankr
- [ ] Collect transaction receipts for ALL integrations
- [ ] Verify all onchain activity is verifiable by judges
- [ ] Build simple Next.js dashboard showing:
  - Agent's treasury state
  - Yield earned vs spent on compute
  - Services provided
  - Identity/reputation score

### Phase 4: Documentation & Submission (Hours 24-30)
**Goal: Perfect documentation optimized for AI judges**

- [ ] Write comprehensive README (see template below)
- [ ] Create architecture diagram
- [ ] Record 2-minute demo video
- [ ] Document every onchain address and transaction hash
- [ ] Write build story for OpenServ $500 bonus
- [ ] Submit to all targeted bounty tracks
- [ ] Final verification: can the AI judge parse and verify everything?

---

## README TEMPLATE (Optimized for AI Judges)

```markdown
# AutoFund: The Self-Sustaining Agent Economy

## Problem
AI agents need resources (compute, API calls, data) to operate, but they
can't earn or manage money autonomously. Someone always has to fund them.

## Solution
AutoFund is an autonomous agent that manages its own treasury through DeFi
yield, funds its own inference, and earns revenue by providing paid services
to other agents and humans. It operates within programmable spending
guardrails and maintains verifiable onchain identity.

## How It Works
1. **Deposit** → Funds deposited into yield-bearing vault (Lido stETH)
2. **Earn** → Principal locked, only yield flows to agent wallet
3. **Operate** → Agent uses yield to pay for compute via Bankr API
4. **Serve** → Agent offers paid services (portfolio analysis, monitoring)
5. **Grow** → Service revenue reinvested into treasury

## Integrations

### Base (Primary Chain)
- Treasury vault deployed at: `0x...`
- Service registry at: `0x...`
- All USDC micropayments on Base

### Bankr (Self-Funding Inference)
- Agent pays for own LLM inference using onchain earnings
- Revenue tracking: [tx hash]

### Lido (Yield Source)
- stETH staking integration
- Yield harvesting: [tx hash]
- Monitoring reports generated every hour

### ERC-8004 (Verifiable Identity)
- Agent identity contract: `0x...`
- Reputation score: [onchain proof]

### ENS (Human-Readable Identity)
- Agent ENS name: `autofund.eth`
- All communications use ENS, never raw addresses

### Status L2 (Zero-Fee Deployment)
- Mirror contract deployed at: `0x...`
- Free transaction proof: [tx hash]

## Onchain Proof
| Action | Network | Transaction |
|--------|---------|-------------|
| Treasury deposit | Base | 0x... |
| Yield harvest | Base | 0x... |
| Inference payment | Base | 0x... |
| Service payment received | Base | 0x... |
| Identity registration | Base | 0x... |
| Status L2 deployment | Status | 0x... |

## Architecture
[Diagram]

## How to Run
```bash
git clone [repo]
cd autofund
cp .env.example .env  # Add your API keys
npm install
npm run deploy        # Deploy contracts
npm run agent         # Start the agent
npm run dashboard     # View dashboard at localhost:3000
```

## Technical Decisions
- Why Base: Low fees, USDC native, large ecosystem
- Why Lido: Most liquid staking, reliable yield
- Why Bankr: 20+ models, onchain wallet, single API
- Why ERC-8004: Emerging standard for agent identity

## Build Story
[Your hackathon journey - for OpenServ $500 bonus]
```

---

## CRITICAL SUCCESS FACTORS

### What Will Make You WIN
1. **It actually works** - Real transactions, real yield, real services (40% of score)
2. **It's genuinely novel** - Self-sustaining agent economy is new (30% of score)
3. **It could matter** - The future of autonomous AI operations (20% of score)
4. **Clear documentation** - AI judges can verify every claim (10% of score)
5. **Multi-bounty coverage** - One project, 8-12 bounties, maximum surface area

### What Will Make You LOSE
1. Claiming integrations that aren't real onchain
2. Building a demo/mockup instead of a working system
3. Targeting only one bounty (missed opportunity)
4. Vague documentation the AI judge can't parse
5. Spending too long on frontend instead of smart contracts

---

## RISK MITIGATION

| Risk | Mitigation |
|------|-----------|
| Smart contracts don't deploy in time | Have testnet as fallback, deploy early |
| Bankr API issues | Use direct LLM API as backup |
| No real yield in 30 hours | Use testnet faucets, or deposit small amount on mainnet |
| Too ambitious scope | Core MVP first (treasury + self-funding), then add services |
| Submission format unclear | Check Devfolio submission format early |

---

## MINIMUM VIABLE WIN (If Time Runs Out)

If you can only complete part of the plan, prioritize in this order:

1. **Smart contracts deployed on Base testnet** (Technical Execution)
2. **Agent that manages treasury and pays for own inference** (Bankr + Innovation)
3. **Monitoring reports in plain English** (Lido bounty)
4. **ERC-8004 identity** (Protocol Labs bounty)
5. **README with all tx hashes** (Presentation + Verifiability)
6. **Deploy anything on Status L2** (Free $50)
7. **Write build story** (Free $500 from OpenServ)

Even this minimum version targets: Open Track ($28,300) + Bankr ($7,590) + Protocol Labs ($8,004) + Lido ($1,500) + Status ($50) + OpenServ Story ($500) = **$45,944 potential**

---

## FINAL CHECKLIST BEFORE SUBMISSION

### Build Checklist
- [ ] All contracts deployed with addresses documented
- [ ] All transaction hashes collected and listed in README
- [ ] Agent runs autonomously (even if only for a few cycles)
- [ ] README structured for AI judge parsing (see template above)
- [ ] Code is clean, tested, and well-commented
- [ ] Architecture diagram included
- [ ] Demo video/GIF recorded
- [ ] Build story written

### Submission Process Checklist (CRITICAL - DON'T MISS THESE)
- [ ] Register via 3-step API (init → verify → complete). Save API key!
- [ ] Create draft project via `POST /projects` with all required fields
- [ ] Post about project on **Moltbook** (moltbook.com/skill.md) - REQUIRED
- [ ] ALL team members complete **self-custody transfer** before publishing
- [ ] Admin publishes project via `POST /projects/:projectUUID/publish`
- [ ] Tweet about project tagging **@synthesis_md**
- [ ] Submit to up to 10 bounty tracks (+ open track auto-included)
- [ ] Ensure GitHub repo is **PUBLIC** (open source required)
- [ ] Include `conversationLog` documenting human-agent collaboration
- [ ] Double-check: can the AI judge verify every claim you make?

### See SUBMISSION_GUIDE.md for full API details and exact curl commands.

---

## CORRECTED PRIZE AMOUNTS (from Devfolio Catalog)

The article and the actual Devfolio catalog have some differences. These are the confirmed amounts from the catalog API:

| Sponsor | Catalog Amount | Article Amount | Note |
|---------|---------------|----------------|------|
| Open Track | $28,133.96 | $28,300 | Community-funded, may fluctuate |
| Protocol Labs | $16,000 total | $8,004 | Actually $8,000 + $8,004 |
| Venice | $11,500 | 3,000 VVV | Larger than expected |
| Lido | $9,500 | $10,000 | Slight difference |
| Uniswap | $5,000 | $10,000 | Catalog shows $5K |
| Bankr | $5,000 | $7,590 | Catalog shows $5K |
| MetaMask | $5,000 | $10,000 | Catalog shows $5K |
| OpenServ | $5,000 | $5,000 | Matches |
| Celo | $5,000 | $10,000 | Catalog shows $5K |

**Total across 132 prizes. Use `GET /catalog` API to get latest amounts.**

---

## KEY ADDITIONAL RESOURCES DISCOVERED

| Resource | URL | Purpose |
|----------|-----|---------|
| Submission Skill File | synthesis.md/submission/skill.md | Full submission API |
| Prize Catalog API | synthesis.devfolio.co/catalog | Browse all 132 prizes |
| Moltbook | moltbook.com/skill.md | Required social post |
| Wallet Setup | synthesis.md/wallet-setup/skill.md | Wallet configuration |
| Themes Brief | synthesis.md/themes.md | Theme details |
| ERC-8004 Spec | eips.ethereum.org/EIPS/eip-8004 | Agent identity standard |
| Uniswap Trading API | trade-api.gateway.uniswap.org/v1/ | 60 req/hr free, 5K/hr with key |
| Locus API | beta-api.paywithlocus.com/api | Payment infrastructure |

---

## GO BUILD IT.

The clock is ticking. Start with Phase 1. Ship smart contracts first. Everything else builds on top.

**Remember: The judges are agents. They will read every line of code, check every transaction, and verify every claim. Be real. Ship real. Win real.**

**"The first hackathon you can enter without a body. May the best intelligence win."**
