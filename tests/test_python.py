"""
Python Unit Tests for AutoFund Agent
======================================
Tests pure logic in the Python agent modules without requiring
any API keys, RPC connections, or network access.

Run: python3 -m pytest tests/ -v
"""

import pytest
import sys
import os

# Ensure the repo root is on the path so `src.*` imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =====================================================================
# 1. Agent core (src/agent.py)
# =====================================================================

from src.agent import AgentConfig, TreasuryStatus, AutoFundAgent


class TestAgentConfig:
    """Test AgentConfig dataclass defaults and construction."""

    def test_defaults(self):
        cfg = AgentConfig()
        assert cfg.rpc_url == "https://sepolia.base.org"
        assert cfg.chain_id == 84532
        assert cfg.private_key == ""
        assert cfg.bankr_api_key == ""

    def test_custom_values(self):
        cfg = AgentConfig(rpc_url="http://localhost:8545", chain_id=1337, private_key="0xabc")
        assert cfg.rpc_url == "http://localhost:8545"
        assert cfg.chain_id == 1337
        assert cfg.private_key == "0xabc"

    def test_erc8004_identity_default(self):
        cfg = AgentConfig()
        identity = cfg.erc8004_identity
        assert identity["standard"] == "ERC-8004"
        assert identity["chain"] == "Base Sepolia"
        assert identity["chain_id"] == 84532
        assert identity["agent_id"] == "autofund-agent-v1"


class TestTreasuryStatus:
    """Test TreasuryStatus dataclass defaults."""

    def test_defaults(self):
        status = TreasuryStatus()
        assert status.principal == 0.0
        assert status.available_yield == 0.0
        assert status.total_spent == 0.0
        assert status.daily_remaining == 0.0
        assert status.last_updated == ""

    def test_custom_values(self):
        status = TreasuryStatus(principal=1000.0, available_yield=50.0, daily_remaining=400.0)
        assert status.principal == 1000.0
        assert status.available_yield == 50.0
        assert status.daily_remaining == 400.0


class TestAutoFundAgent:
    """Test AutoFundAgent pure-logic methods (no network calls)."""

    @pytest.fixture
    def agent(self):
        cfg = AgentConfig()
        return AutoFundAgent(cfg)

    def test_initial_state(self, agent):
        assert agent.inference_count == 0
        assert agent.total_inference_cost == 0.0
        assert agent.services_provided == 0
        assert agent.revenue_earned == 0.0
        assert agent.activity_log == []

    def test_estimate_cost_sonnet(self, agent):
        prompt = "a" * 400  # ~100 tokens
        response = "b" * 400  # ~100 tokens
        cost = agent._estimate_cost(prompt, response, "claude-sonnet-4-6")
        assert cost > 0
        # input: 100 tokens * 3.0/1M = 0.0003
        # output: 100 tokens * 15.0/1M = 0.0015
        assert pytest.approx(cost, rel=0.01) == 0.0018

    def test_estimate_cost_opus_more_expensive(self, agent):
        prompt = "x" * 200
        response = "y" * 200
        cost_sonnet = agent._estimate_cost(prompt, response, "claude-sonnet-4-6")
        cost_opus = agent._estimate_cost(prompt, response, "claude-opus-4-6")
        assert cost_opus > cost_sonnet

    def test_estimate_cost_unknown_model_uses_sonnet_rates(self, agent):
        cost_unknown = agent._estimate_cost("hello", "world", "unknown-model-99")
        cost_sonnet = agent._estimate_cost("hello", "world", "claude-sonnet-4-6")
        assert cost_unknown == cost_sonnet

    def test_simulate_response_returns_string(self, agent):
        response = agent._simulate_response("Analyze ETH price")
        assert isinstance(response, str)
        assert len(response) > 20

    def test_simulate_response_includes_prompt_prefix(self, agent):
        response = agent._simulate_response("Check BTC volatility")
        assert "Check BTC volatility" in response

    def test_log_activity(self, agent):
        agent.log_activity("test_action", {"key": "value"})
        assert len(agent.activity_log) == 1
        entry = agent.activity_log[0]
        assert entry["action"] == "test_action"
        assert entry["details"]["key"] == "value"
        assert "timestamp" in entry

    def test_export_activity_log_json(self, agent):
        agent.log_activity("a1", {"x": 1})
        agent.log_activity("a2", {"y": 2})
        import json
        exported = agent.export_activity_log()
        parsed = json.loads(exported)
        assert len(parsed) == 2


