/**
 * Run onchain demo interactions on Base Sepolia.
 * Creates real transactions that judges can verify on BaseScan.
 */
const hre = require("hardhat");

const DEPLOYED = {
  mockUSDC: "0x5cFA9374C4DcdFE58A32d2702d73bB643cc85A36",
  mockstETH: "0xC7EBEcBfb08B437B6B00d51a7de004E047B4B116",
  treasuryVault: "0xDcb6aEdb34b7c91F3b83a0Bf61c7d84DB2f9F2bF",
  serviceRegistry: "0xa602931E5976FA282d0887c8Bd1741a6FEfF9Dc1"
};

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Running onchain demo with:", deployer.address);

  // Attach to deployed contracts
  const mockUSDC = await hre.ethers.getContractAt("MockERC20", DEPLOYED.mockUSDC);
  const treasury = await hre.ethers.getContractAt("TreasuryVault", DEPLOYED.treasuryVault);
  const registry = await hre.ethers.getContractAt("ServiceRegistry", DEPLOYED.serviceRegistry);

  // 1. Mint mock USDC
  console.log("\n[1] Minting 10,000 mUSDC...");
  let tx = await mockUSDC.mint(deployer.address, hre.ethers.parseUnits("10000", 6));
  let receipt = await tx.wait();
  console.log("   TX:", receipt.hash);

  // 2. Deposit into treasury (locks principal)
  console.log("\n[2] Depositing $1,000 into TreasuryVault (principal locked)...");
  tx = await mockUSDC.approve(DEPLOYED.treasuryVault, hre.ethers.parseUnits("1000", 6));
  await tx.wait();
  tx = await treasury.deposit(hre.ethers.parseUnits("1000", 6));
  receipt = await tx.wait();
  console.log("   TX:", receipt.hash);

  // 3. Simulate yield accrual
  console.log("\n[3] Simulating $50 yield accrual...");
  tx = await mockUSDC.mint(DEPLOYED.treasuryVault, hre.ethers.parseUnits("50", 6));
  receipt = await tx.wait();
  console.log("   TX:", receipt.hash);

  // 4. Harvest yield
  console.log("\n[4] Agent harvesting $50 yield...");
  tx = await treasury.harvestYield(hre.ethers.parseUnits("50", 6));
  receipt = await tx.wait();
  console.log("   TX:", receipt.hash);

  // 5. Register service
  console.log("\n[5] Registering 'AI Portfolio Analysis' service at $1...");
  tx = await registry.registerService(
    "AI Portfolio Analysis",
    "LLM-powered wallet analysis with optimization recommendations",
    hre.ethers.parseUnits("1", 6)
  );
  receipt = await tx.wait();
  console.log("   TX:", receipt.hash);

  // 6. Agent spends yield on inference
  console.log("\n[6] Agent spending $5 from yield on LLM inference...");
  tx = await mockUSDC.mint(DEPLOYED.treasuryVault, hre.ethers.parseUnits("25", 6));
  await tx.wait();
  tx = await treasury.spend(
    deployer.address,
    hre.ethers.parseUnits("5", 6),
    "Bankr LLM inference - market analysis"
  );
  receipt = await tx.wait();
  console.log("   TX:", receipt.hash);

  // 7. Check final status
  const status = await treasury.getStatus();
  console.log("\n=== ONCHAIN TREASURY STATUS ===");
  console.log("Principal (locked):", hre.ethers.formatUnits(status[0], 6), "USDC");
  console.log("Available Yield:", hre.ethers.formatUnits(status[1], 6), "USDC");
  console.log("Total Harvested:", hre.ethers.formatUnits(status[3], 6), "USDC");
  console.log("Total Spent:", hre.ethers.formatUnits(status[4], 6), "USDC");
  console.log("Daily Remaining:", hre.ethers.formatUnits(status[5], 6), "USDC");
  console.log("==============================");
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
