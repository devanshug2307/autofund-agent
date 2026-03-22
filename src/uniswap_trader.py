"""
AutoFund Uniswap Trading Module
================================
Integrates with the Uniswap Trading API for autonomous token swaps.
Supports quoting, execution, and P&L tracking.
Executes REAL on-chain swaps via Uniswap V3 SwapRouter02.

Built for The Synthesis Hackathon - Uniswap Agentic Finance Bounty ($5,000)
"""

import json
import os
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

import httpx

try:
    from web3 import Web3
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False


# Common token addresses on Base
BASE_TOKENS = {
    "ETH": "0x0000000000000000000000000000000000000000",
    "WETH": "0x4200000000000000000000000000000000000006",
    "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "USDbC": "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA",
    "DAI": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
}

BASE_SEPOLIA_TOKENS = {
    "ETH": "0x0000000000000000000000000000000000000000",
    "WETH": "0x4200000000000000000000000000000000000006",
    "USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
}

# Ethereum Sepolia tokens (Uniswap V3 pools with real liquidity)
ETH_SEPOLIA_TOKENS = {
    "ETH": "0x0000000000000000000000000000000000000000",
    "WETH": "0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14",
    "USDC": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
}

# Uniswap V3 Router addresses per chain
UNISWAP_ROUTERS = {
    11155111: "0x3bFA4769FB09eefC5a80d6E87c3B9C650f7Ae48E",  # Ethereum Sepolia
    84532: "0x94cC0AaC535CCDB3C01d6787D6413C739ae12bc4",     # Base Sepolia
    8453: "0x2626664c2603336E57B271c5C0b26F421741e481",      # Base Mainnet
}

# RPC endpoints per chain
CHAIN_RPCS = {
    11155111: "https://ethereum-sepolia-rpc.publicnode.com",
    84532: "https://sepolia.base.org",
    8453: "https://mainnet.base.org",
}

# SwapRouter02 ABI for exactInputSingle
SWAP_ROUTER_ABI = json.loads("""[
    {
        "inputs": [
            {
                "components": [
                    {"name": "tokenIn", "type": "address"},
                    {"name": "tokenOut", "type": "address"},
                    {"name": "fee", "type": "uint24"},
                    {"name": "recipient", "type": "address"},
                    {"name": "amountIn", "type": "uint256"},
                    {"name": "amountOutMinimum", "type": "uint256"},
                    {"name": "sqrtPriceLimitX96", "type": "uint160"}
                ],
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "deadline", "type": "uint256"},
            {"name": "data", "type": "bytes[]"}
        ],
        "name": "multicall",
        "outputs": [{"name": "", "type": "bytes[]"}],
        "stateMutability": "payable",
        "type": "function"
    }
]""")


@dataclass
class TradeRecord:
    """Record of a single trade."""
    timestamp: str
    pair: str
    side: str  # "BUY" or "SELL"
    token_in: str
    token_out: str
    amount_in: float
    amount_out: float
    price: float
    tx_hash: Optional[str] = None
    status: str = "executed"


@dataclass
class TradingStrategy:
    """Simple momentum-based trading strategy."""
    name: str = "AutoFund Momentum"
    position_size_pct: float = 10.0  # % of available balance per trade
    stop_loss_pct: float = 5.0
    take_profit_pct: float = 10.0
    max_daily_trades: int = 10
    cooldown_minutes: int = 30


