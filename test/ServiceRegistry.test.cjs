const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ServiceRegistry - Extended Tests", function () {
  let registry, mockUSDC;
  let provider, requester, otherUser;

  beforeEach(async function () {
    [provider, requester, otherUser] = await ethers.getSigners();

    const MockToken = await ethers.getContractFactory("MockERC20");
    mockUSDC = await MockToken.deploy("Mock USDC", "mUSDC", 6);

    const ServiceRegistry = await ethers.getContractFactory("ServiceRegistry");
    registry = await ServiceRegistry.deploy(await mockUSDC.getAddress());

    await mockUSDC.mint(requester.address, ethers.parseUnits("10000", 6));
    await mockUSDC.mint(otherUser.address, ethers.parseUnits("10000", 6));
  });

  describe("Service Registration", function () {
    it("should register multiple services", async function () {
      await registry.connect(provider).registerService("Service A", "Desc A", ethers.parseUnits("1", 6));
      await registry.connect(provider).registerService("Service B", "Desc B", ethers.parseUnits("5", 6));
      await registry.connect(otherUser).registerService("Service C", "Desc C", ethers.parseUnits("10", 6));

      expect(await registry.nextServiceId()).to.equal(3);
      expect((await registry.services(0)).name).to.equal("Service A");
      expect((await registry.services(1)).name).to.equal("Service B");
      expect((await registry.services(2)).provider).to.equal(otherUser.address);
    });

    it("should track active service count", async function () {
      await registry.connect(provider).registerService("Active", "Desc", ethers.parseUnits("1", 6));
      await registry.connect(provider).registerService("Also Active", "Desc", ethers.parseUnits("2", 6));

      expect(await registry.getActiveServiceCount()).to.equal(2);

      await registry.connect(provider).deactivateService(0);
      expect(await registry.getActiveServiceCount()).to.equal(1);
    });
  });

  describe("Service Deactivation", function () {
    it("should deactivate a service", async function () {
      await registry.connect(provider).registerService("Test", "Desc", ethers.parseUnits("1", 6));
      await registry.connect(provider).deactivateService(0);

      expect((await registry.services(0)).active).to.be.false;
    });

    it("should reject deactivation by non-provider", async function () {
      await registry.connect(provider).registerService("Test", "Desc", ethers.parseUnits("1", 6));
      await expect(
        registry.connect(otherUser).deactivateService(0)
      ).to.be.revertedWith("Not provider");
    });

    it("should reject requests for inactive services", async function () {
      await registry.connect(provider).registerService("Test", "Desc", ethers.parseUnits("1", 6));
      await registry.connect(provider).deactivateService(0);

      await mockUSDC.connect(requester).approve(await registry.getAddress(), ethers.parseUnits("1", 6));
      await expect(
        registry.connect(requester).requestService(0)
      ).to.be.revertedWith("Service not active");
    });
  });

  describe("Service Completion", function () {
    beforeEach(async function () {
      await registry.connect(provider).registerService("Analysis", "Portfolio analysis", ethers.parseUnits("5", 6));
      await mockUSDC.connect(requester).approve(await registry.getAddress(), ethers.parseUnits("5", 6));
      await registry.connect(requester).requestService(0);
    });

    it("should not allow non-provider to complete", async function () {
      await expect(
        registry.connect(requester).completeService(0)
      ).to.be.revertedWith("Not the provider");
    });

    it("should track completion count", async function () {
      await registry.connect(provider).completeService(0);

      // Create another request
      await mockUSDC.connect(otherUser).approve(await registry.getAddress(), ethers.parseUnits("5", 6));
      await registry.connect(otherUser).requestService(0);
      await registry.connect(provider).completeService(1);

      const svc = await registry.services(0);
      expect(svc.completedCount).to.equal(2);
    });
  });

  describe("Multi-user Scenario", function () {
    it("should handle multiple providers and requesters", async function () {
      // Two providers register services
      await registry.connect(provider).registerService("Premium Analysis", "Deep analysis", ethers.parseUnits("10", 6));
      await registry.connect(otherUser).registerService("Quick Scan", "Fast check", ethers.parseUnits("2", 6));

      // Requester uses both services
      await mockUSDC.connect(requester).approve(await registry.getAddress(), ethers.parseUnits("12", 6));
      await registry.connect(requester).requestService(0); // Premium from provider
      await registry.connect(requester).requestService(1); // Quick from otherUser

      // Both providers complete
      const provBal1 = await mockUSDC.balanceOf(provider.address);
      await registry.connect(provider).completeService(0);
      expect(await mockUSDC.balanceOf(provider.address)).to.equal(provBal1 + ethers.parseUnits("10", 6));

      const otherBal1 = await mockUSDC.balanceOf(otherUser.address);
      await registry.connect(otherUser).completeService(1);
      expect(await mockUSDC.balanceOf(otherUser.address)).to.equal(otherBal1 + ethers.parseUnits("2", 6));
    });
  });
});
