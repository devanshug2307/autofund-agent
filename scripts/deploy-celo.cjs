/**
 * Deploy AutoFund contracts to Celo Sepolia testnet.
 * Demonstrates the agent running on Celo with stablecoin-native operations.
 *
 * Usage: npx hardhat --config hardhat.config.cjs run scripts/deploy-celo.cjs --network celoSepolia
 *
 * Get testnet CELO from: https://faucet.celo.org/celo-sepolia
 */
const hre = require("hardhat");
const fs = require("fs");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying to Celo Alfajores with:", deployer.address);

  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Balance:", hre.ethers.formatEther(balance), "CELO");

  if (balance === 0n) {
    console.error("\nERROR: No CELO balance. Get testnet CELO from:");
    console.error("  https://faucet.celo.org/celo-sepolia");
    process.exit(1);
  }

  // Deploy MockERC20 (USDC substitute — on Celo mainnet, real USDC supports fee abstraction)
  console.log("\n[1/4] Deploying Mock USDC (Celo)...");
  const MockToken = await hre.ethers.getContractFactory("MockERC20");
  const mockUSDC = await MockToken.deploy("Mock USDC", "mUSDC", 6);
  await mockUSDC.waitForDeployment();
  const mockUSDCAddr = await mockUSDC.getAddress();
  console.log("Mock USDC:", mockUSDCAddr);

  // Deploy Mock cUSD (Celo native stablecoin)
  console.log("[2/4] Deploying Mock cUSD (yield token)...");
  const mockYield = await MockToken.deploy("Mock cUSD", "mcUSD", 18);
  await mockYield.waitForDeployment();
  const mockYieldAddr = await mockYield.getAddress();
  console.log("Mock cUSD:", mockYieldAddr);

  // Deploy TreasuryVault
  console.log("[3/4] Deploying TreasuryVault...");
  const TreasuryVault = await hre.ethers.getContractFactory("TreasuryVault");
  const maxPerTx = hre.ethers.parseUnits("100", 6);
  const maxDaily = hre.ethers.parseUnits("500", 6);
  const treasury = await TreasuryVault.deploy(deployer.address, mockUSDCAddr, mockYieldAddr, maxPerTx, maxDaily);
  await treasury.waitForDeployment();
  const treasuryAddr = await treasury.getAddress();
  console.log("TreasuryVault:", treasuryAddr);

  // Deploy ServiceRegistry
  console.log("[4/4] Deploying ServiceRegistry...");
  const ServiceRegistry = await hre.ethers.getContractFactory("ServiceRegistry");
  const registry = await ServiceRegistry.deploy(mockUSDCAddr);
  await registry.waitForDeployment();
  const registryAddr = await registry.getAddress();
  console.log("ServiceRegistry:", registryAddr);

  // === Demo Interactions ===
  console.log("\n--- Running onchain demo on Celo ---");

  // Mint USDC
  const mintTx = await mockUSDC.mint(deployer.address, hre.ethers.parseUnits("10000", 6));
  const mintReceipt = await mintTx.wait();
  console.log("Minted 10,000 mUSDC | TX:", mintReceipt.hash);

  // Deposit $1000 into treasury
  await mockUSDC.approve(treasuryAddr, hre.ethers.parseUnits("1000", 6));
  const depositTx = await treasury.deposit(hre.ethers.parseUnits("1000", 6));
  const depositReceipt = await depositTx.wait();
  console.log("Deposited $1,000 (principal locked) | TX:", depositReceipt.hash);

  // Simulate yield accrual
  await mockUSDC.mint(treasuryAddr, hre.ethers.parseUnits("50", 6));
  console.log("Simulated $50 yield accrual");

  // Harvest yield
  const harvestTx = await treasury.harvestYield(hre.ethers.parseUnits("50", 6));
  const harvestReceipt = await harvestTx.wait();
  console.log("Harvested $50 yield | TX:", harvestReceipt.hash);

  // Register a service
  const svcTx = await registry.registerService(
    "AI Portfolio Analysis",
    "LLM-powered analysis of any wallet — powered by yield-funded inference on Celo",
    hre.ethers.parseUnits("1", 6)
  );
  const svcReceipt = await svcTx.wait();
  console.log("Registered service ($1/request) | TX:", svcReceipt.hash);

  // Agent spends from yield
  await mockUSDC.mint(treasuryAddr, hre.ethers.parseUnits("25", 6));
  const spendTx = await treasury.spend(
    deployer.address,
    hre.ethers.parseUnits("5", 6),
    "Bankr LLM inference - market analysis on Celo"
  );
  const spendReceipt = await spendTx.wait();
  console.log("Agent spent $5 on inference | TX:", spendReceipt.hash);

  // Service lifecycle: request + complete
  await mockUSDC.approve(registryAddr, hre.ethers.parseUnits("1", 6));
  const reqTx = await registry.requestService(0);
  const reqReceipt = await reqTx.wait();
  console.log("Service requested ($1 escrowed) | TX:", reqReceipt.hash);

  const completeTx = await registry.completeService(0);
  const completeReceipt = await completeTx.wait();
  console.log("Service completed (payment released) | TX:", completeReceipt.hash);

  // Final status
  const status = await treasury.getStatus();
  console.log("\n--- Final Treasury Status (Celo) ---");
  console.log("Principal (locked):", hre.ethers.formatUnits(status[0], 6), "USDC");
  console.log("Available Yield:", hre.ethers.formatUnits(status[1], 6), "USDC");
  console.log("Total Harvested:", hre.ethers.formatUnits(status[3], 6), "USDC");
  console.log("Total Spent:", hre.ethers.formatUnits(status[4], 6), "USDC");

  // Save deployment
  const deployment = {
    network: "Celo Sepolia (11142220)",
    deployer: deployer.address,
    explorer: "https://celo-sepolia.blockscout.com",
    contracts: {
      mockUSDC: mockUSDCAddr,
      mockCUSD: mockYieldAddr,
      treasuryVault: treasuryAddr,
      serviceRegistry: registryAddr
    },
    transactions: {
      mint: mintReceipt.hash,
      deposit: depositReceipt.hash,
      harvest: harvestReceipt.hash,
      registerService: svcReceipt.hash,
      agentSpend: spendReceipt.hash,
      serviceRequest: reqReceipt.hash,
      serviceComplete: completeReceipt.hash
    },
    timestamp: new Date().toISOString()
  };

  fs.writeFileSync("deployment-celo.json", JSON.stringify(deployment, null, 2));
  console.log("\n=== Celo deployment saved to deployment-celo.json ===");
  console.log(JSON.stringify(deployment, null, 2));

  console.log("\n=== WHY CELO ===");
  console.log("Celo is optimized for agentic activity:");
  console.log("  - Fee abstraction: agents pay gas in USDC (no CELO needed on mainnet)");
  console.log("  - Sub-cent transactions: enables continuous autonomous operation");
  console.log("  - 25+ stablecoins: native stablecoin-first treasury management");
  console.log("  - Mobile-first: MiniPay integration for real-world service delivery");
  console.log("  - ERC-8004 support: native agent identity standard");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
