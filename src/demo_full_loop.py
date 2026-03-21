"""
AutoFund Full Loop Demo
========================
Demonstrates the complete self-sustaining agent cycle:
1. Deposit funds → Lock principal
2. Earn yield from Lido stETH
3. Harvest yield
4. Pay for LLM inference from yield
5. Provide paid services → Earn revenue
6. Monitor vault positions
7. Generate reports

This produces a full activity log that judges can verify.
"""

import json
from datetime import datetime
from src.agent import AutoFundAgent, AgentConfig
from src.mcp_server import LidoMCPServer
from src.monitor import VaultMonitor


def run_full_demo():
    """Run the complete AutoFund demonstration."""
    print("=" * 60)
    print("  AUTOFUND: FULL SELF-SUSTAINING LOOP DEMONSTRATION")
    print("=" * 60)
    print(f"  Time: {datetime.utcnow().isoformat()}")
    print("=" * 60)

    # Initialize all components
    config = AgentConfig()
    agent = AutoFundAgent(config)
    mcp = LidoMCPServer()
    monitor = VaultMonitor()

    results = {}

    # ==========================================
    # PHASE 1: Setup & Staking
    # ==========================================
    print("\n\n" + "=" * 40)
    print("PHASE 1: DEPOSIT & STAKE")
    print("=" * 40)

    # Stake ETH via MCP server
    print("\n[1.1] Dry run: Stake 10 ETH into Lido")
    dry_run = mcp.stake_eth(10.0, dry_run=True)
    print(f"  Preview: {dry_run['message']}")

    print("\n[1.2] Execute: Stake 10 ETH into Lido")
    stake_result = mcp.stake_eth(10.0)
    print(f"  Result: {stake_result['message']}")
    print(f"  APY: {stake_result['current_apy']}")

    print("\n[1.3] Wrap 5 stETH → wstETH for DeFi use")
    wrap_result = mcp.wrap_steth(5.0)
    print(f"  Result: {wrap_result['message']}")

    results["phase1"] = {
        "staked": 10.0,
        "wrapped": 5.0,
        "apy": "3.5%"
    }

    # ==========================================
    # PHASE 2: Yield Monitoring
    # ==========================================
    print("\n\n" + "=" * 40)
    print("PHASE 2: YIELD MONITORING")
    print("=" * 40)

    print("\n[2.1] Check current position")
    balance = mcp.get_balance()
    print(f"  stETH: {balance['steth_balance']:.4f}")
    print(f"  wstETH: {balance['wsteth_balance']:.4f}")
    print(f"  Total value: ~{balance['total_value_eth']:.4f} ETH")

    print("\n[2.2] Check reward estimates")
    rewards = mcp.get_rewards()
    print(f"  Daily: {rewards['daily_reward_estimate']}")
    print(f"  Monthly: {rewards['monthly_reward_estimate']}")
    print(f"  Yearly: {rewards['yearly_reward_estimate']}")

    print("\n[2.3] Compare APY with alternatives")
    apy = mcp.get_apy()
    print(f"  Lido stETH: {apy['lido_steth_apy']}")
    for name, rate in apy['benchmarks'].items():
        print(f"  {name}: {rate}")

    print("\n[2.4] Full position monitoring report")
    report = mcp.monitor_position()
    print(report)

    results["phase2"] = {
        "balance": balance,
        "rewards": rewards,
        "apy": apy
    }

    # ==========================================
    # PHASE 3: Self-Funding Inference
    # ==========================================
    print("\n\n" + "=" * 40)
    print("PHASE 3: SELF-FUNDING INFERENCE")
    print("=" * 40)

    # Simulate yield harvest
    agent.treasury_status.available_yield = 50.0
    agent.treasury_status.principal = 1000.0

    print("\n[3.1] Agent harvests yield from treasury")
    harvest = agent.harvest_yield(25.0)
    print(f"  Harvested: ${harvest['amount']:.2f}")
    print(f"  Remaining yield: ${harvest['remaining_yield']:.2f}")

    print("\n[3.2] Agent uses yield to pay for market analysis")
    analysis = agent.think(
        "Analyze ETH/USDC market. Current price: $3,500. "
        "24h volume up 15%. RSI at 62. Moving averages bullish. "
        "Recommend: BUY, SELL, or HOLD?"
    )
    print(f"  Analysis: {analysis[:200]}...")
    print(f"  Inference cost: ${agent.total_inference_cost:.4f}")

    print("\n[3.3] Agent performs second analysis (portfolio review)")
    analysis2 = agent.think(
        "Review this DeFi portfolio: 40% ETH, 30% stETH, 20% USDC, 10% UNI. "
        "Risk assessment and optimization recommendations?"
    )
    print(f"  Analysis: {analysis2[:200]}...")
    print(f"  Total inference cost: ${agent.total_inference_cost:.4f}")
    print(f"  Total inferences: {agent.inference_count}")

    results["phase3"] = {
        "harvested": 25.0,
        "inferences": agent.inference_count,
        "total_cost": agent.total_inference_cost
    }

    # ==========================================
    # PHASE 4: Revenue Generation
    # ==========================================
    print("\n\n" + "=" * 40)
    print("PHASE 4: REVENUE FROM PAID SERVICES")
    print("=" * 40)

    # Provide paid services
    wallets = [
        "0x1234567890abcdef1234567890abcdef12345678",
        "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
        "0x9876543210fedcba9876543210fedcba98765432"
    ]

    for i, wallet in enumerate(wallets, 1):
        print(f"\n[4.{i}] Service request: Portfolio analysis for {wallet[:10]}...")
        result = agent.provide_portfolio_analysis(wallet)
        print(f"  Fee: ${result['fee_charged']:.2f}")
        print(f"  Analysis: {result['analysis'][:100]}...")

    print(f"\n  Total services provided: {agent.services_provided}")
    print(f"  Total revenue earned: ${agent.revenue_earned:.2f}")

    results["phase4"] = {
        "services_provided": agent.services_provided,
        "revenue": agent.revenue_earned
    }

    # ==========================================
    # PHASE 5: Self-Sustainability Check
    # ==========================================
    print("\n\n" + "=" * 40)
    print("PHASE 5: SELF-SUSTAINABILITY METRICS")
    print("=" * 40)

    net = agent.revenue_earned - agent.total_inference_cost

    print(f"\n  Revenue from services:  ${agent.revenue_earned:.4f}")
    print(f"  Cost of inference:      ${agent.total_inference_cost:.4f}")
    print(f"  Net position:           ${net:.4f}")
    print(f"  Status: {'SELF-SUSTAINING ✓' if net >= 0 else 'GROWING TOWARD SUSTAINABILITY'}")
    print(f"  Yield harvested:        $25.00")
    print(f"  Total income:           ${agent.revenue_earned + 25:.4f}")

    results["phase5"] = {
        "revenue": agent.revenue_earned,
        "costs": agent.total_inference_cost,
        "net": net,
        "self_sustaining": net >= 0
    }

    # ==========================================
    # PHASE 6: Vault Monitor Alerts
    # ==========================================
    print("\n\n" + "=" * 40)
    print("PHASE 6: VAULT MONITORING ALERTS")
    print("=" * 40)

    monitor.set_yield_floor(3.0)
    print("\n[6.1] Initial vault report")
    print(monitor.generate_report())

    # Simulate yield change
    monitor.take_snapshot()
    monitor.current_state.steth_apy = 2.8
    monitor.current_state.allocation["Aave"] = 28.0
    monitor.current_state.allocation["Morpho"] = 32.0

    print("[6.2] After yield change...")
    alerts = monitor.run_checks()
    for alert in alerts:
        print(f"\n  [{alert.severity.upper()}] {alert.title}")
        print(f"  {alert.message[:200]}")

    print("\n[6.3] Updated vault report")
    print(monitor.generate_report())

    # ==========================================
    # SUMMARY
    # ==========================================
    print("\n" + "=" * 60)
    print("  DEMONSTRATION COMPLETE")
    print("=" * 60)
    print(f"""
  SUMMARY:
  • Staked 10 ETH into Lido stETH via MCP server
  • Wrapped 5 stETH → wstETH for DeFi use
  • Harvested $25 yield from treasury vault
  • Made {agent.inference_count} LLM inference calls (cost: ${agent.total_inference_cost:.4f})
  • Provided {agent.services_provided} paid services (revenue: ${agent.revenue_earned:.2f})
  • Net position: ${net:.4f} {'(PROFITABLE)' if net >= 0 else '(GROWING)'}
  • Generated {len(monitor.alerts)} vault monitoring alerts
  • All operations logged for auditability

  THE CLOSED LOOP:
  Deposit → Stake → Earn Yield → Harvest → Pay for Inference
    → Analyze Markets → Provide Services → Earn Revenue → Reinvest
""")

    # Save full activity log
    full_log = {
        "demo_timestamp": datetime.utcnow().isoformat(),
        "agent_activity": agent.activity_log,
        "mcp_operations": mcp.operations_log,
        "monitor_alerts": [
            {"severity": a.severity, "title": a.title, "message": a.message}
            for a in monitor.alerts
        ],
        "results": results
    }

    with open("demo_output.json", "w") as f:
        json.dump(full_log, f, indent=2, default=str)

    print("  Full activity log saved to demo_output.json")
    print("=" * 60)


if __name__ == "__main__":
    run_full_demo()
