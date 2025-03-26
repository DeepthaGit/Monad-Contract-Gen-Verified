// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

contract Counter {
    uint256 public count;

    // Set the counter using inline assembly.
    // Directly writes to the storage slot.
    function set(uint256 newCount) external {
        assembly {
            sstore(count.slot, newCount)
        }
    }

    // Increment the counter using inline assembly.
    // This avoids the automatic overflow check.
    function increment() external {
        assembly {
            let current := sload(count.slot)
            sstore(count.slot, add(current, 1))
        }
    }
}
