// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract Vault {
    event RewardPaid(address indexed to, uint256 amount);

    // Stub: simulate reward payout
    function payReward(address to, uint256 amount) external {
        // TODO: Integrate with ERC-20 token logic
        emit RewardPaid(to, amount);
    }
} 