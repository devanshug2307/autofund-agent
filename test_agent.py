"""
Python unit tests for AutoFund agent modules.
Tests run offline with no API keys, no RPC, and no network calls.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


# ---------------------------------------------------------------------------
# 1. agent.py — AgentConfig, TreasuryStatus, AutoFundAgent
# ---------------------------------------------------------------------------

class TestAgentConfig:
    """Test AgentConfig dataclass defaults and customization."""

    def test_defaults(self):
        from src.agent import AgentConfig
        cfg = AgentConfig()
        assert cfg.rpc_url == "https://sepolia.base.org"
        assert cfg.chain_id == 84532
        assert cfg.private_key == ""
        assert cfg.bankr_api_key == ""
        assert "ERC-8004" in cfg.erc8004_identity.get("standard", "")

    def test_custom_values(self):
        from src.agent import AgentConfig
        cfg = AgentConfig(chain_id=1, private_key="0xdead")
        assert cfg.chain_id == 1
        assert cfg.private_key == "0xdead"


class TestTreasuryStatus:
    """Test TreasuryStatus dataclass."""

    def test_defaults_are_zero(self):
        from src.agent import TreasuryStatus
        ts = TreasuryStatus()
        assert ts.principal == 0.0
        assert ts.available_yield == 0.0
        assert ts.total_spent == 0.0
        assert ts.last_updated == ""


class TestAutoFundAgent:
    """Test AutoFundAgent initialization and methods that don't need the network."""

    def _make_agent(self):
        from src.agent import AgentConfig, AutoFundAgent
        cfg = AgentConfig()
        return AutoFundAgent(cfg)

    def test_init_creates_account(self):
        agent = self._make_agent()
        assert agent.account is not None
        assert agent.inference_count == 0
        assert agent.total_inference_cost == 0.0
        assert agent.activity_log == []

    def test_log_activity_appends(self):
        agent = self._make_agent()
        agent.log_activity("test_action", {"key": "value"})
        assert len(agent.activity_log) == 1
        assert agent.activity_log[0]["action"] == "test_action"
        assert "timestamp" in agent.activity_log[0]

    def test_check_treasury_status_returns_status(self):
        """check_treasury_status should return a TreasuryStatus even when RPC fails."""
        from src.agent import TreasuryStatus
        agent = self._make_agent()
        # RPC will fail (no real network), but fallback should still return a status
        status = agent.check_treasury_status()
        assert isinstance(status, TreasuryStatus)
        assert status.last_updated != ""

    def test_estimate_cost_known_model(self):
        agent = self._make_agent()
        cost = agent._estimate_cost("hello world", "response text", "claude-sonnet-4-6")
        assert isinstance(cost, float)
        assert cost > 0

    def test_estimate_cost_unknown_model_uses_default(self):
        agent = self._make_agent()
        cost_known = agent._estimate_cost("hello", "resp", "claude-sonnet-4-6")
        cost_unknown = agent._estimate_cost("hello", "resp", "some-unknown-model")
        # Unknown model falls back to sonnet rates, so costs should be equal
        assert cost_known == cost_unknown

    def test_export_activity_log_json(self):
        import json
        agent = self._make_agent()
        agent.log_activity("a", {"x": 1})
        raw = agent.export_activity_log()
        parsed = json.loads(raw)
        assert isinstance(parsed, list)
        assert len(parsed) == 1


# ---------------------------------------------------------------------------
# 2. monitor.py — VaultMonitor, Alert, VaultSnapshot
# ---------------------------------------------------------------------------

class TestVaultMonitor:
    """Test VaultMonitor with mocked network calls."""

    def _make_monitor(self):
        from src.monitor import VaultMonitor
        with patch.object(VaultMonitor, "_fetch_real_lido_apy", return_value=3.5), \
             patch.object(VaultMonitor, "_fetch_real_benchmark_apy", return_value=3.2):
            return VaultMonitor()

    def test_init_current_state(self):
        mon = self._make_monitor()
        assert mon.current_state.steth_apy == 3.5
        assert mon.current_state.benchmark_apy == 3.2
        assert "Aave" in mon.current_state.allocation

    def test_generate_report_is_string(self):
        mon = self._make_monitor()
        report = mon.generate_report()
        assert isinstance(report, str)
        assert "YOUR POSITION" in report
        assert "BENCHMARK COMPARISON" in report

    def test_set_yield_floor(self):
        mon = self._make_monitor()
        msg = mon.set_yield_floor(3.0)
        assert mon.yield_floor == 3.0
        assert "3.0%" in msg

    def test_yield_floor_breach_generates_alert(self):
        from src.monitor import VaultSnapshot
        mon = self._make_monitor()
        mon.set_yield_floor(4.0)  # Floor above current APY of 3.5
        alert = mon.check_yield_floor_breach(mon.current_state)
        assert alert is not None
        assert alert.severity == "critical"
        assert alert.action_required is True

    def test_no_yield_floor_breach_when_above(self):
        mon = self._make_monitor()
        mon.set_yield_floor(2.0)  # Floor below current APY
        alert = mon.check_yield_floor_breach(mon.current_state)
        assert alert is None

    def test_vault_health_returns_dict(self):
        mon = self._make_monitor()
        health = mon.vault_health()
        assert health["status"] == "healthy"
        assert "yield" in health
        assert "allocation" in health
        assert "recommended_actions" in health


