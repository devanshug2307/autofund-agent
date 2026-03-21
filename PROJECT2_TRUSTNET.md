# PROJECT 2: TrustNet - Multi-Agent Identity & Coordination Network

> **How does one agent know it can trust another?**

---

## Elevator Pitch
TrustNet is a multi-agent coordination system where agents have verifiable onchain identity (ERC-8004), can delegate scoped permissions to each other (MetaMask Delegation Framework), discover and hire each other through a marketplace (Olas), and build reputation through onchain receipts. It answers Protocol Labs' core question: "How does one agent know it can trust another?"

---

## Problem Statement
As agents proliferate, trust becomes the bottleneck. Today there's no standard way for agents to prove who they are, verify what they can do, or enforce agreements with each other. TrustNet builds the trust infrastructure layer.

---

## Architecture

```
┌───────────────────────────────────────────────────┐
│                   TRUSTNET                         │
├───────────────────────────────────────────────────┤
│                                                     │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐ │
│  │  Identity   │  │ Delegation │  │  Marketplace │ │
│  │  Layer      │  │ Layer      │  │  Layer       │ │
│  │             │  │            │  │              │ │
│  │  ERC-8004   │  │  MetaMask  │  │  Olas Pearl  │ │
│  │  + ENS      │  │  Framework │  │  + OpenServ  │ │
│  │  + Self ZK  │  │            │  │              │ │
│  └──────┬──────┘  └──────┬─────┘  └──────┬───────┘ │
│         │               │               │          │
│         ▼               ▼               ▼          │
│  ┌─────────────────────────────────────────────┐   │
│  │           TRUST PROTOCOL (Base)              │   │
│  │                                              │   │
│  │  Identity     Delegation    Escrow           │   │
│  │  Registry     Manager       (Arkhai)         │   │
│  │  ┌────────┐  ┌──────────┐  ┌────────────┐  │   │
│  │  │register│  │delegate  │  │createEscrow│  │   │
│  │  │verify  │  │subDelegate│ │release     │  │   │
│  │  │attest  │  │revoke    │  │dispute     │  │   │
│  │  │repScore│  │checkPerms│  │resolve     │  │   │
│  │  └────────┘  └──────────┘  └────────────┘  │   │
│  └─────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────┘
```

---

## How Agents Interact in TrustNet

### Scenario: Agent A hires Agent B for a task

```
1. Agent A checks Agent B's ERC-8004 identity
   → Verified: identity contract at 0x..., reputation score: 87/100
   → ENS name: agent-b.trustnet.eth

2. Agent A creates a scoped delegation via MetaMask
   → Agent B can only: read portfolio data, execute max $100 in swaps
   → Delegation expires in 24 hours
   → Sub-delegation: Agent B can grant Agent C read-only access

3. Agent A creates escrow via Arkhai
   → $50 USDC locked in escrow
   → Release condition: task completed + verified onchain

4. Agent B completes the task
   → Onchain receipt generated (ERC-8004)
   → Agent A verifies + releases escrow
   → Agent B's reputation score increases

5. Both agents' interaction is logged onchain
   → Future agents can see this trust history
   → Marketplace ranking updated
```

---

## Smart Contracts

### 1. TrustRegistry.sol (ERC-8004)
```solidity
// Agent identity + reputation
struct AgentIdentity {
    address agent;
    string ensName;
    uint256 registrationTime;
    uint256 reputationScore;      // 0-100
    uint256 tasksCompleted;
    uint256 tasksFailed;
    bytes32 zkIdentityProof;      // Self Protocol
}

function registerAgent(string memory ensName) external returns (uint256 agentId)
function attestCompletion(uint256 agentId, uint256 taskId) external
function getReputation(uint256 agentId) public view returns (uint256)
function verifyIdentity(uint256 agentId, bytes memory zkProof) external returns (bool)
```

### 2. DelegationManager.sol (MetaMask Framework)
```solidity
struct Delegation {
    address delegator;
    address delegatee;
    bytes32[] permissions;        // Scoped capabilities
    uint256 expiry;
    uint256 spendLimit;
    bool canSubDelegate;
    uint256 subDelegationDepth;   // Max chain length
}

function createDelegation(Delegation memory d) external returns (uint256 delegationId)
function subDelegate(uint256 parentId, address newDelegatee, bytes32[] memory subPerms) external
function checkPermission(address agent, bytes32 permission) public view returns (bool)
function revokeDelegation(uint256 delegationId) external
```

### 3. AgentEscrow.sol (Arkhai)
```solidity
function createEscrow(address counterparty, uint256 amount, bytes32 completionCondition) external
function releaseEscrow(uint256 escrowId) external
function disputeEscrow(uint256 escrowId, bytes memory evidence) external
function resolveDispute(uint256 escrowId, address winner) external  // By arbitrator
```

---

## Bounty-Specific Implementation

### Protocol Labs - Trust Layer ($8,004)
The ENTIRE project IS the trust layer. ERC-8004 identity + reputation + onchain receipts.

### Protocol Labs - Autonomous ($8,000)
The agent autonomously:
1. Discovers other agents via marketplace
2. Evaluates their reputation
3. Creates delegations
4. Hires agents for tasks
5. Verifies completion
6. Updates reputation scores
All without human intervention.

### MetaMask - Delegation Framework ($5,000)
**"Standard implementations won't win"** - We go deep:
- **Intent-based delegations:** "Allow Agent B to swap up to $100 of ETH for USDC in the next 24 hours"
- **Sub-delegation chains:** Agent A → Agent B → Agent C, each with narrower permissions
- **Automatic revocation:** Delegation expires on time or spend limit
- **ZK-powered authorization:** Prove you have permission without revealing the full delegation chain

### ENS ($1,730)
- Every agent has an ENS name (agent-name.trustnet.eth)
- All logs, receipts, and communications use ENS names
- Never display a raw 0x address to any user or agent
- ENS resolution integrated into every contract interaction

### OpenServ ($5,000)
- Multi-agent system as a REAL product
- Agents coordinate: one agent discovers tasks, another executes, another verifies
- x402-native: agents pay each other at moment of use

### Olas ($3,000+)
- Register TrustNet agents in Pearl marketplace
- Serve 50+ requests from other agents (reputation queries, delegation creation)
- Monetize: other agents pay to use the trust infrastructure

---

## Key Innovation
**The delegation chain with ZK authorization.** No one has built:
- Agent A delegates to Agent B with spend limit
- Agent B sub-delegates read-only access to Agent C
- Agent C proves it has permission via ZK proof without revealing the chain
- All enforced onchain with automatic expiry

This is MetaMask's "unmapped territory."

---

## Deliverables Checklist

- [ ] TrustRegistry.sol (ERC-8004) deployed on Base
- [ ] DelegationManager.sol deployed on Base
- [ ] AgentEscrow.sol deployed on Base
- [ ] ENS integration throughout
- [ ] Self Protocol ZK identity integration
- [ ] Multi-agent coordination demo (3+ agents interacting)
- [ ] Olas Pearl marketplace registration
- [ ] 50+ service requests served (for Olas bounty)
- [ ] Sub-delegation chain demo with ZK proofs
- [ ] All tx hashes and contract addresses documented
- [ ] Demo video showing agent-to-agent trust flow
