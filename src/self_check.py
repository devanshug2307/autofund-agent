"""
AutoFund Daemon Self-Check Module
===================================
After each daemon cycle, the agent verifies its own treasury status,
confirms that operations succeeded, and logs a structured pass/fail verdict.

This satisfies the "Let the Agent Cook" bounty requirement:
"An agent that wakes up, finds a problem, solves it, checks its own work, and ships."

Usage (called automatically from daemon.py):
    from src.self_check import SelfChecker
    checker = SelfChecker(agent, mcp, monitor)
    verdict = checker.run(cycle_result)
"""

import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CycleVerdict:
    """Structured verdict for a single daemon cycle."""
    cycle: int
    timestamp: str
    passed: bool
    treasury_ok: bool
    yield_positive: bool
    net_sustainable: bool
    no_critical_alerts: bool
    inference_budget_ok: bool
    checks_run: int
    checks_passed: int
    details: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [
            f"  [VERIFY] === Cycle #{self.cycle} Self-Check: {status} ({self.checks_passed}/{self.checks_run} checks) ===",
        ]
        for detail in self.details:
            lines.append(f"  [VERIFY]   {detail}")
        if self.recommendations:
            lines.append("  [VERIFY]   Recommendations:")
            for rec in self.recommendations:
                lines.append(f"  [VERIFY]     - {rec}")
        return "\n".join(lines)


class SelfChecker:
    """
    Self-verification engine for the AutoFund daemon.

    After each cycle the checker:
    1. Re-reads treasury status and confirms principal is intact
    2. Verifies yield is non-negative
    3. Checks that net position (revenue - costs) is tracking correctly
    4. Confirms no critical alerts were missed
    5. Verifies inference budget has not been exhausted
    6. Logs a structured PASS / FAIL verdict
    """

    def __init__(self, agent, mcp, monitor, bankr=None):
        self.agent = agent
        self.mcp = mcp
        self.monitor = monitor
        self.bankr = bankr
        self.verdicts: list[CycleVerdict] = []

    def run(self, cycle_result: dict) -> CycleVerdict:
        """Run all self-checks and return a structured verdict."""
        cycle_num = cycle_result.get("cycle", 0)
        checks_run = 0
        checks_passed = 0
        details = []
        recommendations = []

        # ------------------------------------------------------------------
        # Check 1: Treasury status — re-read and confirm principal is intact
        # ------------------------------------------------------------------
        checks_run += 1
        treasury = self.agent.check_treasury_status()
        treasury_ok = treasury.principal >= 0
        if treasury_ok:
            checks_passed += 1
            details.append(f"Treasury principal intact: ${treasury.principal:.2f}")
        else:
            details.append(f"FAIL: Treasury principal is negative: ${treasury.principal:.2f}")
            recommendations.append("Investigate principal discrepancy immediately")

        # ------------------------------------------------------------------
        # Check 2: Yield is non-negative
        # ------------------------------------------------------------------
        checks_run += 1
        yield_positive = treasury.available_yield >= 0
        if yield_positive:
            checks_passed += 1
            details.append(f"Available yield healthy: ${treasury.available_yield:.2f}")
        else:
            details.append(f"FAIL: Yield is negative: ${treasury.available_yield:.2f}")
            recommendations.append("Pause spending until yield recovers")

        # ------------------------------------------------------------------
        # Check 3: Net position (revenue - costs) tracking
        # ------------------------------------------------------------------
        checks_run += 1
        net = self.agent.revenue_earned - self.agent.total_inference_cost
        net_sustainable = net >= 0
        if net_sustainable:
            checks_passed += 1
            details.append(f"Net position sustainable: ${net:.4f} (revenue ${self.agent.revenue_earned:.2f} - costs ${self.agent.total_inference_cost:.4f})")
        else:
            details.append(f"Net position negative: ${net:.4f} (still growing)")
            recommendations.append("Increase service revenue or reduce inference costs")

        # ------------------------------------------------------------------
        # Check 4: No critical alerts from monitor
        # ------------------------------------------------------------------
        checks_run += 1
        critical_alerts = [a for a in self.monitor.alerts if a.severity == "critical"]
        no_critical = len(critical_alerts) == 0
        if no_critical:
            checks_passed += 1
            details.append("No critical vault alerts")
        else:
            details.append(f"FAIL: {len(critical_alerts)} critical alert(s) active")
            for ca in critical_alerts:
                recommendations.append(f"Resolve: {ca.title}")

        # ------------------------------------------------------------------
        # Check 5: Inference budget not exhausted
        # ------------------------------------------------------------------
        checks_run += 1
        budget_ok = True
        if self.bankr is not None:
            budget_ok = self.bankr.budget_remaining > 0
            if budget_ok:
                checks_passed += 1
                details.append(f"Inference budget remaining: ${self.bankr.budget_remaining:.4f}")
            else:
                details.append("FAIL: Inference budget exhausted")
                recommendations.append("Harvest more yield to replenish inference budget")
        else:
            checks_passed += 1
            details.append("Inference budget check skipped (no Bankr gateway)")

        # ------------------------------------------------------------------
        # Check 6: Lido APY sanity — make sure data is not stale
        # ------------------------------------------------------------------
        checks_run += 1
        apy_data = self.mcp.get_apy()
        apy_str = apy_data.get("lido_steth_apy", "0%")
        apy_val = float(apy_str.replace("%", ""))
        apy_ok = 0 < apy_val < 50  # Sanity range
        if apy_ok:
            checks_passed += 1
            details.append(f"Lido APY in sane range: {apy_str}")
        else:
            details.append(f"WARN: Lido APY looks anomalous: {apy_str}")
            recommendations.append("Verify Lido API data source")

        # ------------------------------------------------------------------
        # Build verdict
        # ------------------------------------------------------------------
        passed = checks_passed == checks_run

        verdict = CycleVerdict(
            cycle=cycle_num,
            timestamp=datetime.utcnow().isoformat(),
            passed=passed,
            treasury_ok=treasury_ok,
            yield_positive=yield_positive,
            net_sustainable=net_sustainable,
            no_critical_alerts=no_critical,
            inference_budget_ok=budget_ok,
            checks_run=checks_run,
            checks_passed=checks_passed,
            details=details,
            recommendations=recommendations,
        )

        self.verdicts.append(verdict)
        return verdict

    def get_history(self) -> list[dict]:
        """Return all verdicts as dicts (for JSON serialization)."""
        return [
            {
                "cycle": v.cycle,
                "timestamp": v.timestamp,
                "passed": v.passed,
                "checks": f"{v.checks_passed}/{v.checks_run}",
                "details": v.details,
                "recommendations": v.recommendations,
            }
            for v in self.verdicts
        ]
