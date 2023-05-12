# Lending Pool Simulation

This is a python mesa simulations of a lending pool allowing to simulated borrowers and lenders interacting with the contract as agents. The agents have a pseudo-random behaviour regarding on how much units and what coins to borrow or lend among the tokens included in the protocol.

This repository uses hardhat and a web3 wrapper in python as client to interact with the contract. The client allows to push and pull data from the state of the contract from the simulator.

Additonally, this repo provides a jupyter notebook within the client folder. This is using the same web3 client as the simulation, and helps to visualize the results before, during and after the simulation. 

The main reference of this repo can be found at the docs folder, in which different interest rate models for lending pools are explained in details. This simulations and solidity contract implements a simple linear interest rate model similar to AAVE but simpler. 

## Contract (Solidity) and Hardhat Node Setup

First clone this reposity from a terminal on your local machine. 

Install the npm dependencies using `npm install`. This will create `node_modules` folder in the repository.

After succesfully install `npm` dependencies, do `make node` which will start the hardhat node on your machine. 

Hardhat node should open a websocked JSON-RPC at `http://127.0.0.1:8545` by default.

```
npx hardhat node
Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/

Accounts
========

WARNING: These accounts, and their private keys, are publicly known.
Any funds sent to them on Mainnet or any other live network WILL BE LOST.

Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
Private Key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

Account #1: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 (10000 ETH)
Private Key: 0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d

Account #2: 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC (10000 ETH)
Private Key: 0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a

...
```
Hardhat node create until 20 accounts to play with. Be aware that the account provided by hardhat are HD i.e. deterministic, and you shoudln't use them for other purposed than testing. 

Now, open a second terminal, from which you will deploy the contract and its tokens. 

Do `make deploy`, which will compile and deploy the lending pool giving you back a contract address. This will create a text file 
`deployed_contract_address.txt` of the current contract address. This will be read by the python simulations later.

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
As before, be aware that the token addresses created above are completely random for testing purposes. This will create a set of text files that will be read later by the python simulation. Now the contract and its environment have been setup, and now it's time to setup the python mesa simulator

## Simulation Setup

Access to `client` folder and create a virtual environment `virtualenv env --python=python3.9` (3.9 works for me)

Enable the environment using `source env/bin/activate` 

Install the python requirements via `pip install -r requiremenets.txt` and wait and it finish succesfully.

At this point you can run the simulation either a single instance or a batch of them

To run a single instance do `run-simulation-single.sh` which will populate the local blockchain.

To run a batch of simulations do `run-simulation-batch.sh`

The two of the simulation executiosn will end up producing performance profile `svg` files

## Analysing and Monitoring the Results

Open a new terminal over the `client` folder, and enable as before the environment.

Run `jupyter notebook` to launch this server. 

Open the brower and run all cell to see the simulation results