# =====================================================================
# 2. Uniswap Trader (src/uniswap_trader.py)
# =====================================================================

from src.uniswap_trader import (
    UniswapTrader, TradingSignal, TradingStrategy, TradeRecord,
    BASE_TOKENS, BASE_SEPOLIA_TOKENS, ETH_SEPOLIA_TOKENS,
    UNISWAP_ROUTERS,
)


class TestTradingSignal:
    """Test TradingSignal dataclass."""

    def test_creation(self):
        sig = TradingSignal(
            direction="BUY", confidence=0.85, position_size_pct=8.5,
            momentum=2.3, volatility=1.1, reasons=["bullish crossover"]
        )
        assert sig.direction == "BUY"
        assert sig.confidence == 0.85
        assert sig.position_size_pct == 8.5
        assert sig.reasons == ["bullish crossover"]

    def test_default_reasons_empty(self):
        sig = TradingSignal(direction="HOLD", confidence=0.0,
                            position_size_pct=0.0, momentum=0.0, volatility=0.0)
        assert sig.reasons == []


class TestTradingStrategy:
    """Test TradingStrategy defaults."""

    def test_defaults(self):
        strat = TradingStrategy()
        assert strat.name == "AutoFund Adaptive Momentum"
        assert strat.kelly_fraction == 0.25
        assert strat.max_position_pct == 20.0
        assert strat.min_position_pct == 2.0
        assert strat.stop_loss_pct == 5.0
        assert strat.take_profit_pct == 10.0
        assert strat.max_daily_trades == 10

    def test_momentum_thresholds(self):
        strat = TradingStrategy()
        assert strat.momentum_buy_threshold == 1.5
        assert strat.momentum_sell_threshold == -2.0


