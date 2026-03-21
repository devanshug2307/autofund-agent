# SYNTHESIS HACKATHON - JUDGING SYSTEM DEEP ANALYSIS

> **How to get the highest score from both AI and human judges**

---

## THE JUDGING SYSTEM

### AI Agent Judges (Powered by Bonfires AI)
Every partner has deployed an AI agent judge. These are NOT human reviewers glancing at your README. These are autonomous agents that:

1. **Read your code** - They will parse your repository, understand your architecture
2. **Read your documentation** - Every word in your README, docs, and comments matters
3. **Check your onchain activity** - Real deployments, real transactions, real receipts
4. **Cross-reference claims vs reality** - If you say "real swaps on Uniswap," they VERIFY it happened onchain

### The Meta-Agent (Open Track)
For the $28,300 Open Track, a META-AGENT synthesizes evaluations from ALL partner judges into a single combined verdict. This means:
- More partner tools you genuinely integrate = more judges evaluate you positively
- Each partner judge feeds into the meta-agent's combined score
- Breadth of genuine integration matters more than depth in one area

### Partner Track Judges
Each partner has their own judge evaluating against their SPECIFIC bounty criteria. These are independent from the meta-agent.

---

## JUDGING CRITERIA (Official Weights)

### 1. Technical Execution - 40% (HIGHEST WEIGHT)
**What they check:**
- Does it actually work? Not a mockup. Not a demo. WORKING code.
- Is the code solid? Clean, well-structured, no obvious bugs.
- Is the integration GENUINE, not decorative?
  - "Decorative" = importing a library but only using it for a hello world
  - "Genuine" = the partner's tool is load-bearing infrastructure in your project

**How to max this score:**
- Deploy to mainnet or testnet with REAL transactions
- Generate onchain receipts the judge agent can verify
- Write clean, well-commented code (the AI reads it)
- Have actual error handling and edge cases covered
- Run real tests that pass
- Make integrations core to your architecture, not bolted on

### 2. Innovation - 30%
**What they check:**
- Is this something new?
- Does it make people stop and think?
- Novel combination of existing tools counts

**How to max this score:**
- Combine partner tools in ways nobody has before
- Address a real problem that hasn't been solved
- The "self-sustaining agent economy" concept is inherently innovative
- Show emergent behavior from agent autonomy
- Push boundaries of what agents can do onchain

### 3. Potential Impact - 20%
**What they check:**
- If this shipped for real, would it matter?
- Does it solve a real problem for real users?
- Scale potential

**How to max this score:**
- Frame your project as solving a real-world problem
- Show clear use cases beyond the hackathon
- Demonstrate potential for adoption
- Global accessibility (Celo's emphasis) scores here
- Protocol Labs path to accelerator = long-term impact signal

### 4. Presentation - 10%
**What they check:**
- Can you explain what you built and why?
- Clear documentation
- Demo quality

**How to max this score:**
- Crystal-clear README with architecture diagrams
- Video demo or GIF walkthrough
- Explain the WHY, not just the WHAT
- Show before/after or problem/solution framing

---

## HOW TO OPTIMIZE FOR AI JUDGES SPECIFICALLY

### Structure Your README for Machine Parsing
AI judges parse your documentation. Structure it for maximum signal:

```markdown
# Project Name

## Problem
[One clear sentence about what problem you solve]

## Solution
[One clear sentence about your approach]

## Architecture
[Diagram or clear description of how components connect]

## Integrations
- **[Partner Name]**: [Exactly how you use their tool, with links to code]
- **[Partner Name]**: [Exactly how you use their tool, with links to code]

## Onchain Activity
- Contract deployed at: [address]
- Transaction receipts: [links]
- Network: [mainnet/testnet]

## How to Run
[Step-by-step instructions that actually work]

## Technical Details
[Architecture decisions, trade-offs, what makes this novel]
```

### Make Onchain Activity Verifiable
The judges CROSS-REFERENCE claims. This means:
- Deploy real smart contracts (include addresses in README)
- Execute real transactions (include tx hashes)
- Use real APIs (show API integration, not mocks)
- If claiming "makes money" - show the actual P&L onchain

### Code Quality Signals AI Judges Detect
- Consistent code style
- Meaningful variable/function names
- Error handling
- Tests that pass
- No hardcoded secrets
- Clean git history with meaningful commit messages
- Modular architecture

### Documentation Keywords That Signal Genuine Integration
Instead of: "We integrated Uniswap"
Write: "Our agent executes swaps via Uniswap v4 Hooks on Unichain, using Permit2 for gasless approvals. See contract at 0x... and swap transaction at 0x..."

The AI judge will:
1. Parse the address
2. Check if the contract exists
3. Verify the transaction happened
4. Confirm it used the claimed protocols

---

## WHAT LOSES POINTS

1. **Decorative integrations** - Importing an SDK but not actually using it
2. **Claims without proof** - Saying "deployed on mainnet" without addresses
3. **Mockups and wireframes** - They want working code
4. **Copy-paste boilerplate** - The AI can detect starter templates with minimal modification
5. **No onchain activity** - If it's a blockchain hackathon and nothing is onchain, you lose
6. **Vague documentation** - "This project does cool things with AI and blockchain"
7. **Standard implementations** - MetaMask explicitly says "standard implementations won't win"

---

## MULTI-BOUNTY OPTIMIZATION STRATEGY

Since the meta-agent synthesizes ALL partner judge scores:

```
More genuine integrations
  → More partner judges score you well
    → Higher meta-agent combined verdict
      → Higher chance at the $28,300 Open Track
        → PLUS you win individual partner bounties
```

**The optimal approach is ONE project that genuinely integrates 5-8 partner tools**, each used as real infrastructure, not decorative imports.

---

## TIMELINE FOR JUDGING

| Date | Event |
|------|-------|
| March 22 (11:59 PM PT) | Building ends, submissions close |
| March 23 | Judging opens - AI agents begin evaluating |
| March 25 | Winners decided and announced |

**Key insight:** You have ~2 days of AI evaluation. The judges have TIME to deeply analyze your code, onchain activity, and documentation. This is not a 5-minute demo pitch. They will be thorough.

---

## WHAT THE BEST PROJECTS WILL HAVE

1. Working, deployed code with real onchain transactions
2. Multi-partner integration where each tool is genuinely used
3. Clear, structured documentation optimized for both human and AI reading
4. A novel concept that makes judges "stop and think"
5. Real-world applicability beyond the hackathon
6. Clean code with tests
7. Verifiable onchain receipts for every claimed integration
8. A compelling narrative about WHY this matters
