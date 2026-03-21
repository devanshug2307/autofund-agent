# MEGA STRATEGY: 3 PROJECTS, 132 PRIZES, MAXIMUM COVERAGE

> **60 hours left. This is the definitive plan to maximize winnings.**
> **Deadline: March 22, 2026 at 11:59 PM PT**

---

## WHY 3 PROJECTS, NOT 1

### The Math

| Strategy | Track Slots | Prize Coverage | Risk |
|----------|------------|----------------|------|
| 1 project, 10 tracks | 10 | ~8% of 132 prizes | All eggs in one basket |
| 2 projects, 10 tracks each | 20 | ~15% of 132 prizes | Moderate spread |
| **3 projects, 10 tracks each** | **30** | **~23% of 132 prizes** | **Maximum coverage** |

**Rules that make this work:**
- Max **3 projects per team** (we use all 3)
- Max **10 tracks per project** (we use all 10) + Open Track auto-included
- Each project auto-competes in the **$28,134 Open Track**
- 3 entries in the Open Track = 3x the chance

### The Key Insight
Most teams will submit ONE project. We submit THREE. Each project is genuinely different, targeting a different bounty cluster. Even if only ONE project wins, we're ahead. If two or three win, we dominate.

### Shared Infrastructure Strategy
The 3 projects share a common base layer (wallet, agent framework, deployment scripts) but each has unique logic, contracts, and integrations. This means:
- ~40% of the work is shared across all 3 projects
- Each project takes ~20 hours of unique work
- Total: ~40 hrs shared + ~20 hrs per unique project = doable in 60 hrs if parallelized

---

## THE THREE PROJECTS

---

## PROJECT 1: "AutoFund" - The Self-Sustaining DeFi Agent

### Concept
An autonomous AI agent that earns yield from DeFi, uses that yield to pay for its own compute, executes trades, and provides paid financial services to other agents.

### Why It Wins
- **Self-sustaining economics** is the most talked-about theme
- Every DeFi bounty aligns with this concept
- Working trade + yield = impressive technical demo
- "Agent that actually makes money" is Base's exact ask

### Bounty Targets (10 tracks)

| # | Bounty | Prize | How We Hit It |
|---|--------|-------|---------------|
| 1 | **Bankr** | $5,000 | Agent uses Bankr API for LLM inference, pays with onchain revenue |
| 2 | **Lido - MCP Server** | $5,000 | MCP server for staking stETH via natural language |
| 3 | **Lido - Vault Monitor** | $1,500 | Monitors vault positions, plain English reports |
| 4 | **Lido - Treasury** | $3,000 | Principal locked, only yield flows to agent |
| 5 | **Base - Trading Agent** | $5,000 | Autonomous profitable trading (up to 3 winners) |
| 6 | **Base - Agent Service** | $5,000 | Paid portfolio analysis service (up to 3 winners) |
| 7 | **Uniswap** | $5,000 | Real swaps via Uniswap API |
| 8 | **ZYF AI** | $2,000 | Self-funding from yield earnings |
| 9 | **Bond.Credit** | $1,720 | Live trading on GMX perps |
| 10 | **MoonPay CLI** | $3,500 | Agent uses MoonPay MCP for swaps/bridges |

**+ Open Track: $28,134**

**Total prize potential: $64,854**

### Tech Stack
- **Agent:** Bankr API (20+ LLM models + onchain wallet)
- **Yield:** Lido stETH staking
- **Trading:** Uniswap v4 API + GMX perps on Arbitrum
- **Chain:** Base (primary) + Arbitrum (for Bond.Credit)
- **Payments:** MoonPay CLI MCP server
- **Contracts:** Foundry/Solidity - Treasury vault, spending guardrails

### Implementation Priority
1. Treasury vault contract (deposit, lock principal, yield withdrawal)
2. Bankr API integration (self-funding inference)
3. Lido stETH staking + MCP server
4. Uniswap swap execution
5. Monitoring dashboard with plain English reports
6. Trading strategy for Base/Bond.Credit

---

## PROJECT 2: "TrustNet" - Multi-Agent Identity & Coordination Network