class TestUniswapTrader:
    """Test UniswapTrader pure-logic methods (no network calls)."""

    @pytest.fixture
    def trader(self):
        return UniswapTrader(api_key="", chain_id=84532)

    def test_initial_portfolio(self, trader):
        assert trader.portfolio["ETH"] == 10.0
        assert trader.portfolio["USDC"] == 5000.0

    def test_simulate_swap_buy(self, trader):
        trade = trader.simulate_swap("ETH/USDC", "BUY", 1000.0)
        assert trade.side == "BUY"
        assert trade.token_in == "USDC"
        assert trade.token_out == "ETH"
        assert trade.amount_in == 1000.0
        assert trade.amount_out > 0
        assert trade.status == "simulated"
        # Portfolio should be updated
        assert trader.portfolio["USDC"] < 5000.0
        assert trader.portfolio["ETH"] > 10.0

    def test_simulate_swap_sell(self, trader):
        trade = trader.simulate_swap("ETH/USDC", "SELL", 1.0)
        assert trade.side == "SELL"
        assert trade.token_in == "ETH"
        assert trade.token_out == "USDC"
        assert trade.amount_in == 1.0
        assert trade.amount_out > 3000  # ETH price ~ 3500
        assert trader.portfolio["ETH"] < 10.0

    def test_simulate_swap_slippage_applied(self, trader):
        trade = trader.simulate_swap("ETH/USDC", "SELL", 1.0)
        # Without slippage: 1 ETH = 3500 USDC. With 0.3% slippage: 3489.5
        expected = 3500.0 * (1 - 0.003)
        assert pytest.approx(trade.amount_out, rel=0.001) == expected

    def test_calculate_signals_insufficient_history(self, trader):
        """With only 1 data point, should return HOLD."""
        signal = trader.calculate_signals(3500.0)
        # First call = only 1 price recorded => n < 2 check inside may still pass
        # because _record_price is called first. Let's check.
        # After first call, price_history has 1 entry => n=1 => "Insufficient price history"
        assert signal.direction == "HOLD"
        assert signal.confidence == 0.0

    def test_calculate_signals_bullish_momentum(self, trader):
        """Feed rising prices to trigger a BUY signal."""
        prices = [3000, 3010, 3020, 3040, 3060, 3080, 3100]
        for p in prices:
            signal = trader.calculate_signals(float(p))
        # Short-term momentum should be positive
        assert signal.momentum > 0
        assert signal.direction in ("BUY", "HOLD")

    def test_calculate_signals_bearish_momentum(self, trader):
        """Feed falling prices to trigger a SELL signal."""
        prices = [4000, 3980, 3950, 3910, 3860, 3800, 3720]
        for p in prices:
            signal = trader.calculate_signals(float(p))
        assert signal.momentum < 0
        assert signal.direction in ("SELL", "HOLD")

    def test_calculate_signals_position_sizing_clamped(self, trader):
        """Position size must stay within min/max bounds."""
        # Create enough history with a clear trend
        for p in [3000, 3050, 3100, 3150, 3200, 3250, 3300, 3400, 3500, 3600]:
            signal = trader.calculate_signals(float(p))
        if signal.direction != "HOLD":
            assert signal.position_size_pct >= trader.strategy.min_position_pct
            assert signal.position_size_pct <= trader.strategy.max_position_pct

    def test_get_pnl_initial(self, trader):
        pnl = trader.get_pnl()
        assert pnl["total_trades"] == 0
        assert pnl["initial_value"] == trader.initial_portfolio_value

    def test_get_pnl_after_trade(self, trader):
        trader.simulate_swap("ETH/USDC", "SELL", 1.0)
        pnl = trader.get_pnl()
        assert pnl["total_trades"] == 1
        # After selling 1 ETH with slippage, total value is slightly lower
        assert pnl["current_value"] < trader.initial_portfolio_value

    def test_trade_history(self, trader):
        trader.simulate_swap("ETH/USDC", "BUY", 500.0)
        trader.simulate_swap("ETH/USDC", "SELL", 0.5)
        history = trader.get_trade_history()
        assert len(history) == 2
        assert history[0]["side"] == "BUY"
        assert history[1]["side"] == "SELL"

    def test_token_constants(self):
        assert "ETH" in BASE_TOKENS
        assert "WETH" in BASE_TOKENS
        assert "USDC" in BASE_TOKENS
        assert "USDC" in BASE_SEPOLIA_TOKENS
        assert "WETH" in ETH_SEPOLIA_TOKENS

    def test_router_addresses(self):
        assert 84532 in UNISWAP_ROUTERS   # Base Sepolia
        assert 8453 in UNISWAP_ROUTERS     # Base Mainnet
        assert 11155111 in UNISWAP_ROUTERS  # Ethereum Sepolia

    def test_price_history_capped(self, trader):
        """Price history should not grow beyond 500 entries."""
        for i in range(600):
            trader._record_price(3000.0 + i)
        assert len(trader.price_history) <= 500


# =====================================================================
# 3. Bankr Integration (src/bankr_integration.py)
# =====================================================================

from src.bankr_integration import BankrGateway, InferenceRecord


class TestInferenceRecord:
    """Test InferenceRecord dataclass."""

    def test_creation(self):
        rec = InferenceRecord(
            timestamp="2026-03-23T00:00:00",
            model="claude-sonnet-4-6",
            prompt_tokens=100,
            completion_tokens=200,
            cost_usd=0.005,
            funding_source="yield",
            purpose="market_analysis",
        )
        assert rec.model == "claude-sonnet-4-6"
        assert rec.cost_usd == 0.005
        assert rec.funding_source == "yield"


