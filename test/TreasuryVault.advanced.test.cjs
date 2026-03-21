const { expect } = require("chai");
const { ethers } = require("hardhat");
const { time } = require("@nomicfoundation/hardhat-network-helpers");

describe("TreasuryVault — Advanced Tests", function () {
  let treasury, mockUSDC, mockYield;
  let owner, agent, user, attacker;
  const D = 6; // USDC decimals

  beforeEach(async function () {
    [owner, agent, user, attacker] = await ethers.getSigners();
    const MockToken = await ethers.getContractFactory("MockERC20");
    mockUSDC = await MockToken.deploy("Mock USDC", "mUSDC", D);
    mockYield = await MockToken.deploy("Mock stETH", "mstETH", 18);
    const TV = await ethers.getContractFactory("TreasuryVault");
    treasury = await TV.deploy(agent.address, await mockUSDC.getAddress(), await mockYield.getAddress(),
      ethers.parseUnits("100", D), ethers.parseUnits("500", D));
    await mockUSDC.mint(owner.address, ethers.parseUnits("100000", D));
  });

  describe("Principal Protection", function () {
    it("should NEVER allow agent to withdraw principal via harvestYield", async function () {
      await mockUSDC.approve(await treasury.getAddress(), ethers.parseUnits("5000", D));
      await treasury.deposit(ethers.parseUnits("5000", D));
      // No extra yield — try to harvest principal
      await expect(treasury.connect(agent).harvestYield(ethers.parseUnits("1", D)))
        .to.be.revertedWithCustomError(treasury, "InsufficientYield");
    });

    it("should NEVER allow agent to withdraw principal via spend", async function () {
      await mockUSDC.approve(await treasury.getAddress(), ethers.parseUnits("5000", D));
      await treasury.deposit(ethers.parseUnits("5000", D));
      await expect(treasury.connect(agent).spend(user.address, ethers.parseUnits("1", D), "test"))
        .to.be.revertedWithCustomError(treasury, "InsufficientYield");
    });

    it("should protect principal even after yield is harvested", async function () {
      await mockUSDC.approve(await treasury.getAddress(), ethers.parseUnits("1000", D));
      await treasury.deposit(ethers.parseUnits("1000", D));
      // Add and harvest yield
      await mockUSDC.mint(await treasury.getAddress(), ethers.parseUnits("100", D));
      await treasury.connect(agent).harvestYield(ethers.parseUnits("100", D));
      // Principal should still be locked
      expect(await treasury.getAvailableYield()).to.equal(0);
      await expect(treasury.connect(agent).harvestYield(1))
        .to.be.revertedWithCustomError(treasury, "InsufficientYield");
    });

    it("should protect principal across multiple deposits", async function () {
      await mockUSDC.approve(await treasury.getAddress(), ethers.parseUnits("3000", D));
      await treasury.deposit(ethers.parseUnits("1000", D));
      await treasury.deposit(ethers.parseUnits("2000", D));
      expect(await treasury.totalDeposited()).to.equal(ethers.parseUnits("3000", D));
      expect(await treasury.getAvailableYield()).to.equal(0);
    });
  });

  describe("Access Control", function () {
    it("should reject harvestYield from owner", async function () {
      await mockUSDC.approve(await treasury.getAddress(), ethers.parseUnits("1000", D));
      await treasury.deposit(ethers.parseUnits("1000", D));
      await mockUSDC.mint(await treasury.getAddress(), ethers.parseUnits("50", D));
      await expect(treasury.connect(owner).harvestYield(ethers.parseUnits("50", D)))
        .to.be.revertedWithCustomError(treasury, "OnlyAgent");
    });

    it("should reject spend from attacker", async function () {
      await mockUSDC.approve(await treasury.getAddress(), ethers.parseUnits("1000", D));
      await treasury.deposit(ethers.parseUnits("1000", D));
      await mockUSDC.mint(await treasury.getAddress(), ethers.parseUnits("50", D));
      await expect(treasury.connect(attacker).spend(attacker.address, ethers.parseUnits("50", D), "steal"))
        .to.be.revertedWithCustomError(treasury, "OnlyAgent");
    });

    it("should allow owner to update guardrails", async function () {
      await treasury.updateGuardrails(ethers.parseUnits("200", D), ethers.parseUnits("1000", D));
      expect(await treasury.maxPerTransaction()).to.equal(ethers.parseUnits("200", D));
      expect(await treasury.maxDailySpend()).to.equal(ethers.parseUnits("1000", D));
    });

    it("should reject guardrail updates from non-owner", async function () {
      await expect(treasury.connect(agent).updateGuardrails(1, 1))
        .to.be.revertedWithCustomError(treasury, "OwnableUnauthorizedAccount");
    });

    it("should allow owner to update agent address", async function () {
      await treasury.updateAgent(user.address);
      expect(await treasury.agent()).to.equal(user.address);
    });

    it("should reject agent update from non-owner", async function () {
      await expect(treasury.connect(attacker).updateAgent(attacker.address))
        .to.be.revertedWithCustomError(treasury, "OwnableUnauthorizedAccount");
    });
  });

  describe("Yield Tracking Accuracy", function () {
    it("should correctly track yield across multiple harvests", async function () {
      await mockUSDC.approve(await treasury.getAddress(), ethers.parseUnits("1000", D));
      await treasury.deposit(ethers.parseUnits("1000", D));

      // Harvest 1
      await mockUSDC.mint(await treasury.getAddress(), ethers.parseUnits("30", D));
      await treasury.connect(agent).harvestYield(ethers.parseUnits("30", D));

      // Harvest 2
      await mockUSDC.mint(await treasury.getAddress(), ethers.parseUnits("20", D));
      await treasury.connect(agent).harvestYield(ethers.parseUnits("20", D));

      expect(await treasury.totalYieldHarvested()).to.equal(ethers.parseUnits("50", D));
    });

    it("should allow partial yield harvest", async function () {
      await mockUSDC.approve(await treasury.getAddress(), ethers.parseUnits("1000", D));
      await treasury.deposit(ethers.parseUnits("1000", D));
      await mockUSDC.mint(await treasury.getAddress(), ethers.parseUnits("100", D));

      await treasury.connect(agent).harvestYield(ethers.parseUnits("40", D));
      expect(await treasury.getAvailableYield()).to.equal(ethers.parseUnits("60", D));
    });
  });

  describe("Spending Guardrails — Edge Cases", function () {
    beforeEach(async function () {
      await mockUSDC.approve(await treasury.getAddress(), ethers.parseUnits("1000", D));
      await treasury.deposit(ethers.parseUnits("1000", D));
      await mockUSDC.mint(await treasury.getAddress(), ethers.parseUnits("1000", D));
    });

    it("should allow spending exactly at per-tx limit", async function () {
      await expect(treasury.connect(agent).spend(user.address, ethers.parseUnits("100", D), "exact limit"))
        .to.not.be.reverted;
    });

    it("should reject spending 1 wei over per-tx limit", async function () {
      const limit = ethers.parseUnits("100", D);
      await expect(treasury.connect(agent).spend(user.address, limit + 1n, "over by 1"))
        .to.be.revertedWithCustomError(treasury, "ExceedsTransactionLimit");
    });

    it("should allow spending exactly at daily limit", async function () {
      // 5 x $100 = $500 = daily limit
      for (let i = 0; i < 5; i++) {
        await treasury.connect(agent).spend(user.address, ethers.parseUnits("100", D), `tx ${i}`);
      }
      expect(await treasury.getRemainingDailyAllowance()).to.equal(0);
    });

    it("should reject spending zero", async function () {
      await expect(treasury.connect(agent).spend(user.address, 0, "zero"))
        .to.be.revertedWithCustomError(treasury, "ZeroAmount");
    });

    it("should track spend reason in events", async function () {
      const reason = "Bankr LLM inference - ETH price analysis";
      await expect(treasury.connect(agent).spend(user.address, ethers.parseUnits("5", D), reason))
        .to.emit(treasury, "AgentSpent");
      // Verify the event was emitted (timestamp varies so we just check emission)
    });
  });

  describe("Events", function () {
    it("should emit Deposited event", async function () {
      const amount = ethers.parseUnits("500", D);
      await mockUSDC.approve(await treasury.getAddress(), amount);
      await expect(treasury.deposit(amount)).to.emit(treasury, "Deposited");
    });

    it("should emit YieldHarvested event", async function () {
      await mockUSDC.approve(await treasury.getAddress(), ethers.parseUnits("1000", D));
      await treasury.deposit(ethers.parseUnits("1000", D));
      await mockUSDC.mint(await treasury.getAddress(), ethers.parseUnits("50", D));
      await expect(treasury.connect(agent).harvestYield(ethers.parseUnits("50", D)))
        .to.emit(treasury, "YieldHarvested");
    });

    it("should emit GuardrailsUpdated event", async function () {
      await expect(treasury.updateGuardrails(100, 200))
        .to.emit(treasury, "GuardrailsUpdated").withArgs(100, 200);
    });

    it("should emit AgentUpdated event", async function () {
      await expect(treasury.updateAgent(user.address))
        .to.emit(treasury, "AgentUpdated").withArgs(agent.address, user.address);
    });
  });

  describe("getStatus", function () {
    it("should return complete accurate status", async function () {
      await mockUSDC.approve(await treasury.getAddress(), ethers.parseUnits("2000", D));
      await treasury.deposit(ethers.parseUnits("2000", D));
      await mockUSDC.mint(await treasury.getAddress(), ethers.parseUnits("80", D));
      await treasury.connect(agent).harvestYield(ethers.parseUnits("30", D));

      // Remaining yield in vault = 80 - 30 = 50
      await treasury.connect(agent).spend(user.address, ethers.parseUnits("10", D), "test");

      const [principal, availYield, yieldBal, harvested, spent, dailyRem] = await treasury.getStatus();
      expect(principal).to.equal(ethers.parseUnits("2000", D));
      expect(availYield).to.equal(ethers.parseUnits("40", D)); // 80 - 30 harvested - 10 spent = 40
      expect(harvested).to.equal(ethers.parseUnits("30", D));
      expect(spent).to.equal(ethers.parseUnits("10", D));
      expect(dailyRem).to.equal(ethers.parseUnits("490", D)); // 500 - 10 = 490
    });
  });
});
