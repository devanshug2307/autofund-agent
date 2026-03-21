const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with:", deployer.address);
  console.log("Balance:", hre.ethers.formatEther(await hre.ethers.provider.getBalance(deployer.address)), "ETH");

  // For testnet, we use the deployer as both owner and agent
  // and use placeholder token addresses (will be real on mainnet)
  const agentAddress = deployer.address;

  // Deploy a mock ERC20 for testing (USDC substitute)
  const MockToken = await hre.ethers.getContractFactory("MockERC20");
  const mockUSDC = await MockToken.deploy("Mock USDC", "mUSDC", 6);
  await mockUSDC.waitForDeployment();
  const mockUSDCAddr = await mockUSDC.getAddress();
  console.log("Mock USDC deployed to:", mockUSDCAddr);

  // Deploy a mock yield token
  const mockYield = await MockToken.deploy("Mock stETH", "mstETH", 18);
  await mockYield.waitForDeployment();
  const mockYieldAddr = await mockYield.getAddress();
  console.log("Mock stETH deployed to:", mockYieldAddr);

  // Deploy TreasuryVault
  const TreasuryVault = await hre.ethers.getContractFactory("TreasuryVault");
  const maxPerTx = hre.ethers.parseUnits("100", 6);    // $100 per transaction
  const maxDaily = hre.ethers.parseUnits("500", 6);     // $500 per day
  const treasury = await TreasuryVault.deploy(
    agentAddress,
    mockUSDCAddr,
    mockYieldAddr,
    maxPerTx,
    maxDaily
  );
  await treasury.waitForDeployment();
  const treasuryAddr = await treasury.getAddress();
  console.log("TreasuryVault deployed to:", treasuryAddr);

  // Deploy ServiceRegistry
  const ServiceRegistry = await hre.ethers.getContractFactory("ServiceRegistry");
  const registry = await ServiceRegistry.deploy(mockUSDCAddr);
  await registry.waitForDeployment();
  const registryAddr = await registry.getAddress();
  console.log("ServiceRegistry deployed to:", registryAddr);

  // --- Demo interactions ---

  // Mint some mock USDC to deployer
  const mintAmount = hre.ethers.parseUnits("10000", 6); // $10,000
  await mockUSDC.mint(deployer.address, mintAmount);
  console.log("\nMinted 10,000 mUSDC to deployer");

  // Deposit into treasury
  const depositAmount = hre.ethers.parseUnits("1000", 6); // $1,000
  await mockUSDC.approve(treasuryAddr, depositAmount);
  await treasury.deposit(depositAmount);
  console.log("Deposited $1,000 into TreasuryVault (principal locked)");

  // Simulate yield by sending extra tokens to vault
  const yieldAmount = hre.ethers.parseUnits("50", 6); // $50 yield
  await mockUSDC.mint(treasuryAddr, yieldAmount);
  console.log("Simulated $50 yield accrual");

  // Check status
  const status = await treasury.getStatus();
  console.log("\n--- Treasury Status ---");
  console.log("Principal (locked):", hre.ethers.formatUnits(status[0], 6), "USDC");
  console.log("Available Yield:", hre.ethers.formatUnits(status[1], 6), "USDC");
  console.log("Daily Remaining:", hre.ethers.formatUnits(status[5], 6), "USDC");

  // Harvest yield
  await treasury.harvestYield(yieldAmount);
  console.log("\nAgent harvested $50 yield");

  // Register a service
  const servicePrice = hre.ethers.parseUnits("1", 6); // $1 per analysis
  await registry.registerService(
    "Portfolio Analysis",
    "AI-powered analysis of any Ethereum wallet portfolio with recommendations",
    servicePrice
  );
  console.log("Registered 'Portfolio Analysis' service at $1/request");

  // Spend from yield (simulating paying for inference)
  await mockUSDC.mint(treasuryAddr, hre.ethers.parseUnits("25", 6));
  await treasury.spend(
    deployer.address,
    hre.ethers.parseUnits("5", 6),
    "Bankr LLM inference - market analysis"
  );
  console.log("Agent spent $5 on LLM inference from yield");

  // Final status
  const finalStatus = await treasury.getStatus();
  console.log("\n--- Final Treasury Status ---");
  console.log("Principal (locked):", hre.ethers.formatUnits(finalStatus[0], 6), "USDC");
  console.log("Available Yield:", hre.ethers.formatUnits(finalStatus[1], 6), "USDC");
  console.log("Total Harvested:", hre.ethers.formatUnits(finalStatus[3], 6), "USDC");
  console.log("Total Spent:", hre.ethers.formatUnits(finalStatus[4], 6), "USDC");

  console.log("\n=== Deployment Summary ===");
  console.log("Mock USDC:", mockUSDCAddr);
  console.log("Mock stETH:", mockYieldAddr);
  console.log("TreasuryVault:", treasuryAddr);
  console.log("ServiceRegistry:", registryAddr);
  console.log("Agent/Owner:", deployer.address);
  console.log("========================");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
