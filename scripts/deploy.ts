import { syncWriteFile } from "./utils.ts"

import { ethers, upgrades } from "hardhat";

async function main() {

    const LendingPool = await ethers.getContractFactory("LendingPool");

    console.log("Deploying LendingPool..");

    
    const lendingPool = await LendingPool.deploy();

    await lendingPool.deployed();
    console.log("LendingPool deployed to:", lendingPool.address);

    syncWriteFile('../deployed_contract_address.txt', lendingPool.address);    
    
}


// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
