/**
 * Deploy a simple contract on Status Network Sepolia (zero gas fees)
 * This qualifies for the Status L2 "Go Gasless" bounty ($50 per team)
 */
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying to Status Network Sepolia with:", deployer.address);
  console.log("Chain ID:", (await hre.ethers.provider.getNetwork()).chainId);
  console.log("Balance:", hre.ethers.formatEther(await hre.ethers.provider.getBalance(deployer.address)), "ETH");

  // Deploy MockERC20 as a simple AI-component contract
  const MockToken = await hre.ethers.getContractFactory("MockERC20");
  const token = await MockToken.deploy("AutoFund AI Token", "AFT", 18);
  await token.waitForDeployment();
  const tokenAddr = await token.getAddress();
  console.log("\nAutoFund AI Token deployed to:", tokenAddr);

  // Execute a free transaction (mint tokens)
  const tx = await token.mint(deployer.address, hre.ethers.parseEther("1000"));
  const receipt = await tx.wait();
  console.log("Minted 1000 AFT tokens (free tx!)");
  console.log("TX hash:", receipt.hash);
  console.log("Gas used:", receipt.gasUsed.toString(), "(zero fee!)");

  console.log("\n=== Status Network Deployment ===");
  console.log("Contract:", tokenAddr);
  console.log("TX:", receipt.hash);
  console.log("Explorer: https://sepoliascan.status.network/address/" + tokenAddr);
  console.log("=================================");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