# ---------------------------------------------------------------------------
# 3. self_check.py — CycleVerdict, SelfChecker
# ---------------------------------------------------------------------------

class TestSelfChecker:
    """Test SelfChecker and CycleVerdict."""

    def test_cycle_verdict_summary(self):
        from src.self_check import CycleVerdict
        v = CycleVerdict(
            cycle=1, timestamp="t", passed=True,
            treasury_ok=True, yield_positive=True, net_sustainable=True,
            no_critical_alerts=True, inference_budget_ok=True,
            checks_run=6, checks_passed=6,
            details=["All good"], recommendations=[],
        )
        s = v.summary()
        assert "PASS" in s
        assert "6/6" in s

    def test_cycle_verdict_fail(self):
        from src.self_check import CycleVerdict
        v = CycleVerdict(
            cycle=2, timestamp="t", passed=False,
            treasury_ok=False, yield_positive=True, net_sustainable=True,
            no_critical_alerts=True, inference_budget_ok=True,
            checks_run=6, checks_passed=5,
            details=["FAIL: something"], recommendations=["Fix it"],
        )
        s = v.summary()
        assert "FAIL" in s
        assert "5/6" in s


# ---------------------------------------------------------------------------
# 4. uniswap_trader.py — TradingStrategy, TradingSignal, UniswapTrader
# ---------------------------------------------------------------------------

class TestTradingStrategy:
    """Test TradingStrategy defaults."""

    def test_defaults(self):
        from src.uniswap_trader import TradingStrategy
        strat = TradingStrategy()
        assert strat.name == "AutoFund Adaptive Momentum"
        assert strat.base_position_size_pct == 10.0
        assert strat.kelly_fraction == 0.25
        assert strat.max_position_pct == 20.0
        assert strat.min_position_pct == 2.0


class TestTradingSignal:
    """Test TradingSignal creation."""

    def test_creation(self):
        from src.uniswap_trader import TradingSignal
        sig = TradingSignal(
            direction="BUY", confidence=0.8,
            position_size_pct=5.0, momentum=2.1,
            volatility=1.5, reasons=["test"],
        )
        assert sig.direction == "BUY"
        assert sig.confidence == 0.8
        assert sig.reasons == ["test"]


class TestUniswapTrader:
    """Test UniswapTrader offline methods."""

    def _make_trader(self):
        from src.uniswap_trader import UniswapTrader
        return UniswapTrader(api_key="", chain_id=84532)

    def test_init_defaults(self):
        trader = self._make_trader()
        assert trader.chain_id == 84532
        assert "ETH" in trader.portfolio
        assert "USDC" in trader.portfolio
        assert trader.trades == []

    def test_simulate_swap_buy(self):
        trader = self._make_trader()
        trade = trader.simulate_swap("ETH/USDC", "BUY", 1000.0)
        assert trade.side == "BUY"
        assert trade.amount_in == 1000.0
        assert trade.amount_out > 0
        assert trade.status == "simulated"
        assert len(trader.trades) == 1

    def test_simulate_swap_sell(self):
        trader = self._make_trader()
        trade = trader.simulate_swap("ETH/USDC", "SELL", 1.0)
        assert trade.side == "SELL"
        assert trade.amount_out > 0
        assert trade.token_in == "ETH"
        assert trade.token_out == "USDC"

    def test_get_pnl_structure(self):
        trader = self._make_trader()
        pnl = trader.get_pnl()
        assert "initial_value" in pnl
        assert "current_value" in pnl
        assert "pnl_usd" in pnl
        assert "pnl_percent" in pnl
        assert "profitable" in pnl
        assert isinstance(pnl["profitable"], bool)

    def test_calculate_signals_insufficient_history(self):
        """With no price history, signal should be HOLD."""
        trader = self._make_trader()
        trader.price_history = []
        sig = trader.calculate_signals(current_price=3500.0)
        # After one price recorded, still < 2 observations
        assert sig.direction == "HOLD"
        assert sig.confidence == 0.0

    def test_calculate_signals_with_bullish_data(self):
        """Feed rising prices and expect a BUY signal."""
        trader = self._make_trader()
        # Seed 10 rising prices
        import time
        base = 3000.0
        for i in range(10):
            trader.price_history.append({
                "price": base + i * 60,
                "timestamp": time.time() + i,
            })
        sig = trader.calculate_signals(current_price=3600.0)
        assert sig.direction == "BUY"
        assert sig.confidence > 0
        assert sig.position_size_pct > 0

    def test_calculate_signals_with_bearish_data(self):
        """Feed falling prices and expect a SELL signal."""
        trader = self._make_trader()
        import time
        base = 4000.0
        for i in range(10):
            trader.price_history.append({
                "price": base - i * 100,
                "timestamp": time.time() + i,
            })
        sig = trader.calculate_signals(current_price=2800.0)
        assert sig.direction == "SELL"
        assert sig.confidence > 0


