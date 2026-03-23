"""
Real Uniswap V3 Swap on Ethereum Sepolia
==========================================
Executes a REAL swap of ETH -> USDC via Uniswap V3 SwapRouter02 on Sepolia testnet.
This produces a real on-chain transaction hash.

Uses: 0.0005 ETH -> USDC via the WETH/USDC 1% fee pool
"""

import json
import os
import time
import sys
from web3 import Web3

# ============ CONFIG ============
SEPOLIA_RPC = "https://ethereum-sepolia-rpc.publicnode.com"
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
if not PRIVATE_KEY:
    print("ERROR: PRIVATE_KEY environment variable not set")
    sys.exit(1)
WALLET = "0x54eeFbb7b3F701eEFb7fa99473A60A6bf5fE16D7"

# Uniswap V3 SwapRouter02 on Sepolia
SWAP_ROUTER_02 = "0x3bFA4769FB09eefC5a80d6E87c3B9C650f7Ae48E"

# Token addresses on Sepolia
WETH_SEPOLIA = "0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14"
USDC_SEPOLIA = "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"

# Swap parameters
SWAP_AMOUNT_ETH = 0.0005  # 0.0005 ETH (very small, safe amount)
POOL_FEE = 10000  # 1% fee tier (matching the pool found by Uniswap API)
SLIPPAGE = 0.50  # 50% slippage tolerance for testnet (low liquidity)