### Concept
A multi-agent system where agents have verifiable onchain identity (ERC-8004), can delegate permissions to each other (MetaMask Delegation Framework), discover and hire each other through a marketplace, and build reputation through onchain receipts.

### Why It Wins
- **"Agents that trust"** is a core hackathon theme
- ERC-8004 is explicitly highlighted by Protocol Labs ($16K total)
- MetaMask wants "unmapped territory" in delegation
- Multi-agent coordination is what OpenServ specifically asks for
- Nobody else will build a full trust + delegation + marketplace system

### Bounty Targets (10 tracks)

| # | Bounty | Prize | How We Hit It |
|---|--------|-------|---------------|
| 1 | **Protocol Labs - Trust Layer** | $8,004 | ERC-8004 identity + reputation + onchain receipts |
| 2 | **Protocol Labs - Autonomous** | $8,000 | Agent operates fully autonomously |
| 3 | **MetaMask - Delegation** | $5,000 | Sub-delegation chains, intent-based delegations |
| 4 | **ENS - Identity** | $600 | Agent uses ENS name for all interactions |
| 5 | **ENS - Communication** | $600 | Human-readable comms, no raw addresses |
| 6 | **ENS - Open Integration** | $300 | ENS integrated throughout |
| 7 | **OpenServ** | $5,000 | Multi-agent system as real product |
| 8 | **Olas** | $3,000+ | Agent in Pearl marketplace, serves 50+ requests |
| 9 | **Self Protocol** | $1,000 | ZK proof of agent identity |
| 10 | **Arkhai** | $1,000 | Escrow protocols for agent-to-agent trust |

**+ Open Track: $28,134**

**Total prize potential: $60,638**

### Tech Stack
- **Identity:** ERC-8004 contracts on Base
- **Delegation:** MetaMask Delegation Framework
- **Names:** ENS integration
- **Marketplace:** Olas Pearl SDK
- **Privacy:** Self Protocol ZK credentials
- **Escrow:** Arkhai Alkahest protocols
- **Agent Framework:** OpenClaw or custom Python

### Implementation Priority
1. ERC-8004 identity contract deployment
2. MetaMask Delegation Framework integration (sub-delegation chains)
3. Agent marketplace (register, discover, hire, pay)
4. ENS name resolution throughout
5. Self Protocol ZK identity proof
6. OpenServ multi-agent coordination demo
7. Arkhai escrow for agent-to-agent transactions

---

## PROJECT 3: "VaultGuard" - Private AI with Verified Compute & Creative Output

### Concept
An AI agent that reasons privately (Venice), executes verifiable computation (EigenCloud TEE), stores data permanently (Filecoin), evaluates public goods impact, and generates evolving digital art - all without exposing sensitive data.

### Why It Wins
- **"Agents that keep secrets"** is a core theme
- Venice wants private reasoning ($11,500 - their biggest single prize)
- EigenCloud wants working Docker + live demo ($5,000)
- Creative angle (SuperRare) differentiates from pure DeFi projects
- Privacy + verifiability is a genuinely novel combo
- Filecoin storage gives it persistence

### Bounty Targets (10 tracks)

| # | Bounty | Prize | How We Hit It |
|---|--------|-------|---------------|
| 1 | **Venice** | $11,500 | Private reasoning over sensitive data, public outputs |
| 2 | **EigenCloud** | $5,000 | Working Docker image in TEE, live demo |
| 3 | **Octant - Mechanism** | $1,000 | Fairer allocation mechanism for public goods |
| 4 | **Octant - Analysis** | $1,000 | Impact data analysis at scale |
| 5 | **Octant - Evidence** | $1,000 | Evidence collection for project legitimacy |
| 6 | **SuperRare** | $5,000 | Autonomous art agent, behavior IS the artwork |
| 7 | **Filecoin** | $2,000 | Agentic storage on Onchain Cloud |
| 8 | **Lit Protocol** | $500 | Private AI skills in TEE |
| 9 | **Virtuals** | $2,000 | ERC-8183 agent interaction standard |
| 10 | **Status L2** | $2,000 | Deploy on zero-fee L2 ($50/team guaranteed) |

