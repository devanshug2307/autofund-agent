const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("TreasuryVault", function () {
  let treasury, mockUSDC, mockYield;
  let owner, agent, user;
  const DECIMALS = 6;

  beforeEach(async function () {
    [owner, agent, user] = await ethers.getSigners();

    // Deploy mock tokens
    const MockToken = await ethers.getContractFactory("MockERC20");
    mockUSDC = await MockToken.deploy("Mock USDC", "mUSDC", DECIMALS);
    mockYield = await MockToken.deploy("Mock stETH", "mstETH", 18);

    // Deploy treasury
    const TreasuryVault = await ethers.getContractFactory("TreasuryVault");
    const maxPerTx = ethers.parseUnits("100", DECIMALS);
    const maxDaily = ethers.parseUnits("500", DECIMALS);
    treasury = await TreasuryVault.deploy(
      agent.address,
      await mockUSDC.getAddress(),
      await mockYield.getAddress(),
      maxPerTx,
      maxDaily
    );

    // Mint tokens to owner for testing
    await mockUSDC.mint(owner.address, ethers.parseUnits("10000", DECIMALS));
  });

  describe("Deposits", function () {
    it("should accept deposits and lock principal", async function () {
      const amount = ethers.parseUnits("1000", DECIMALS);
      await mockUSDC.approve(await treasury.getAddress(), amount);
      await treasury.deposit(amount);

      expect(await treasury.getPrincipal()).to.equal(amount);
      expect(await treasury.totalDeposited()).to.equal(amount);
    });

    it("should reject zero deposits", async function () {
      await expect(treasury.deposit(0)).to.be.revertedWithCustomError(treasury, "ZeroAmount");
    });

    it("should track multiple deposits", async function () {
      const amount1 = ethers.parseUnits("500", DECIMALS);
      const amount2 = ethers.parseUnits("300", DECIMALS);
      await mockUSDC.approve(await treasury.getAddress(), amount1 + amount2);
      await treasury.deposit(amount1);
      await treasury.deposit(amount2);

      expect(await treasury.totalDeposited()).to.equal(amount1 + amount2);
    });
  });

  describe("Yield", function () {
    beforeEach(async function () {
      // Deposit principal
      const deposit = ethers.parseUnits("1000", DECIMALS);
      await mockUSDC.approve(await treasury.getAddress(), deposit);
      await treasury.deposit(deposit);
    });

    it("should show zero yield when no extra tokens", async function () {
      expect(await treasury.getAvailableYield()).to.equal(0);
    });

    it("should show yield when extra tokens arrive", async function () {
      const yield_ = ethers.parseUnits("50", DECIMALS);
      await mockUSDC.mint(await treasury.getAddress(), yield_);
      expect(await treasury.getAvailableYield()).to.equal(yield_);
    });

    it("should allow agent to harvest yield", async function () {
      const yield_ = ethers.parseUnits("50", DECIMALS);
      await mockUSDC.mint(await treasury.getAddress(), yield_);

      const balBefore = await mockUSDC.balanceOf(agent.address);
      await treasury.connect(agent).harvestYield(yield_);
      const balAfter = await mockUSDC.balanceOf(agent.address);

      expect(balAfter - balBefore).to.equal(yield_);
      expect(await treasury.totalYieldHarvested()).to.equal(yield_);
    });

    it("should NOT allow agent to harvest more than yield", async function () {
      const yield_ = ethers.parseUnits("50", DECIMALS);
      await mockUSDC.mint(await treasury.getAddress(), yield_);

      const tooMuch = ethers.parseUnits("100", DECIMALS);
      await expect(
        treasury.connect(agent).harvestYield(tooMuch)
      ).to.be.revertedWithCustomError(treasury, "InsufficientYield");
    });

    it("should NOT allow non-agent to harvest", async function () {
      const yield_ = ethers.parseUnits("50", DECIMALS);
      await mockUSDC.mint(await treasury.getAddress(), yield_);

      await expect(
        treasury.connect(user).harvestYield(yield_)
      ).to.be.revertedWithCustomError(treasury, "OnlyAgent");
    });
  });

  describe("Spending Guardrails", function () {
    beforeEach(async function () {
      const deposit = ethers.parseUnits("1000", DECIMALS);
      await mockUSDC.approve(await treasury.getAddress(), deposit);
      await treasury.deposit(deposit);
      // Add yield
      await mockUSDC.mint(await treasury.getAddress(), ethers.parseUnits("200", DECIMALS));
    });

    it("should allow agent to spend within limits", async function () {
      await treasury.connect(agent).spend(
        user.address,
        ethers.parseUnits("50", DECIMALS),
        "LLM inference payment"
      );
      expect(await treasury.totalSpent()).to.equal(ethers.parseUnits("50", DECIMALS));
    });

    it("should reject spend exceeding per-transaction limit", async function () {
      await expect(
        treasury.connect(agent).spend(
          user.address,
          ethers.parseUnits("150", DECIMALS), // Max is 100
          "Too much"
        )
      ).to.be.revertedWithCustomError(treasury, "ExceedsTransactionLimit");
    });

    it("should reject spend exceeding daily limit", async function () {
      // Add more yield so we don't run out before hitting daily cap
      await mockUSDC.mint(await treasury.getAddress(), ethers.parseUnits("800", DECIMALS));
      // Spend up to near daily limit (500 total, doing 5 x 99 = 495)
      for (let i = 0; i < 5; i++) {
        await treasury.connect(agent).spend(
          user.address,
          ethers.parseUnits("99", DECIMALS),
          `Payment ${i}`
        );
      }
      // This should exceed the daily $500 limit (495 + 10 = 505 > 500)
      await expect(
        treasury.connect(agent).spend(
          user.address,
          ethers.parseUnits("10", DECIMALS),
          "Over daily"
        )
      ).to.be.revertedWithCustomError(treasury, "ExceedsDailyLimit");
    });

    it("should track daily spending correctly", async function () {
      await treasury.connect(agent).spend(user.address, ethers.parseUnits("50", DECIMALS), "Test");
      const remaining = await treasury.getRemainingDailyAllowance();
      expect(remaining).to.equal(ethers.parseUnits("450", DECIMALS));
    });

    it("should NOT allow spending principal", async function () {
      // Only 200 yield available, try to spend 300
      await expect(
        treasury.connect(agent).spend(
          user.address,
          ethers.parseUnits("99", DECIMALS),
          "OK"
        )
      ).to.not.be.reverted; // 99 < 200 yield, should pass

      // Spend more to eat into principal
      await treasury.connect(agent).spend(user.address, ethers.parseUnits("99", DECIMALS), "OK2");
      // Now only 2 yield left
      await expect(
        treasury.connect(agent).spend(user.address, ethers.parseUnits("5", DECIMALS), "Too much")
      ).to.be.revertedWithCustomError(treasury, "InsufficientYield");
    });
  });

  describe("Status", function () {
    it("should return full status", async function () {
      const deposit = ethers.parseUnits("1000", DECIMALS);
      await mockUSDC.approve(await treasury.getAddress(), deposit);
      await treasury.deposit(deposit);
      await mockUSDC.mint(await treasury.getAddress(), ethers.parseUnits("50", DECIMALS));

      const [principal, availYield, yieldBal, harvested, spent, dailyRem] = await treasury.getStatus();
      expect(principal).to.equal(deposit);
      expect(availYield).to.equal(ethers.parseUnits("50", DECIMALS));
    });
  });
});