# SwapRouter02 ABI - exactInputSingle function
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
        "inputs": [{"name": "deadline", "type": "uint256"}],
        "name": "multicall",
        "outputs": [{"name": "", "type": "bytes[]"}],
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
    },
    {
        "inputs": [
            {"name": "minAmount", "type": "uint256"},
            {"name": "recipient", "type": "address"}
        ],
        "name": "unwrapWETH9",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "refundETH",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]""")


def main():
    print("=" * 60)
    print("REAL UNISWAP V3 SWAP ON ETHEREUM SEPOLIA")
    print("=" * 60)

    # Connect to Sepolia
    w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC))
    if not w3.is_connected():
        print("ERROR: Cannot connect to Sepolia RPC")
        sys.exit(1)

    chain_id = w3.eth.chain_id
    print(f"\nConnected to chain: {chain_id} (Sepolia)")

    # Check balance
    balance = w3.eth.get_balance(WALLET)
    balance_eth = w3.from_wei(balance, 'ether')
    print(f"Wallet: {WALLET}")
    print(f"Balance: {balance_eth} ETH")

    swap_amount_wei = w3.to_wei(SWAP_AMOUNT_ETH, 'ether')
    print(f"\nSwap: {SWAP_AMOUNT_ETH} ETH -> USDC")
    print(f"Pool: WETH/USDC (fee: {POOL_FEE / 10000}%)")
    print(f"Router: {SWAP_ROUTER_02}")

    if balance < swap_amount_wei + w3.to_wei(0.001, 'ether'):
        print(f"WARNING: Low balance. Need ~0.0015 ETH (swap + gas), have {balance_eth}")

    # Build the swap contract call
    router = w3.eth.contract(
        address=Web3.to_checksum_address(SWAP_ROUTER_02),
        abi=SWAP_ROUTER_ABI
    )

    # Calculate minimum output with slippage
    # From the Uniswap API quote: 0.0005 ETH ~ 2.77 USDC
    # Set minimum to essentially 0 for testnet (liquidity can be weird)
    amount_out_minimum = 0  # Accept any amount on testnet

    # Deadline: 20 minutes from now
    deadline = int(time.time()) + 1200

    # Build exactInputSingle params
    swap_params = (
        Web3.to_checksum_address(WETH_SEPOLIA),   # tokenIn (WETH - router wraps ETH)
        Web3.to_checksum_address(USDC_SEPOLIA),    # tokenOut (USDC)
        POOL_FEE,                                   # fee tier
        Web3.to_checksum_address(WALLET),           # recipient
        swap_amount_wei,                            # amountIn
        amount_out_minimum,                         # amountOutMinimum
        0                                           # sqrtPriceLimitX96 (0 = no limit)
    )

    # Encode the exactInputSingle call
    swap_calldata = router.encode_abi("exactInputSingle", [swap_params])

    # Use multicall with deadline
    multicall_data = router.encode_abi("multicall", [deadline, [swap_calldata]])

    # Get nonce and gas price
    nonce = w3.eth.get_transaction_count(WALLET)
    gas_price = w3.eth.gas_price

    print(f"\nNonce: {nonce}")
    print(f"Gas price: {w3.from_wei(gas_price, 'gwei')} gwei")

    # Build transaction
    tx = {
        'to': Web3.to_checksum_address(SWAP_ROUTER_02),
        'value': swap_amount_wei,  # Send ETH (router wraps to WETH)
        'data': multicall_data,
        'nonce': nonce,
        'gas': 350000,  # Generous gas limit for swap
        'gasPrice': gas_price + w3.to_wei(1, 'gwei'),  # Slight priority
        'chainId': chain_id,
    }

    # Estimate gas
    try:
        gas_est = w3.eth.estimate_gas(tx)
        tx['gas'] = int(gas_est * 1.3)  # 30% buffer
        print(f"Gas estimate: {gas_est} (using {tx['gas']})")
    except Exception as e:
        print(f"Gas estimation failed: {e}")
        print("Using default gas limit of 350000")

    total_cost = swap_amount_wei + (tx['gas'] * tx['gasPrice'])
    print(f"Total cost: {w3.from_wei(total_cost, 'ether')} ETH")

    if balance < total_cost:
        print(f"ERROR: Insufficient balance. Need {w3.from_wei(total_cost, 'ether')} ETH, have {balance_eth} ETH")
        sys.exit(1)

    # Sign and send
    print("\nSigning transaction...")
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

    print("Broadcasting transaction...")
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    tx_hash_hex = tx_hash.hex()
    print(f"\nTransaction sent!")
    print(f"TX Hash: 0x{tx_hash_hex}")
    print(f"Explorer: https://sepolia.etherscan.io/tx/0x{tx_hash_hex}")

    # Wait for confirmation
    print("\nWaiting for confirmation...")
    try:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        print(f"\nTransaction confirmed!")
        print(f"Status: {'SUCCESS' if receipt['status'] == 1 else 'FAILED'}")
        print(f"Block: {receipt['blockNumber']}")
        print(f"Gas used: {receipt['gasUsed']}")
        print(f"Gas cost: {w3.from_wei(receipt['gasUsed'] * receipt['effectiveGasPrice'], 'ether')} ETH")

        if receipt['status'] == 1:
            print("\n" + "=" * 60)
            print("SWAP SUCCESSFUL!")
            print(f"TX Hash: 0x{tx_hash_hex}")
            print(f"Swapped {SWAP_AMOUNT_ETH} ETH -> USDC on Sepolia")
            print(f"Explorer: https://sepolia.etherscan.io/tx/0x{tx_hash_hex}")
            print("=" * 60)

            # Save proof
            proof = {
                "type": "uniswap_v3_swap",
                "network": "ethereum_sepolia",
                "chain_id": 11155111,
                "tx_hash": f"0x{tx_hash_hex}",
                "block_number": receipt['blockNumber'],
                "swap": {
                    "token_in": "ETH (wrapped to WETH)",
                    "token_out": "USDC",
                    "amount_in_eth": SWAP_AMOUNT_ETH,
                    "router": SWAP_ROUTER_02,
                    "pool_fee": f"{POOL_FEE / 10000}%",
                    "pool_address": "0x6418EEC70f50913ff0d756B48d32Ce7C02b47C47"
                },
                "gas_used": receipt['gasUsed'],
                "explorer_url": f"https://sepolia.etherscan.io/tx/0x{tx_hash_hex}",
                "status": "SUCCESS",
                "wallet": WALLET
            }
            with open("swap_proof.json", "w") as f:
                json.dump(proof, f, indent=2)
            print("\nProof saved to swap_proof.json")
        else:
            print("\nSwap transaction REVERTED on chain.")
            print("This might be due to pool liquidity issues on testnet.")

    except Exception as e:
        print(f"\nError waiting for receipt: {e}")
        print(f"TX may still confirm. Check: https://sepolia.etherscan.io/tx/0x{tx_hash_hex}")

    return tx_hash_hex


if __name__ == "__main__":
    main()
