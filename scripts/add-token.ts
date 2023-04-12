import { ethers } from "hardhat";
import { readFileSync, writeFileSync } from 'fs';

import { syncWriteFile } from "./utils.ts"

async function main() {

    const contractOwner = await ethers.getSigners();

    console.log(`Deploying contract from contract owner: ${contractOwner[0].address}`);

    ////
    const ERC20Dai = await ethers.getContractFactory("ERC20Dai");
    
    console.log('Deploying ERC20Dai...');
    const erc20Dai = await ERC20Dai.deploy();
    await erc20Dai.deployed();
    console.log(`Erc20Dai deployed to: ${erc20Dai.address}`)

    syncWriteFile('../deployed_token_address_dai.txt',
                  erc20Dai.address);    

    ////    
    const ERC20RubenCoin = await ethers.getContractFactory("ERC20RubenCoin");
    
    console.log('Deploying ERC20RubenCoin...');
    const erc20RubenCoin = await ERC20RubenCoin.deploy();
    await erc20RubenCoin.deployed();
    console.log(`Erc20RubenCoin deployed to: ${erc20RubenCoin.address}`)

    syncWriteFile('../deployed_token_address_ruben_coin.txt',
                  erc20RubenCoin.address);    

    ////    
    const ERC20AlmanakCoin = await ethers.getContractFactory("ERC20AlmanakCoin");
    
    console.log('Deploying ERC20AlmanakCoin...');
    const erc20AlmanakCoin = await ERC20AlmanakCoin.deploy();
    await erc20AlmanakCoin.deployed();
    console.log(`Erc20AlmanakCoin deployed to: ${erc20AlmanakCoin.address}`)

    syncWriteFile('../deployed_token_address_almanak_coin.txt',
                  erc20AlmanakCoin.address);    
    
}


// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