# ---------------------------------------------------------------------------
# 5. bankr_integration.py — BankrGateway
# ---------------------------------------------------------------------------

class TestBankrGateway:
    """Test BankrGateway offline."""

    def _make_gw(self):
        from src.bankr_integration import BankrGateway
        return BankrGateway(api_key="test_key_12345")

    def test_init(self):
        gw = self._make_gw()
        assert gw.api_key == "test_key_12345"
        assert gw.total_cost == 0.0
        assert gw.budget_remaining == 100.0

    def test_select_optimal_model(self):
        gw = self._make_gw()
        assert gw.select_optimal_model("simple") == "gemini-2.0-flash"
        assert gw.select_optimal_model("moderate") == "gpt-4o-mini"
        assert gw.select_optimal_model("complex") == "claude-sonnet-4-6"
        assert gw.select_optimal_model("critical") == "claude-opus-4-6"
        # Unknown complexity falls back to sonnet
        assert gw.select_optimal_model("unknown") == "claude-sonnet-4-6"

    def test_estimate_cost_positive(self):
        gw = self._make_gw()
        cost = gw._estimate_cost("What is ETH price?", 512, "claude-sonnet-4-6")
        assert cost > 0

    def test_chat_budget_exceeded(self):
        gw = self._make_gw()
        gw.budget_remaining = 0.0
        result = gw.chat("hello", model="claude-opus-4-6", max_tokens=4096)
        assert "error" in result
        assert "Insufficient budget" in result["error"]


# ---------------------------------------------------------------------------
# 6. celo_integration.py — CeloAgent, RemittanceQuote, constants
# ---------------------------------------------------------------------------

class TestCeloConstants:
    """Test that Celo stablecoin constants are well-formed."""

    def test_stablecoin_entries(self):
        from src.celo_integration import CELO_STABLECOINS
        for symbol in ("cUSD", "cEUR", "cREAL", "USDC"):
            assert symbol in CELO_STABLECOINS
            info = CELO_STABLECOINS[symbol]
            assert "decimals" in info
            assert "name" in info
            assert info["decimals"] in (6, 18)


class TestRemittanceQuote:
    """Test RemittanceQuote dataclass creation."""

    def test_creation(self):
        from src.celo_integration import RemittanceQuote
        q = RemittanceQuote(
            from_currency="cUSD", to_currency="cEUR",
            from_amount=100.0, to_amount=92.5,
            exchange_rate=0.925, fee_usd=0.25,
            estimated_time="< 5 seconds", tx_cost_usd=0.001,
        )
        assert q.from_currency == "cUSD"
        assert q.to_amount == 92.5
        assert q.fee_usd == 0.25


class TestCeloAgent:
    """Test CeloAgent initialization and offline methods."""

    def _make_agent(self):
        from src.celo_integration import CeloAgent
        return CeloAgent(network="alfajores")

    def test_init(self):
        agent = self._make_agent()
        assert agent.network == "alfajores"
        assert agent.chain_id == 44787
        assert agent.operations_log == []

    @patch("httpx.Client")
    def test_quote_remittance_cusd_to_ceur(self, mock_httpx_client):
        """Test remittance quoting logic with mocked FX rates."""
        agent = self._make_agent()
        # Mock _get_stablecoin_fx_rates to avoid network
        with patch.object(agent, "_get_stablecoin_fx_rates",
                          return_value={"cUSD": 1.0, "cEUR": 1.08, "cREAL": 0.18, "USDC": 1.0}):
            quote = agent.quote_remittance("cUSD", "cEUR", 100.0)
        assert quote.from_currency == "cUSD"
        assert quote.to_currency == "cEUR"
        assert quote.from_amount == 100.0
        # rate = 1.0 / 1.08 ~ 0.9259; to_amount ~ 100 * 0.9259 * 0.9975
        assert quote.to_amount > 0
        assert quote.exchange_rate > 0
        assert quote.fee_usd > 0
        assert "seconds" in quote.estimated_time

    @patch("httpx.Client")
    def test_quote_remittance_zero_amount(self, mock_httpx_client):
        """Zero-amount remittance should yield zero output."""
        agent = self._make_agent()
        with patch.object(agent, "_get_stablecoin_fx_rates",
                          return_value={"cUSD": 1.0, "cEUR": 1.08, "USDC": 1.0, "cREAL": 0.18}):
            quote = agent.quote_remittance("cUSD", "cEUR", 0.0)
        assert quote.to_amount == 0.0
        assert quote.fee_usd == 0.0

    def test_get_capabilities_summary(self):
        agent = self._make_agent()
        caps = agent.get_capabilities_summary()
        assert caps["network"] == "alfajores"
        assert len(caps["capabilities"]) > 0
        names = [c["name"] for c in caps["capabilities"]]
        assert "Fee Abstraction" in names
        assert "Cross-Border Remittance" in names