**+ Open Track: $28,134**

**Total prize potential: $59,134**

### Tech Stack
- **Private AI:** Venice API (privacy-preserving inference)
- **Verified Compute:** EigenCloud TEE + Docker
- **Storage:** Filecoin Onchain Cloud
- **Art Generation:** Stable Diffusion / DALL-E + Rare Protocol
- **TEE Skills:** Lit Protocol Chipotle runtime
- **Chain:** Base + Status L2
- **Standards:** ERC-8183 agent interaction

### Implementation Priority
1. Venice API integration for private reasoning
2. EigenCloud Docker deployment with TEE proof
3. Public goods analysis agent (Octant)
4. Generative art pipeline + SuperRare minting
5. Filecoin storage integration
6. Status L2 deployment (quick $50)
7. ERC-8183 implementation

---

## COMBINED PRIZE POTENTIAL

| Project | Bounty Prizes | Open Track | Total |
|---------|--------------|------------|-------|
| AutoFund (DeFi) | $36,720 | $28,134 | $64,854 |
| TrustNet (Identity) | $32,504 | $28,134 | $60,638 |
| VaultGuard (Privacy) | $31,000 | $28,134 | $59,134 |
| **COMBINED** | **$100,224** | **$28,134** | **$128,358** |

**Note:** Open Track prize can only be won once, but 3 entries = 3x the probability.

**Realistic estimate:** If you win even 20-30% of targeted prizes, that's **$20K-$38K**.

---

## 60-HOUR EXECUTION TIMELINE

### Phase 1: Foundation (Hours 0-10)
**All 3 projects share this base**

- [ ] Set up monorepo with shared infrastructure
- [ ] Create wallet, fund with testnet ETH
- [ ] Deploy ERC-8004 identity contract (used by all 3)
- [ ] Set up Foundry project with shared contracts
- [ ] Register agent via Synthesis API
- [ ] Deploy basic contract on Status L2 (grab the $50)

### Phase 2: Project 1 - AutoFund (Hours 10-25)
**Primary developer focus**

- [ ] Treasury vault contract (Lido)
- [ ] Bankr API integration (self-funding)
- [ ] Uniswap swap execution
- [ ] Lido MCP server
- [ ] Monitoring agent
- [ ] Basic trading strategy
- [ ] Deploy to Base testnet/mainnet

### Phase 3: Project 2 - TrustNet (Hours 20-40)
**Can overlap with Phase 2**

- [ ] ERC-8004 identity system
- [ ] MetaMask Delegation Framework
- [ ] ENS integration
- [ ] Agent marketplace (Olas)
- [ ] Multi-agent coordination demo
- [ ] Self Protocol ZK identity

### Phase 4: Project 3 - VaultGuard (Hours 30-50)
**Can overlap with Phase 3**

- [ ] Venice API private reasoning
- [ ] EigenCloud Docker/TEE deployment
- [ ] Octant public goods analysis
- [ ] SuperRare art generation
- [ ] Filecoin storage
- [ ] Lit Protocol TEE skill

### Phase 5: Polish & Submit (Hours 50-60)
**All 3 projects**

- [ ] Write 3 READMEs optimized for AI judges
- [ ] Collect all tx hashes and contract addresses
- [ ] Record 3 demo videos
- [ ] Create projects via Synthesis API
- [ ] Post all 3 on Moltbook (REQUIRED)
- [ ] Complete self-custody transfer for all members
- [ ] Publish all 3 projects
- [ ] Tweet about each project tagging @synthesis_md
- [ ] Write build stories for OpenServ bonus

---

## ABOUT THE classified-agent TOOL

### What It Is
- **PyVax** - A tool that transpiles Python to EVM bytecode for Avalanche C-Chain
- Claims to: fetch skill.md, register your agent, deploy on Avalanche, submit

### My Assessment

**PROCEED WITH CAUTION:**

1. **Not an official Synthesis tool** - It's a third-party project
2. **Avalanche is NOT a primary chain** for Synthesis (Base, Ethereum, Celo are)
3. **Security risk** - `pip install` from unknown source that auto-registers and deploys
4. **Auto-submission** could submit before your project is ready
5. **Unknown code execution** - Haven't audited what it actually does

