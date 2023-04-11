// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract ERC20RubenCoin is ERC20 {
        constructor() ERC20("RubenCoin", "RUC") { 
        
        uint256 initial_supply = 1e6;
        
        uint256 unit_of_account = 1e18; // convert to wei
        
        _mint(msg.sender, initial_supply * unit_of_account); 
    }

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }

    function burn(uint256 amount) external {
        _burn(address(this), amount);
    }
}
