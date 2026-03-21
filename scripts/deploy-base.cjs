/**
 * Deploy AutoFund contracts to Base Sepolia testnet.
 * Run after getting testnet ETH from a faucet.
 *
 * Usage: npx hardhat --config hardhat.config.cjs run scripts/deploy-base.cjs --network baseSepolia
 */
const hre = require("hardhat");
const fs = require("fs");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying to Base Sepolia with:", deployer.address);

  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Balance:", hre.ethers.formatEther(balance), "ETH");

  if (balance === 0n) {
    console.error("\nERROR: No ETH balance. Get testnet ETH from:");
    console.error("  https://faucets.chain.link/base-sepolia");
    console.error("  https://faucet.quicknode.com/base/sepolia");
    process.exit(1);
  }

  // Deploy MockERC20 (USDC substitute)
  console.log("\n[1/4] Deploying Mock USDC...");
  const MockToken = await hre.ethers.getContractFactory("MockERC20");
  const mockUSDC = await MockToken.deploy("Mock USDC", "mUSDC", 6);
  await mockUSDC.waitForDeployment();
  const mockUSDCAddr = await mockUSDC.getAddress();
  console.log("Mock USDC:", mockUSDCAddr);

  // Deploy Mock stETH
  console.log("[2/4] Deploying Mock stETH...");
  const mockYield = await MockToken.deploy("Mock stETH", "mstETH", 18);
  await mockYield.waitForDeployment();
  const mockYieldAddr = await mockYield.getAddress();
  console.log("Mock stETH:", mockYieldAddr);

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
  console.log("\n--- Running onchain demo ---");

  // Mint USDC
  await mockUSDC.mint(deployer.address, hre.ethers.parseUnits("10000", 6));
  console.log("Minted 10,000 mUSDC");

  // Deposit $1000 into treasury
  await mockUSDC.approve(treasuryAddr, hre.ethers.parseUnits("1000", 6));
  const depositTx = await treasury.deposit(hre.ethers.parseUnits("1000", 6));
  const depositReceipt = await depositTx.wait();
  console.log("Deposited $1,000 (principal locked) | TX:", depositReceipt.hash);

  // Simulate yield
  await mockUSDC.mint(treasuryAddr, hre.ethers.parseUnits("50", 6));
  console.log("Simulated $50 yield");

  // Harvest yield
  const harvestTx = await treasury.harvestYield(hre.ethers.parseUnits("50", 6));
  const harvestReceipt = await harvestTx.wait();
  console.log("Harvested $50 yield | TX:", harvestReceipt.hash);

  // Register a service
  const svcTx = await registry.registerService(
    "AI Portfolio Analysis",
    "LLM-powered analysis of any wallet with recommendations",
    hre.ethers.parseUnits("1", 6)
  );
  const svcReceipt = await svcTx.wait();
  console.log("Registered service ($1/request) | TX:", svcReceipt.hash);

  // Spend from yield (inference payment)
  await mockUSDC.mint(treasuryAddr, hre.ethers.parseUnits("25", 6));
  const spendTx = await treasury.spend(
    deployer.address,
    hre.ethers.parseUnits("5", 6),
    "Bankr LLM inference - market analysis"
  );
  const spendReceipt = await spendTx.wait();
  console.log("Agent spent $5 on inference | TX:", spendReceipt.hash);

  // Final status
  const status = await treasury.getStatus();
  console.log("\n--- Final Treasury Status ---");
  console.log("Principal (locked):", hre.ethers.formatUnits(status[0], 6), "USDC");
  console.log("Available Yield:", hre.ethers.formatUnits(status[1], 6), "USDC");
  console.log("Total Harvested:", hre.ethers.formatUnits(status[3], 6), "USDC");
  console.log("Total Spent:", hre.ethers.formatUnits(status[4], 6), "USDC");

  // Save deployment addresses
  const deployment = {
    network: "Base Sepolia (84532)",
    deployer: deployer.address,
    contracts: {
      mockUSDC: mockUSDCAddr,
      mockstETH: mockYieldAddr,
      treasuryVault: treasuryAddr,
      serviceRegistry: registryAddr
    },
    transactions: {
      deposit: depositReceipt.hash,
      harvest: harvestReceipt.hash,
      registerService: svcReceipt.hash,
      agentSpend: spendReceipt.hash
    },
    timestamp: new Date().toISOString()
  };

  fs.writeFileSync("deployment.json", JSON.stringify(deployment, null, 2));
  console.log("\n=== Deployment saved to deployment.json ===");
  console.log(JSON.stringify(deployment, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