class TestBankrGateway:
    """Test BankrGateway pure logic (no API calls)."""

    @pytest.fixture
    def gw(self):
        return BankrGateway(api_key="")

    def test_initial_state(self, gw):
        assert gw.total_cost == 0.0
        assert gw.total_inferences == 0
        assert gw.budget_remaining == 100.0
        assert gw.inference_history == []

    def test_estimate_cost_positive(self, gw):
        cost = gw._estimate_cost("Analyze ETH price", 256, "claude-sonnet-4-6")
        assert cost > 0

    def test_estimate_cost_cheaper_model_costs_less(self, gw):
        prompt = "Tell me about Bitcoin"
        cost_flash = gw._estimate_cost(prompt, 256, "gemini-2.0-flash")
        cost_opus = gw._estimate_cost(prompt, 256, "claude-opus-4-6")
        assert cost_flash < cost_opus

    def test_calculate_cost(self, gw):
        cost = gw._calculate_cost(100, 200, "claude-sonnet-4-6")
        # input: 100 * 3e-6 = 0.0003, output: 200 * 15e-6 = 0.003
        assert pytest.approx(cost, rel=0.01) == 0.0033

    def test_select_optimal_model_simple(self, gw):
        assert gw.select_optimal_model("simple") == "gemini-2.0-flash"

    def test_select_optimal_model_moderate(self, gw):
        assert gw.select_optimal_model("moderate") == "gpt-4o-mini"

    def test_select_optimal_model_complex(self, gw):
        assert gw.select_optimal_model("complex") == "claude-sonnet-4-6"

    def test_select_optimal_model_critical(self, gw):
        assert gw.select_optimal_model("critical") == "claude-opus-4-6"

    def test_select_optimal_model_unknown_defaults_to_sonnet(self, gw):
        assert gw.select_optimal_model("unknown") == "claude-sonnet-4-6"

    def test_simulate_response_market_analysis(self, gw):
        resp = gw._simulate_response("ETH analysis", "claude-sonnet-4-6", "market_analysis")
        assert "ETH" in resp or "bullish" in resp.lower() or "RSI" in resp
        assert len(resp) > 50

    def test_simulate_response_portfolio_review(self, gw):
        resp = gw._simulate_response("Review my positions", "gpt-4o-mini", "portfolio_review")
        assert "portfolio" in resp.lower() or "allocation" in resp.lower()

    def test_simulate_response_general(self, gw):
        resp = gw._simulate_response("Test prompt here", "claude-sonnet-4-6", "general")
        assert "Test prompt here" in resp

    def test_chat_simulation_fallback(self, gw):
        """With no API key, chat() should fall back to simulation."""
        result = gw.chat("What is ETH price?", purpose="general")
        assert "response" in result
        assert result["api_source"] == "simulation"
        assert result["cost"] > 0
        assert gw.total_inferences == 1
        assert gw.budget_remaining < 100.0

    def test_chat_budget_deducted(self, gw):
        gw.chat("prompt 1", purpose="general")
        gw.chat("prompt 2", purpose="general")
        assert gw.total_inferences == 2
        assert gw.total_cost > 0
        assert gw.budget_remaining < 100.0

    def test_chat_budget_exhausted_rejected(self, gw):
        gw.budget_remaining = 0.0000001  # Almost nothing
        result = gw.chat("x" * 10000, max_tokens=4096, purpose="general")
        assert "error" in result
        assert "Insufficient budget" in result["error"]

    def test_model_costs_dict_has_expected_models(self, gw):
        expected = ["claude-sonnet-4-6", "claude-haiku-4-5", "claude-opus-4-6",
                     "gpt-4o", "gpt-4o-mini", "gemini-2.0-flash"]
        for model in expected:
            assert model in gw.MODEL_COSTS
            assert "input" in gw.MODEL_COSTS[model]
            assert "output" in gw.MODEL_COSTS[model]


# =====================================================================
# 4. Self-Check (src/self_check.py)
# =====================================================================

from src.self_check import CycleVerdict


class TestCycleVerdict:
    """Test CycleVerdict dataclass and summary method."""

    def test_creation(self):
        v = CycleVerdict(
            cycle=1,
            timestamp="2026-03-23T00:00:00",
            passed=True,
            treasury_ok=True,
            yield_positive=True,
            net_sustainable=True,
            no_critical_alerts=True,
            inference_budget_ok=True,
            checks_run=6,
            checks_passed=6,
        )
        assert v.passed is True
        assert v.checks_run == 6
        assert v.checks_passed == 6

    def test_summary_pass(self):
        v = CycleVerdict(
            cycle=3, timestamp="t", passed=True,
            treasury_ok=True, yield_positive=True,
            net_sustainable=True, no_critical_alerts=True,
            inference_budget_ok=True, checks_run=6, checks_passed=6,
            details=["All checks OK"], recommendations=[],
        )
        summary = v.summary()
        assert "PASS" in summary
        assert "6/6" in summary

    def test_summary_fail(self):
        v = CycleVerdict(
            cycle=2, timestamp="t", passed=False,
            treasury_ok=False, yield_positive=True,
            net_sustainable=False, no_critical_alerts=True,
            inference_budget_ok=True, checks_run=6, checks_passed=4,
            details=["Treasury problem"], recommendations=["Fix it"],
        )
        summary = v.summary()
        assert "FAIL" in summary
        assert "4/6" in summary
        assert "Recommendations" in summary


