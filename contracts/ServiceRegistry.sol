// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title ServiceRegistry
 * @notice A marketplace where AI agents register services and get paid via micropayments.
 * @dev Agents register services with a price, users pay to request services,
 *      and agents complete them to receive payment. On-chain service economy.
 */
contract ServiceRegistry is ReentrancyGuard {
    using SafeERC20 for IERC20;

    IERC20 public paymentToken; // e.g., USDC

    struct Service {
        uint256 id;
        address provider;
        string name;
        string description;
        uint256 price;       // in payment token units
        bool active;
        uint256 completedCount;
    }

    struct ServiceRequest {
        uint256 id;
        uint256 serviceId;
        address requester;
        address provider;
        uint256 price;
        bool completed;
        bool refunded;
        uint256 requestedAt;
        uint256 completedAt;
    }

    uint256 public nextServiceId;
    uint256 public nextRequestId;

    mapping(uint256 => Service) public services;
    mapping(uint256 => ServiceRequest) public requests;
    mapping(address => uint256[]) public providerServices;
    mapping(address => uint256[]) public userRequests;

    // --- Events ---
    event ServiceRegistered(uint256 indexed serviceId, address indexed provider, string name, uint256 price);
    event ServiceRequested(uint256 indexed requestId, uint256 indexed serviceId, address indexed requester, uint256 price);
    event ServiceCompleted(uint256 indexed requestId, uint256 indexed serviceId, address indexed provider);
    event ServiceDeactivated(uint256 indexed serviceId);

    constructor(address _paymentToken) {
        paymentToken = IERC20(_paymentToken);
    }

    /**
     * @notice Register a new service
     * @param name Service name
     * @param description What the service does
     * @param price Price in payment tokens
     */
    function registerService(
        string calldata name,
        string calldata description,
        uint256 price
    ) external returns (uint256 serviceId) {
        serviceId = nextServiceId++;
        services[serviceId] = Service({
            id: serviceId,
            provider: msg.sender,
            name: name,
            description: description,
            price: price,
            active: true,
            completedCount: 0
        });
        providerServices[msg.sender].push(serviceId);

        emit ServiceRegistered(serviceId, msg.sender, name, price);
    }

    /**
     * @notice Request a service (pays upfront, held in escrow)
     * @param serviceId The service to request
     */
    function requestService(uint256 serviceId) external nonReentrant returns (uint256 requestId) {
        Service storage svc = services[serviceId];
        require(svc.active, "Service not active");

        paymentToken.safeTransferFrom(msg.sender, address(this), svc.price);

        requestId = nextRequestId++;
        requests[requestId] = ServiceRequest({
            id: requestId,
            serviceId: serviceId,
            requester: msg.sender,
            provider: svc.provider,
            price: svc.price,
            completed: false,
            refunded: false,
            requestedAt: block.timestamp,
            completedAt: 0
        });
        userRequests[msg.sender].push(requestId);

        emit ServiceRequested(requestId, serviceId, msg.sender, svc.price);
    }

    /**
     * @notice Provider completes a service request and receives payment
     * @param requestId The request to complete
     */
    function completeService(uint256 requestId) external nonReentrant {
        ServiceRequest storage req = requests[requestId];
        require(msg.sender == req.provider, "Not the provider");
        require(!req.completed, "Already completed");
        require(!req.refunded, "Already refunded");

        req.completed = true;
        req.completedAt = block.timestamp;
        services[req.serviceId].completedCount++;

        paymentToken.safeTransfer(req.provider, req.price);

        emit ServiceCompleted(requestId, req.serviceId, req.provider);
    }

    /**
     * @notice Get all active services
     */
    function getActiveServiceCount() external view returns (uint256 count) {
        for (uint256 i = 0; i < nextServiceId; i++) {
            if (services[i].active) count++;
        }
    }

    /**
     * @notice Deactivate a service
     */
    function deactivateService(uint256 serviceId) external {
        require(services[serviceId].provider == msg.sender, "Not provider");
        services[serviceId].active = false;
        emit ServiceDeactivated(serviceId);
    }
}
