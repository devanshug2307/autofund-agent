const hre = require("hardhat");
const DEPLOYED = {
  mockUSDC: "0x5cFA9374C4DcdFE58A32d2702d73bB643cc85A36",
  treasuryVault: "0xDcb6aEdb34b7c91F3b83a0Bf61c7d84DB2f9F2bF",
  serviceRegistry: "0xa602931E5976FA282d0887c8Bd1741a6FEfF9Dc1"
};
async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const mockUSDC = await hre.ethers.getContractAt("MockERC20", DEPLOYED.mockUSDC);
  const treasury = await hre.ethers.getContractAt("TreasuryVault", DEPLOYED.treasuryVault);
  const registry = await hre.ethers.getContractAt("ServiceRegistry", DEPLOYED.serviceRegistry);

  console.log("Continuing onchain demo...\n");

  // Simulate yield
  console.log("[3] Simulating $50 yield...");
  let tx = await mockUSDC.mint(DEPLOYED.treasuryVault, hre.ethers.parseUnits("50", 6));
  let r = await tx.wait();
  console.log("   TX:", r.hash);

  // Harvest yield
  console.log("[4] Harvesting $50 yield...");
  tx = await treasury.harvestYield(hre.ethers.parseUnits("50", 6));
  r = await tx.wait();
  console.log("   TX:", r.hash);

  // Register service
  console.log("[5] Registering service...");
  tx = await registry.registerService("AI Portfolio Analysis", "LLM-powered analysis", hre.ethers.parseUnits("1", 6));
  r = await tx.wait();
  console.log("   TX:", r.hash);

  // Agent spends on inference
  console.log("[6] Agent spending $5 on inference...");
  await (await mockUSDC.mint(DEPLOYED.treasuryVault, hre.ethers.parseUnits("25", 6))).wait();
  tx = await treasury.spend(deployer.address, hre.ethers.parseUnits("5", 6), "Bankr LLM inference");
  r = await tx.wait();
  console.log("   TX:", r.hash);

  // Final status
  const s = await treasury.getStatus();
  console.log("\n=== ONCHAIN TREASURY STATUS ===");
  console.log("Principal (locked):", hre.ethers.formatUnits(s[0], 6), "USDC");
  console.log("Available Yield:", hre.ethers.formatUnits(s[1], 6), "USDC");
  console.log("Total Harvested:", hre.ethers.formatUnits(s[3], 6), "USDC");
  console.log("Total Spent:", hre.ethers.formatUnits(s[4], 6), "USDC");
}
main().catch(e => { console.error(e.message); process.exit(1); });