# =====================================================================
# 5. Celo Integration (src/celo_integration.py)
# =====================================================================

from src.celo_integration import (
    CeloAgent, CELO_STABLECOINS, FEE_CURRENCIES,
    CELO_CHAINS, CELO_CONTRACTS, RemittanceQuote, CeloStablecoinBalance,
)


class TestCeloConstants:
    """Test Celo configuration constants."""

    def test_stablecoins_have_required_fields(self):
        for symbol, info in CELO_STABLECOINS.items():
            assert "mainnet" in info, f"{symbol} missing mainnet address"
            assert "alfajores" in info, f"{symbol} missing alfajores address"
            assert "decimals" in info, f"{symbol} missing decimals"
            assert "name" in info, f"{symbol} missing name"

    def test_cusd_decimals(self):
        assert CELO_STABLECOINS["cUSD"]["decimals"] == 18

    def test_usdc_decimals(self):
        assert CELO_STABLECOINS["USDC"]["decimals"] == 6

    def test_fee_currencies_have_cusd(self):
        assert "cUSD" in FEE_CURRENCIES
        assert "cEUR" in FEE_CURRENCIES
        assert "USDC" in FEE_CURRENCIES

    def test_celo_chains_configured(self):
        assert "mainnet" in CELO_CHAINS
        assert "alfajores" in CELO_CHAINS
        assert CELO_CHAINS["mainnet"]["chain_id"] == 42220

    def test_celo_contracts_deployed(self):
        assert "TreasuryVault" in CELO_CONTRACTS
        assert "ServiceRegistry" in CELO_CONTRACTS
        assert CELO_CONTRACTS["TreasuryVault"].startswith("0x")


class TestRemittanceQuote:
    """Test RemittanceQuote dataclass."""

    def test_creation(self):
        q = RemittanceQuote(
            from_currency="cUSD", to_currency="cEUR",
            from_amount=100.0, to_amount=92.5,
            exchange_rate=0.925, fee_usd=0.25,
            estimated_time="< 5 seconds", tx_cost_usd=0.001,
        )
        assert q.from_currency == "cUSD"
        assert q.to_currency == "cEUR"
        assert q.to_amount == 92.5
        assert q.fee_usd == 0.25


class TestCeloAgent:
    """Test CeloAgent pure logic (no network calls)."""

    @pytest.fixture
    def agent(self):
        return CeloAgent(network="alfajores", private_key="")

    def test_initialization(self, agent):
        assert agent.network == "alfajores"
        assert agent.chain_id == 44787
        assert agent.operations_log == []

    def test_quote_remittance_cusd_to_ceur(self, agent):
        quote = agent.quote_remittance("cUSD", "cEUR", 100.0)
        assert isinstance(quote, RemittanceQuote)
        assert quote.from_currency == "cUSD"
        assert quote.to_currency == "cEUR"
        assert quote.from_amount == 100.0
        # cUSD=1.0, cEUR=1.08 => rate = 1.0/1.08 ~ 0.926
        assert 0.8 < quote.exchange_rate < 1.2
        assert quote.to_amount > 0
        assert quote.fee_usd > 0
        assert quote.tx_cost_usd == 0.001

    def test_quote_remittance_fee_proportional(self, agent):
        q100 = agent.quote_remittance("cUSD", "cEUR", 100.0)
        q200 = agent.quote_remittance("cUSD", "cEUR", 200.0)
        # Fee should roughly double when amount doubles (0.25% of amount)
        assert pytest.approx(q200.fee_usd, rel=0.05) == q100.fee_usd * 2

    def test_get_capabilities_summary(self, agent):
        caps = agent.get_capabilities_summary()
        assert caps["agent"] == "AutoFund CeloAgent"
        assert caps["network"] == "alfajores"
        assert len(caps["capabilities"]) >= 5
        # Check for Celo-unique features
        unique_caps = [c for c in caps["capabilities"] if c.get("celo_unique")]
        assert len(unique_caps) >= 2  # fee abstraction & MiniPay at minimum

    def test_log_operation(self, agent):
        agent._log("test_op", {"foo": "bar"})
        assert len(agent.operations_log) == 1
        assert agent.operations_log[0]["operation"] == "test_op"
        assert agent.operations_log[0]["network"] == "alfajores"
