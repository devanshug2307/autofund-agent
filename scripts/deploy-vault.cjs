const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deployer:", deployer.address);
  const bal = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Balance:", hre.ethers.formatEther(bal), "ETH");

  const mockUSDC = "0x5cFA9374C4DcdFE58A32d2702d73bB643cc85A36";
  const mockYield = "0xC7EBEcBfb08B437B6B00d51a7de004E047B4B116";
  const maxPerTx = hre.ethers.parseUnits("100", 6);
  const maxDaily = hre.ethers.parseUnits("500", 6);

  console.log("\nDeploying TreasuryVault...");
  const TV = await hre.ethers.getContractFactory("TreasuryVault");
  const tv = await TV.deploy(deployer.address, mockUSDC, mockYield, maxPerTx, maxDaily);
  await tv.waitForDeployment();
  console.log("TreasuryVault:", await tv.getAddress());

  console.log("\nDeploying ServiceRegistry...");
  const SR = await hre.ethers.getContractFactory("ServiceRegistry");
  const sr = await SR.deploy(mockUSDC);
  await sr.waitForDeployment();
  console.log("ServiceRegistry:", await sr.getAddress());

  console.log("\n=== ALL CONTRACTS ON BASE SEPOLIA ===");
  console.log("Mock USDC:       ", mockUSDC);
  console.log("Mock stETH:      ", mockYield);
  console.log("TreasuryVault:   ", await tv.getAddress());
  console.log("ServiceRegistry: ", await sr.getAddress());
}

main().catch(e => { console.error(e.message); process.exit(1); });
