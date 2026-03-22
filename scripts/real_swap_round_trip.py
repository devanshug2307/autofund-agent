"""
Real Uniswap V3 Round-Trip Swap Demo
======================================
Executes a second ETH->USDC swap on Ethereum Sepolia to demonstrate
the integrated execute_real_swap method in UniswapTrader.
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.uniswap_trader import UniswapTrader

PRIVATE_KEY = "b5d82d77b0ba619e3bec08dfeb5bde6b55fe5b93e2b4b25dfb07c3e925b13d69"


def main():
    print("=" * 60)
    print("AUTOFUND REAL SWAP EXECUTION")
    print("Using integrated UniswapTrader.execute_real_swap()")
    print("=" * 60)

    # Use Ethereum Sepolia (chainId 11155111) where Uniswap V3 pools have liquidity
    trader = UniswapTrader(
        api_key=os.getenv("UNISWAP_API_KEY", "Aw0yGu90YrmRs5dYOwdYeHpDH8gvpsuKgBZXWAi9OlE"),
        chain_id=11155111
    )

    # Step 1: Get a quote first via the Uniswap Trading API
    print("\n[1] Getting Uniswap API quote...")
    quote = trader.get_real_quote("ETH", "USDC", 0.0003)
    print(f"    Quote: {json.dumps(quote, indent=2, default=str)[:300]}")

    # Step 2: Execute a real on-chain swap
    print("\n[2] Executing REAL on-chain swap: 0.0003 ETH -> USDC")
    result = trader.execute_real_swap(
        token_in_symbol="ETH",
        token_out_symbol="USDC",
        amount=0.0003,
        private_key=PRIVATE_KEY,
        pool_fee=10000  # 1% fee tier
    )

    print(f"\n    Result:")
    for k, v in result.items():
        print(f"      {k}: {v}")

    if result.get("status") == "success":
        print(f"\n    SWAP CONFIRMED ON-CHAIN!")
        print(f"    TX: {result['tx_hash']}")
        print(f"    {result['amount_in']} ETH -> {result['amount_out']} USDC")
        print(f"    Explorer: {result['explorer_url']}")

    # Step 3: Show trade history
    print("\n[3] Trade History:")
    for t in trader.get_trade_history():
        print(f"    {t['side']} {t['in']} -> {t['out']} | Status: {t['status']}")

    # Save all swap proofs
    all_swaps = {
        "swap_1_initial": {
            "tx_hash": "0x42308f246ad675aacbf2ea42b6bf2f29c6972e3242f5e398c6b7c61efd661bb7",
            "network": "ethereum_sepolia",
            "chain_id": 11155111,
            "swap": "0.0005 ETH -> 2.773624 USDC",
            "router": "0x3bFA4769FB09eefC5a80d6E87c3B9C650f7Ae48E",
            "explorer": "https://sepolia.etherscan.io/tx/0x42308f246ad675aacbf2ea42b6bf2f29c6972e3242f5e398c6b7c61efd661bb7",
            "status": "SUCCESS"
        },
        "swap_2_integrated": result
    }

    with open("swap_proof.json", "w") as f:
        json.dump(all_swaps, f, indent=2)
    print("\n    All swap proofs saved to swap_proof.json")

    print("\n" + "=" * 60)
    print("DONE - Real Uniswap swaps executed on Ethereum Sepolia")
    print("=" * 60)


if __name__ == "__main__":
    main()
