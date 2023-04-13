# Lending Pool Simpy Simulation

This is a python mesa simulation integrated along with a lending pool contract solidity contract. The setup uses hardhat and web3 wrapper python client to interact, change and monitor the state of contract.

## Setup

First clone this reposity from a terminal on your local machine. 

Install the npm dependencies using `npm install`. This will create `node_modules` folder in the repository.

After succesfully install `npm`, do `make node` which will start the hardhat node on your. The node should open a websocked JSON-RPC at `http://127.0.0.1:8545` by default.

Now, open a second terminal from which you will deploy the contract and the tokens.

Do `make deploy`, which will compile and deploy the lending pool giving you back a contract address. This will create a text file `deployed_contract_address.txt` of the current contract address. This will be read by the python simulations later.

Now, do `make add-tokens`, which should add the tokens that the contract will have available for borrowing and lending. 
```
~/lending_pool_simpy_simulation$ make add-tokens
npx hardhat run --network localhost scripts/add-token.ts
Deploying contract from contract owner: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
Deploying ERC20Dai...
Erc20Dai deployed to: 0x3A25408D952F91e42F39587820bEe5f051f4556c
0x3A25408D952F91e42F39587820bEe5f051f4556c
Deploying ERC20RubenCoin...
Erc20RubenCoin deployed to: 0xA6407325fF7DAAB36D20992dADC031c82D1C4390
0xA6407325fF7DAAB36D20992dADC031c82D1C4390
Deploying ERC20AlmanakCoin...
Erc20AlmanakCoin deployed to: 0xE65B75e7A8de220bcfec86F58c4c25A62aB7CD9b
0xE65B75e7A8de220bcfec86F58c4c25A62aB7CD9b

```

This will create a set of text files that will be read later by the python simulation