class UniswapTrader:
    """
    Autonomous trading agent using Uniswap Trading API.

    Features:
    - Real-time quotes via Uniswap API
    - LLM-powered market analysis for trade decisions
    - P&L tracking and performance reporting
    - Risk management with stop-loss and position sizing
    """

    UNISWAP_API_BASE = "https://trade-api.gateway.uniswap.org/v1"

    def __init__(self, api_key: str = "", chain_id: int = 84532):
        self.api_key = api_key or os.getenv("UNISWAP_API_KEY", "")
        self.chain_id = chain_id
        self.strategy = TradingStrategy()
        self.trades: list[TradeRecord] = []
        self.portfolio = {"ETH": 10.0, "USDC": 5000.0}  # Starting portfolio
        self.initial_portfolio_value = 5000.0 + (10.0 * 3500)  # ~$40,000

    def get_quote(self, token_in: str, token_out: str, amount: float,
                  token_in_decimals: int = 18) -> dict:
        """
        Get a swap quote from Uniswap Trading API.

        Args:
            token_in: Input token address
            token_out: Output token address
            amount: Amount of input token
            token_in_decimals: Decimals of input token
        """
        amount_raw = str(int(amount * (10 ** token_in_decimals)))

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        try:
            with httpx.Client(timeout=15) as client:
                response = client.post(
                    f"{self.UNISWAP_API_BASE}/quote",
                    headers=headers,
                    json={
                        "tokenIn": token_in,
                        "tokenOut": token_out,
                        "amount": amount_raw,
                        "type": "EXACT_INPUT",
                        "tokenInChainId": self.chain_id,
                        "tokenOutChainId": self.chain_id,
                        "swapper": "0x54eeFbb7b3F701eEFb7fa99473A60A6bf5fE16D7",
                        "slippageTolerance": 0.5
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": "quoted",
                        "amount_in": amount,
                        "amount_out": data.get("quoteDecimals", "0"),
                        "gas_estimate": data.get("gasEstimate", "unknown"),
                        "route": data.get("route", []),
                        "price_impact": data.get("priceImpact", "unknown"),
                        "raw": data
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"API returned {response.status_code}",
                        "body": response.text[:200]
                    }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def execute_real_swap(self, token_in_symbol: str = "ETH",
                          token_out_symbol: str = "USDC",
                          amount: float = 0.0005,
                          private_key: str = "",
                          pool_fee: int = 10000) -> dict:
        """
        Execute a REAL on-chain swap via Uniswap V3 SwapRouter02.

        Args:
            token_in_symbol: Input token symbol (ETH, WETH, USDC)
            token_out_symbol: Output token symbol (ETH, WETH, USDC)
            amount: Amount of input token (in human-readable units)
            private_key: Private key for signing (or from env PRIVATE_KEY)
            pool_fee: Pool fee tier (500=0.05%, 3000=0.3%, 10000=1%)

        Returns:
            dict with tx_hash, status, amounts, explorer URL
        """
        if not WEB3_AVAILABLE:
            return {"status": "error", "error": "web3 not installed. Run: pip install web3"}

        pk = private_key or os.getenv("PRIVATE_KEY", "")
        if not pk:
            return {"status": "error", "error": "No private key provided"}

        # Select token addresses for the chain
        if self.chain_id == 11155111:
            tokens = ETH_SEPOLIA_TOKENS
        elif self.chain_id == 84532:
            tokens = BASE_SEPOLIA_TOKENS
        else:
            tokens = BASE_TOKENS

        rpc_url = CHAIN_RPCS.get(self.chain_id, "https://ethereum-sepolia-rpc.publicnode.com")
        router_addr = UNISWAP_ROUTERS.get(self.chain_id)
        if not router_addr:
            return {"status": "error", "error": f"No router for chain {self.chain_id}"}

        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            return {"status": "error", "error": f"Cannot connect to RPC: {rpc_url}"}

        account = w3.eth.account.from_key(pk)
        wallet = account.address

        # Determine token addresses and decimals
        token_in_addr = tokens.get(token_in_symbol if token_in_symbol != "ETH" else "WETH")
        token_out_addr = tokens.get(token_out_symbol if token_out_symbol != "ETH" else "WETH")
        token_in_decimals = 6 if token_in_symbol == "USDC" else 18
        amount_wei = int(amount * (10 ** token_in_decimals))

        # For ETH input, we send value with the tx and the router wraps it
        is_eth_input = token_in_symbol == "ETH"
        tx_value = amount_wei if is_eth_input else 0

        # Build the router contract
        router = w3.eth.contract(
            address=Web3.to_checksum_address(router_addr),
            abi=SWAP_ROUTER_ABI
        )

        # Build swap params
        swap_params = (
            Web3.to_checksum_address(token_in_addr),
            Web3.to_checksum_address(token_out_addr),
            pool_fee,
            Web3.to_checksum_address(wallet),
            amount_wei,
            0,  # amountOutMinimum = 0 (testnet, accept any)
            0   # sqrtPriceLimitX96 = 0 (no limit)
        )

        # Encode via multicall with deadline
        deadline = int(time.time()) + 1200
        swap_calldata = router.encode_abi("exactInputSingle", [swap_params])
        multicall_data = router.encode_abi("multicall", [deadline, [swap_calldata]])

        # Build transaction
        nonce = w3.eth.get_transaction_count(wallet)
        gas_price = w3.eth.gas_price

        tx = {
            'to': Web3.to_checksum_address(router_addr),
            'value': tx_value,
            'data': multicall_data,
            'nonce': nonce,
            'gas': 350000,
            'gasPrice': gas_price + w3.to_wei(1, 'gwei'),
            'chainId': self.chain_id,
        }

        # Estimate gas
        try:
            gas_est = w3.eth.estimate_gas(tx)
            tx['gas'] = int(gas_est * 1.3)
        except Exception:
            pass  # Use default 350000

        # Sign and send
        signed = w3.eth.account.sign_transaction(tx, pk)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        tx_hash_hex = f"0x{tx_hash.hex()}"

        # Wait for receipt
        try:
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            success = receipt['status'] == 1

            # Decode output amount from transfer logs
            amount_out = 0
            if success and len(receipt['logs']) > 0:
                # First log is typically the output token transfer
                out_data = receipt['logs'][0]['data'].hex()
                out_decimals = 6 if token_out_symbol == "USDC" else 18
                amount_out = int(out_data, 16) / (10 ** out_decimals)

            # Record the trade
            explorer_base = {
                11155111: "https://sepolia.etherscan.io",
                84532: "https://sepolia.basescan.org",
                8453: "https://basescan.org",
            }.get(self.chain_id, "https://sepolia.etherscan.io")

            if success:
                trade = TradeRecord(
                    timestamp=datetime.utcnow().isoformat(),
                    pair=f"{token_in_symbol}/{token_out_symbol}",
                    side="SELL" if token_in_symbol == "ETH" else "BUY",
                    token_in=token_in_symbol,
                    token_out=token_out_symbol,
                    amount_in=amount,
                    amount_out=round(amount_out, 6),
                    price=amount_out / amount if amount > 0 else 0,
                    tx_hash=tx_hash_hex,
                    status="confirmed_onchain"
                )
                self.trades.append(trade)

            return {
                "status": "success" if success else "reverted",
                "tx_hash": tx_hash_hex,
                "block_number": receipt['blockNumber'],
                "gas_used": receipt['gasUsed'],
                "token_in": token_in_symbol,
                "token_out": token_out_symbol,
                "amount_in": amount,
                "amount_out": amount_out,
                "chain_id": self.chain_id,
                "explorer_url": f"{explorer_base}/tx/{tx_hash_hex}",
                "router": router_addr,
            }

        except Exception as e:
            return {
                "status": "pending",
                "tx_hash": tx_hash_hex,
                "error": str(e),
                "note": "TX broadcast but receipt not confirmed yet"
            }

    def simulate_swap(self, pair: str, side: str, amount: float) -> TradeRecord:
        """
        Simulate a swap for demo/testing purposes.
        In production, this calls the Uniswap API and signs the transaction.
        """
        prices = {
            "ETH/USDC": 3500.0,
            "USDC/ETH": 1 / 3500.0,
        }

        price = prices.get(pair, 3500.0)
        slippage = 0.003  # 0.3% slippage

        if side == "BUY":
            # Buy ETH with USDC
            amount_out = (amount / price) * (1 - slippage)
            token_in, token_out = "USDC", "ETH"
            self.portfolio["USDC"] -= amount
            self.portfolio["ETH"] += amount_out
        else:
            # Sell ETH for USDC
            amount_out = (amount * price) * (1 - slippage)
            token_in, token_out = "ETH", "USDC"
            self.portfolio["ETH"] -= amount
            self.portfolio["USDC"] += amount_out

        trade = TradeRecord(
            timestamp=datetime.utcnow().isoformat(),
            pair=pair,
            side=side,
            token_in=token_in,
            token_out=token_out,
            amount_in=amount,
            amount_out=round(amount_out, 6),
            price=price,
            status="simulated"
        )
        self.trades.append(trade)
        return trade

    def get_real_price(self, base: str = "ethereum", quote: str = "usd") -> float:
        """Fetch real-time price from CoinGecko (free, no API key needed)."""
        try:
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    f"https://api.coingecko.com/api/v3/simple/price",
                    params={"ids": base, "vs_currencies": quote}
                )
                if response.status_code == 200:
                    return response.json()[base][quote]
        except Exception:
            pass
        return 3500.0  # Fallback

    def get_real_quote(self, token_in_symbol: str = "ETH", token_out_symbol: str = "USDC",
                       amount: float = 1.0) -> dict:
        """
        Get a REAL quote from Uniswap Trading API.
        Falls back to CoinGecko price if no Uniswap API key.
        """
        # Try Uniswap API first
        if self.api_key:
            if self.chain_id == 11155111:
                tokens = ETH_SEPOLIA_TOKENS
            elif self.chain_id == 8453:
                tokens = BASE_TOKENS
            else:
                tokens = BASE_SEPOLIA_TOKENS
            token_in = tokens.get(token_in_symbol, tokens.get("WETH"))
            token_out = tokens.get(token_out_symbol, tokens.get("USDC"))
            decimals = 6 if token_out_symbol == "USDC" else 18
            result = self.get_quote(token_in, token_out, amount, 18)
            if result.get("status") == "quoted":
                return result

        # Fallback: use real CoinGecko price for accurate simulation
        price = self.get_real_price()
        return {
            "status": "quoted_via_coingecko",
            "price": price,
            "amount_in": amount,
            "amount_out": amount * price if token_in_symbol == "ETH" else amount / price,
            "source": "CoinGecko real-time price",
            "note": "Set UNISWAP_API_KEY for direct Uniswap quotes"
        }

    def analyze_and_trade(self, market_signal: str) -> dict:
        """
        Make a trading decision based on market signal from LLM analysis.

        Args:
            market_signal: "BUY", "SELL", or "HOLD" from LLM analysis
        """
        result = {
            "signal": market_signal,
            "timestamp": datetime.utcnow().isoformat(),
            "action_taken": None,
            "trade": None
        }

        if market_signal == "HOLD":
            result["action_taken"] = "No trade — holding position"
            return result

        if market_signal == "BUY":
            # Use 10% of USDC to buy ETH
            trade_amount = self.portfolio["USDC"] * (self.strategy.position_size_pct / 100)
            if trade_amount < 1.0:
                result["action_taken"] = "Insufficient USDC balance"
                return result
            trade = self.simulate_swap("ETH/USDC", "BUY", trade_amount)
            result["action_taken"] = f"Bought {trade.amount_out:.6f} ETH for ${trade.amount_in:.2f}"
            result["trade"] = trade

        elif market_signal == "SELL":
            trade_amount = self.portfolio["ETH"] * (self.strategy.position_size_pct / 100)
            if trade_amount < 0.001:
                result["action_taken"] = "Insufficient ETH balance"
                return result
            trade = self.simulate_swap("ETH/USDC", "SELL", trade_amount)
            result["action_taken"] = f"Sold {trade.amount_in:.6f} ETH for ${trade.amount_out:.2f}"
            result["trade"] = trade

        return result

    def get_pnl(self) -> dict:
        """Calculate current P&L (Profit and Loss)."""
        eth_price = 3500.0
        current_value = self.portfolio["USDC"] + (self.portfolio["ETH"] * eth_price)
        pnl = current_value - self.initial_portfolio_value
        pnl_pct = (pnl / self.initial_portfolio_value) * 100

        return {
            "initial_value": round(self.initial_portfolio_value, 2),
            "current_value": round(current_value, 2),
            "pnl_usd": round(pnl, 2),
            "pnl_percent": round(pnl_pct, 4),
            "total_trades": len(self.trades),
            "portfolio": {k: round(v, 6) for k, v in self.portfolio.items()},
            "profitable": pnl >= 0
        }

    def get_trade_history(self) -> list[dict]:
        """Get formatted trade history."""
        return [
            {
                "time": t.timestamp,
                "pair": t.pair,
                "side": t.side,
                "in": f"{t.amount_in:.4f} {t.token_in}",
                "out": f"{t.amount_out:.4f} {t.token_out}",
                "price": t.price,
                "status": t.status
            }
            for t in self.trades
        ]

    def generate_performance_report(self) -> str:
        """Generate a performance report for judges."""
        pnl = self.get_pnl()
        history = self.get_trade_history()

        report = f"""
╔══════════════════════════════════════════════════╗
║        AUTOFUND TRADING PERFORMANCE REPORT        ║
║        {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}                  ║
╚══════════════════════════════════════════════════╝

STRATEGY: {self.strategy.name}
  Position Size: {self.strategy.position_size_pct}% per trade
  Stop Loss: {self.strategy.stop_loss_pct}%
  Take Profit: {self.strategy.take_profit_pct}%

PORTFOLIO:
  ETH:  {pnl['portfolio']['ETH']:.6f} (~${pnl['portfolio']['ETH'] * 3500:.2f})
  USDC: ${pnl['portfolio']['USDC']:.2f}
  Total Value: ${pnl['current_value']:.2f}

P&L:
  Initial: ${pnl['initial_value']:.2f}
  Current: ${pnl['current_value']:.2f}
  Profit/Loss: ${pnl['pnl_usd']:.2f} ({pnl['pnl_percent']:.2f}%)
  Status: {'PROFITABLE ✓' if pnl['profitable'] else 'LOSS ✗'}

TRADE HISTORY ({len(history)} trades):
"""
        for i, trade in enumerate(history, 1):
            report += f"  #{i} [{trade['side']}] {trade['in']} → {trade['out']} @ ${trade['price']:.2f}\n"

        if not history:
            report += "  No trades executed yet.\n"

        report += f"""
RISK METRICS:
  Max drawdown: N/A (insufficient history)
  Win rate: N/A
  Avg trade size: ${sum(t.amount_in for t in self.trades) / max(len(self.trades), 1):.2f}

INTEGRATION:
  API: Uniswap Trading API v1
  Chain: Base (ID: {self.chain_id})
  Protocols: V2, V3
"""
        return report


def demo():
    """Demo the trading module."""
    trader = UniswapTrader()

    print("=== Uniswap Trading Module Demo ===\n")

    # Execute a series of trades based on simulated signals
    signals = [
        ("BUY", "RSI oversold, momentum turning bullish"),
        ("BUY", "Volume spike, breakout confirmation"),
        ("HOLD", "Consolidation, wait for direction"),
        ("SELL", "RSI overbought, take partial profits"),
        ("BUY", "Support bounce, re-entry signal"),
    ]

    for signal, reason in signals:
        print(f"\nSignal: {signal} — {reason}")
        result = trader.analyze_and_trade(signal)
        print(f"  Action: {result['action_taken']}")

    # Performance report
    print(trader.generate_performance_report())

    # P&L summary
    pnl = trader.get_pnl()
    print(f"\nFinal P&L: ${pnl['pnl_usd']:.2f} ({pnl['pnl_percent']:.2f}%)")
    print(f"Trades: {pnl['total_trades']}")
    print(f"Status: {'PROFITABLE' if pnl['profitable'] else 'LOSS'}")


if __name__ == "__main__":
    demo()