describe("ServiceRegistry", function () {
  let registry, mockUSDC;
  let provider, requester;

  beforeEach(async function () {
    [provider, requester] = await ethers.getSigners();

    const MockToken = await ethers.getContractFactory("MockERC20");
    mockUSDC = await MockToken.deploy("Mock USDC", "mUSDC", 6);

    const ServiceRegistry = await ethers.getContractFactory("ServiceRegistry");
    registry = await ServiceRegistry.deploy(await mockUSDC.getAddress());

    await mockUSDC.mint(requester.address, ethers.parseUnits("1000", 6));
  });

  it("should register a service", async function () {
    await registry.connect(provider).registerService(
      "Portfolio Analysis",
      "AI-powered portfolio analysis",
      ethers.parseUnits("1", 6)
    );
    const svc = await registry.services(0);
    expect(svc.name).to.equal("Portfolio Analysis");
    expect(svc.active).to.be.true;
  });

  it("should handle full service lifecycle", async function () {
    // Register
    await registry.connect(provider).registerService(
      "Market Report",
      "Daily market analysis",
      ethers.parseUnits("5", 6)
    );

    // Request (requester pays)
    await mockUSDC.connect(requester).approve(
      await registry.getAddress(),
      ethers.parseUnits("5", 6)
    );
    await registry.connect(requester).requestService(0);

    // Verify payment held in escrow
    expect(await mockUSDC.balanceOf(await registry.getAddress())).to.equal(
      ethers.parseUnits("5", 6)
    );

    // Complete (provider receives payment)
    const balBefore = await mockUSDC.balanceOf(provider.address);
    await registry.connect(provider).completeService(0);
    const balAfter = await mockUSDC.balanceOf(provider.address);

    expect(balAfter - balBefore).to.equal(ethers.parseUnits("5", 6));

    // Check completion count
    const svc = await registry.services(0);
    expect(svc.completedCount).to.equal(1);
  });

  it("should reject double completion", async function () {
    await registry.connect(provider).registerService("Svc", "Desc", ethers.parseUnits("1", 6));
    await mockUSDC.connect(requester).approve(await registry.getAddress(), ethers.parseUnits("1", 6));
    await registry.connect(requester).requestService(0);
    await registry.connect(provider).completeService(0);

    await expect(registry.connect(provider).completeService(0)).to.be.revertedWith("Already completed");
  });
});