**Recommendation:** Don't use it for registration/submission. Use the official Synthesis API directly (documented in SUBMISSION_GUIDE.md). If you want to experiment with PyVax for Python-to-Solidity transpilation, do it in an isolated environment.

**Why manual is better:**
- You control exactly what gets submitted
- You choose which tracks to submit to
- You can craft submission metadata for AI judges
- No risk of rogue code accessing your keys

---

## SOLO vs TEAM STRATEGY

### If You're Solo (1 person, 60 hours)
**Build 2 projects, not 3.** Focus on:
1. **AutoFund** (DeFi) - Highest prize density
2. **TrustNet** (Identity) - Most innovative, Protocol Labs path to $150K

Drop VaultGuard or build a minimal version.

### If You Have 2 People
Split: Person A builds AutoFund, Person B builds TrustNet. Both collaborate on VaultGuard in remaining time.

### If You Have 3-4 People
Each person owns one project. Fourth person handles shared infra, submission, and documentation.

---

## WHICH BOUNTIES ARE "FREE MONEY"

These require minimal effort and overlap with any project:

| Bounty | Prize | Effort | What To Do |
|--------|-------|--------|-----------|
| Status L2 | $50/team | 10 min | Deploy any contract on Status Sepolia |
| OpenServ Build Story | $500 | 30 min | Write about your hackathon journey |
| Open Track | $28,134 | 0 extra | Every project auto-enters |
| College.xyz | $500 | Low | If you're a student, just submit |

**Guaranteed $550 for 40 minutes of work** (Status + Build Story).

---

## SUBMISSION PROCESS (Per Project)

Repeat this for each of the 3 projects:

```
1. POST /projects  → Create draft with all required fields
2. Post on Moltbook  → Required (moltbook.com/skill.md)
3. POST /projects/:id  → Update with final details
4. Transfer to self-custody  → /participants/me/transfer/init + confirm
5. POST /projects/:id/publish  → Admin publishes (all members must be self-custody)
6. Tweet tagging @synthesis_md
```

### Required Fields Per Project
- `name` - Project name
- `description` - What it does
- `problemStatement` - Problem you solve
- `repoURL` - Public GitHub repo
- `trackUUIDs` - Array of up to 10 bounty track UUIDs
- `conversationLog` - Human-agent collaboration log
- `submissionMetadata` - Additional metadata

### Get Track UUIDs
```bash
curl https://synthesis.devfolio.co/catalog \
  -H "Authorization: Bearer sk-synth-YOUR_KEY"
```

---

## DECISION FRAMEWORK: HOW TO PRIORITIZE IN THE MOMENT

When you're in the middle of building and need to decide what to work on next:

```
IF time < 10 hours remaining:
  → STOP building new features
  → Polish, document, submit all projects
  → Collect tx hashes, write READMEs

IF a feature is taking > 2 hours:
  → Ship minimum viable version
  → Move to next bounty target
  → Come back if time permits

IF choosing between depth vs breadth:
  → Breadth wins (more bounties = more chances)
  → BUT each integration must be GENUINE (AI judges verify)

IF exhausted:
  → Submit what you have NOW
  → You can update published projects until deadline
  → A submitted 70% project beats an unsubmitted 100% project
```

---

## THE WINNER'S MINDSET

1. **Ship > Perfect.** A deployed contract beats a beautiful diagram.
2. **3 projects > 1 project.** Coverage beats depth in a 132-prize hackathon.
3. **Real > Fake.** AI judges verify onchain. One real transaction > 100 mock calls.
4. **Document everything.** The AI judge reads your README like code.
5. **Submit early, update later.** Published projects can be edited until deadline.
6. **Every $50 counts.** Status L2 deployment is 10 minutes for guaranteed money.

---

## GO.

Start with Phase 1 (shared foundation). Then build Project 1 (AutoFund) to at least MVP before touching Project 2. Ship early, iterate fast, submit all 3.

**The hackathon where AI agents judge AI agents. Play the meta-game.**
