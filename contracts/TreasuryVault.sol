// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title TreasuryVault
 * @notice A treasury vault where the principal is locked and only yield is accessible.
 * @dev Designed for autonomous AI agents that fund themselves from DeFi yield.
 *      The agent deposits funds, stakes in yield protocols, and can only withdraw
 *      the yield (interest earned), never the principal.
 */
contract TreasuryVault is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // --- State ---
    address public agent;                    // The AI agent's wallet
    uint256 public totalDeposited;           // Total principal deposited (locked)
    uint256 public totalYieldHarvested;      // Cumulative yield withdrawn
    uint256 public totalSpent;               // Total spent by agent from yield

    // Spending guardrails
    uint256 public maxPerTransaction;        // Max spend per single tx
    uint256 public maxDailySpend;            // Max spend per day
    mapping(uint256 => uint256) public dailySpent; // day number => amount spent

    // Supported yield tokens
    IERC20 public depositToken;              // e.g., USDC
    IERC20 public yieldToken;                // e.g., stETH or aUSDC

    // --- Events ---
    event Deposited(address indexed depositor, uint256 amount, uint256 timestamp);
    event YieldHarvested(uint256 yieldAmount, uint256 timestamp);
    event AgentSpent(address indexed to, uint256 amount, string reason, uint256 timestamp);
    event GuardrailsUpdated(uint256 maxPerTx, uint256 maxDaily);
    event AgentUpdated(address indexed oldAgent, address indexed newAgent);

    // --- Errors ---
    error OnlyAgent();
    error ExceedsTransactionLimit(uint256 requested, uint256 limit);
    error ExceedsDailyLimit(uint256 requested, uint256 remaining);
    error InsufficientYield(uint256 requested, uint256 available);
    error ZeroAmount();

    modifier onlyAgent() {
        if (msg.sender != agent) revert OnlyAgent();
        _;
    }

    constructor(
        address _agent,
        address _depositToken,
        address _yieldToken,
        uint256 _maxPerTransaction,
        uint256 _maxDailySpend
    ) Ownable(msg.sender) {
        agent = _agent;
        depositToken = IERC20(_depositToken);
        yieldToken = IERC20(_yieldToken);
        maxPerTransaction = _maxPerTransaction;
        maxDailySpend = _maxDailySpend;
    }

    /**
     * @notice Deposit funds into the treasury (locks principal)
     * @param amount Amount of deposit token to lock
     */
    function deposit(uint256 amount) external nonReentrant {
        if (amount == 0) revert ZeroAmount();

        depositToken.safeTransferFrom(msg.sender, address(this), amount);
        totalDeposited += amount;

        emit Deposited(msg.sender, amount, block.timestamp);
    }

    /**
     * @notice Get the available yield (total balance minus locked principal)
     * @return Available yield the agent can spend
     */
    function getAvailableYield() public view returns (uint256) {
        uint256 currentBalance = depositToken.balanceOf(address(this));
        if (currentBalance <= totalDeposited) return 0;
        return currentBalance - totalDeposited;
    }

    /**
     * @notice Get yield from yield-bearing token
     * @return Available yield token balance
     */
    function getYieldTokenBalance() public view returns (uint256) {
        return yieldToken.balanceOf(address(this));
    }

    /**
     * @notice Agent harvests available yield
     * @param amount Amount of yield to harvest
     */
    function harvestYield(uint256 amount) external onlyAgent nonReentrant {
        uint256 available = getAvailableYield();
        if (amount > available) revert InsufficientYield(amount, available);
        if (amount == 0) revert ZeroAmount();

        totalYieldHarvested += amount;
        depositToken.safeTransfer(agent, amount);

        emit YieldHarvested(amount, block.timestamp);
    }

    /**
     * @notice Agent spends from its yield balance (with guardrails)
     * @param to Recipient address
     * @param amount Amount to spend
     * @param reason Human-readable reason for the spend
     */
    function spend(
        address to,
        uint256 amount,
        string calldata reason
    ) external onlyAgent nonReentrant {
        if (amount == 0) revert ZeroAmount();
        if (amount > maxPerTransaction)
            revert ExceedsTransactionLimit(amount, maxPerTransaction);

        uint256 today = block.timestamp / 1 days;
        uint256 remainingDaily = maxDailySpend - dailySpent[today];
        if (amount > remainingDaily)
            revert ExceedsDailyLimit(amount, remainingDaily);

        uint256 available = getAvailableYield();
        if (amount > available) revert InsufficientYield(amount, available);

        dailySpent[today] += amount;
        totalSpent += amount;
        depositToken.safeTransfer(to, amount);

        emit AgentSpent(to, amount, reason, block.timestamp);
    }

    /**
     * @notice Get the locked principal (never withdrawable by agent)
     */
    function getPrincipal() external view returns (uint256) {
        return totalDeposited;
    }

    /**
     * @notice Get remaining daily spend allowance
     */
    function getRemainingDailyAllowance() external view returns (uint256) {
        uint256 today = block.timestamp / 1 days;
        if (dailySpent[today] >= maxDailySpend) return 0;
        return maxDailySpend - dailySpent[today];
    }

    /**
     * @notice Get full treasury status
     */
    function getStatus() external view returns (
        uint256 principal,
        uint256 availableYield,
        uint256 yieldTokenBal,
        uint256 cumulativeYieldHarvested,
        uint256 cumulativeSpent,
        uint256 dailyRemaining
    ) {
        uint256 today = block.timestamp / 1 days;
        return (
            totalDeposited,
            getAvailableYield(),
            getYieldTokenBalance(),
            totalYieldHarvested,
            totalSpent,
            dailySpent[today] >= maxDailySpend ? 0 : maxDailySpend - dailySpent[today]
        );
    }

    // --- Admin Functions ---

    function updateGuardrails(
        uint256 _maxPerTransaction,
        uint256 _maxDailySpend
    ) external onlyOwner {
        maxPerTransaction = _maxPerTransaction;
        maxDailySpend = _maxDailySpend;
        emit GuardrailsUpdated(_maxPerTransaction, _maxDailySpend);
    }

    function updateAgent(address _newAgent) external onlyOwner {
        emit AgentUpdated(agent, _newAgent);
        agent = _newAgent;
    }
}
