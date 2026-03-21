"""
AutoFund Service API — Discoverable HTTP Service
==================================================
A FastAPI application that exposes the AutoFund agent's portfolio analysis,
vault monitoring, and Lido tools as a discoverable HTTP service on Base.

Any client (human, agent, or contract) can discover and call these endpoints
to receive paid financial analysis powered by self-funded LLM inference.

Usage:
    uvicorn src.service_api:app --host 0.0.0.0 --port 8000
    # or
    python3 -m src.service_api  # runs on port 8000

Built for The Synthesis Hackathon — Base Services Bounty ($5,000)
"""

import os
import json
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.agent import AutoFundAgent, AgentConfig
from src.mcp_server import LidoMCPServer
from src.monitor import VaultMonitor
from src.uniswap_trader import UniswapTrader

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AutoFund Service API",
    description=(
        "Discoverable HTTP API for the AutoFund self-sustaining DeFi agent. "
        "Provides portfolio analysis, Lido vault monitoring, market data, "
        "and trading insights — all powered by yield-funded LLM inference."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Singleton service instances (lazy-init on first request)
# ---------------------------------------------------------------------------
_agent: AutoFundAgent | None = None
_lido: LidoMCPServer | None = None
_monitor: VaultMonitor | None = None
_trader: UniswapTrader | None = None


def _get_agent() -> AutoFundAgent:
    global _agent
    if _agent is None:
        config = AgentConfig(
            rpc_url=os.getenv("RPC_URL", "https://sepolia.base.org"),
            bankr_api_key=os.getenv("BANKR_API_KEY", ""),
        )
        _agent = AutoFundAgent(config)
    return _agent


def _get_lido() -> LidoMCPServer:
    global _lido
    if _lido is None:
        _lido = LidoMCPServer()
    return _lido


def _get_monitor() -> VaultMonitor:
    global _monitor
    if _monitor is None:
        _monitor = VaultMonitor()
    return _monitor


def _get_trader() -> UniswapTrader:
    global _trader
    if _trader is None:
        _trader = UniswapTrader(api_key=os.getenv("UNISWAP_API_KEY", ""))
    return _trader


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------
class PortfolioRequest(BaseModel):
    wallet_address: str = Field(
        ...,
        description="Ethereum wallet address to analyse",
        pattern=r"^0x[a-fA-F0-9]{40}$",
    )


class StakeRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount of ETH to stake")
    dry_run: bool = Field(True, description="Simulate without executing")


class ServiceInfo(BaseModel):
    name: str
    description: str
    endpoint: str
    method: str
    fee_usd: float


# ---------------------------------------------------------------------------
# Discovery Endpoint — required by Base Services bounty
# ---------------------------------------------------------------------------
@app.get("/", tags=["Discovery"])
async def root():
    """Service discovery root. Returns metadata about the agent and its capabilities."""
    return {
        "service": "AutoFund Agent",
        "version": "1.0.0",
        "chain": "Base Sepolia (84532)",
        "description": (
            "Self-sustaining DeFi agent offering portfolio analysis, "
            "Lido vault monitoring, and market intelligence as paid HTTP services."
        ),
        "docs": "/docs",
        "endpoints": [
            "/services",
            "/portfolio/analyze",
            "/vault/report",
            "/vault/alerts",
            "/lido/apy",
            "/lido/stake",
            "/lido/balance",
            "/lido/governance",
            "/market/price",
            "/market/quote",
            "/agent/status",
            "/health",
        ],
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/services", tags=["Discovery"])
async def list_services():
    """List all discoverable services with pricing and endpoints."""
    services = [
        ServiceInfo(
            name="Portfolio Analysis",
            description="AI-powered analysis of any Ethereum wallet's holdings, DeFi positions, and risk",
            endpoint="/portfolio/analyze",
            method="POST",
            fee_usd=1.00,
        ),
        ServiceInfo(
            name="Vault Monitoring Report",
            description="Plain-English Lido Earn vault position report with yield benchmarks",
            endpoint="/vault/report",
            method="GET",
            fee_usd=0.00,
        ),
        ServiceInfo(
            name="Vault Alerts",
            description="Check for yield drops, allocation shifts, and floor breaches",
            endpoint="/vault/alerts",
            method="GET",
            fee_usd=0.00,
        ),
        ServiceInfo(
            name="Lido APY",
            description="Current Lido stETH APY with benchmark comparisons",
            endpoint="/lido/apy",
            method="GET",
            fee_usd=0.00,
        ),
        ServiceInfo(
            name="Lido Stake (dry-run)",
            description="Simulate staking ETH into Lido and see expected stETH return",
            endpoint="/lido/stake",
            method="POST",
            fee_usd=0.00,
        ),
        ServiceInfo(
            name="Market Price",
            description="Real-time ETH/USD price from CoinGecko",
            endpoint="/market/price",
            method="GET",
            fee_usd=0.00,
        ),
        ServiceInfo(
            name="Market Quote",
            description="Real-time swap quote for token pairs via Uniswap / CoinGecko",
            endpoint="/market/quote",
            method="GET",
            fee_usd=0.00,
        ),
    ]
    return {"services": [s.model_dump() for s in services], "count": len(services)}


# ---------------------------------------------------------------------------
# Portfolio Analysis — the core paid service
# ---------------------------------------------------------------------------
@app.post("/portfolio/analyze", tags=["Services"])
async def analyze_portfolio(req: PortfolioRequest):
    """
    Analyse an Ethereum wallet's portfolio.

    Returns token holdings summary, DeFi positions, risk assessment,
    and optimisation recommendations. Powered by self-funded LLM inference.
    """
    agent = _get_agent()
    result = agent.provide_portfolio_analysis(req.wallet_address)
    return result


# ---------------------------------------------------------------------------
# Vault Monitoring
# ---------------------------------------------------------------------------
@app.get("/vault/report", tags=["Vault"])
async def vault_report():
    """Generate a full plain-English vault monitoring report."""
    monitor = _get_monitor()
    report = monitor.generate_report()
    return {"report": report, "timestamp": datetime.utcnow().isoformat()}


@app.get("/vault/alerts", tags=["Vault"])
async def vault_alerts():
    """Run monitoring checks and return any new alerts."""
    monitor = _get_monitor()
    alerts = monitor.run_checks()
    return {
        "alerts": [
            {
                "severity": a.severity,
                "title": a.title,
                "message": a.message,
                "action_required": a.action_required,
                "timestamp": a.timestamp,
            }
            for a in alerts
        ],
        "total_historical_alerts": len(monitor.alerts),
    }


# ---------------------------------------------------------------------------
# Lido Endpoints
# ---------------------------------------------------------------------------
@app.get("/lido/apy", tags=["Lido"])
async def lido_apy():
    """Get current Lido stETH APY with benchmark comparisons."""
    lido = _get_lido()
    return lido.get_apy()


@app.get("/lido/balance", tags=["Lido"])
async def lido_balance():
    """Query current stETH / wstETH balances."""
    lido = _get_lido()
    return lido.get_balance()


@app.post("/lido/stake", tags=["Lido"])
async def lido_stake(req: StakeRequest):
    """Stake ETH into Lido (defaults to dry-run mode)."""
    lido = _get_lido()
    return lido.stake_eth(req.amount, dry_run=req.dry_run)


@app.get("/lido/governance", tags=["Lido"])
async def lido_governance():
    """Query active Lido DAO governance proposals."""
    lido = _get_lido()
    return lido.get_governance_votes()


@app.get("/lido/monitor", tags=["Lido"])
async def lido_monitor():
    """Generate a plain-English Lido position monitoring report."""
    lido = _get_lido()
    report = lido.monitor_position()
    return {"report": report, "timestamp": datetime.utcnow().isoformat()}


# ---------------------------------------------------------------------------
# Market Data
# ---------------------------------------------------------------------------
@app.get("/market/price", tags=["Market"])
async def market_price():
    """Get real-time ETH/USD price."""
    trader = _get_trader()
    price = trader.get_real_price()
    return {
        "pair": "ETH/USD",
        "price": price,
        "source": "CoinGecko",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/market/quote", tags=["Market"])
async def market_quote(
    token_in: str = Query("ETH", description="Input token symbol"),
    token_out: str = Query("USDC", description="Output token symbol"),
    amount: float = Query(1.0, gt=0, description="Amount of input token"),
):
    """Get a real-time swap quote."""
    trader = _get_trader()
    quote = trader.get_real_quote(token_in, token_out, amount)
    return quote


# ---------------------------------------------------------------------------
# Agent Status
# ---------------------------------------------------------------------------
@app.get("/agent/status", tags=["Agent"])
async def agent_status():
    """Return the agent's self-sustainability metrics."""
    agent = _get_agent()
    net = agent.revenue_earned - agent.total_inference_cost
    return {
        "wallet": agent.account.address,
        "chain": "Base Sepolia (84532)",
        "inference_count": agent.inference_count,
        "total_inference_cost_usd": round(agent.total_inference_cost, 6),
        "services_provided": agent.services_provided,
        "revenue_earned_usd": round(agent.revenue_earned, 2),
        "net_position_usd": round(net, 6),
        "self_sustaining": net >= 0,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"])
async def health():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ---------------------------------------------------------------------------
# Run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    print(f"Starting AutoFund Service API on port {port}...")
    print(f"Docs at http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)
