import { ethers } from "hardhat";
import { readFileSync, writeFileSync } from 'fs';

import { syncWriteFile } from "./utils.ts"

async function main() {

    // Get the contract owner
    const contractOwner = await ethers.getSigners();
    console.log(`Deploying contract from: ${contractOwner[0].address}`);
    
    const ERC20Mock = await ethers.getContractFactory("ERC20Mock");

    // Deploy the contract
    console.log('Deploying ERC20Mock...');
    const erc20Mock = await ERC20Mock.deploy();
    await erc20Mock.deployed();
    console.log(`Erc20Mock deployed to: ${erc20Mock.address}`)

    syncWriteFile('../deployed_token_address.txt', erc20Mock.address);    

}


// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
