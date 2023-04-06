from web3 import Web3, AsyncWeb3
import pprint
import json

#from entities import UserLendingPool
class UserLendingPool:
    def __init__(self,name, address):
        self.name = name
        self.address = address
    def __str__(self):
        return f"Name of user is '{self.name}' with address '{self.address}'"
    


## initialize w3 drivers locally
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

## aux functions
def print_receipt(tx_hash, topic):
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)    
    print(f"Transaction {topic} receipt mined:")
    #print(dict(receipt))
    print("Was transaction successful?", receipt["status"])
    
def print_user_data(user, user_data):
    print(f"{user} totalCollateral = {user_data[0] // DECIMALS} DAIs",
          f"| total Borrow {user_data[1] // DECIMALS} DAIs")

    
## build contract object from its abi
def get_contract_instance(path, address):
    abi = json.load(open(path))["abi"]
    return w3.eth.contract(address=address, abi=abi)


def add_supported_token_1(token_address,
                          contract_instance,
                          dummy_price_feed="0x1CBd3b2770909D4e10f157cABC84C7264073C9Ec"):
    tx_hash = contract_instance.functions.addSupportedToken(token_address,
                                                            dummy_price_feed).transact()
    print_receipt(tx_hash, "addSupportedToken")


## add supply tokens to the pool
def print_action(actor, action, amount, token_address):
    print(f"{actor} is {action} an amount of {amount} units of the token address {token_address}")


def setup_contracts(manager):
    print("Check w3 is connected?",w3.is_connected())
    info = w3.eth.get_block('latest')
    
    path_to_artifact_contracts = "../artifacts/contracts" 

    ## Read from file deployed contract address
    contract_lending_pool = None
    with open("../deployed_contract_address.txt","r") as f:
        contact_address = f.read()
        print("Latest Lending Pool Contract Address Deployed:",contact_address)
        path=f"{path_to_artifact_contracts}/LendingPool.sol/LendingPool.json"
        contract_lending_pool = get_contract_instance(path,contact_address)

    ### unpause the contract
    tx_hash = contract_lending_pool.functions.setPaused(2).transact({'from':manager.address})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    ## Read from file deployed token address
    contract_token = None
    with open("../deployed_token_address.txt","r") as f:
        token_address = f.read()
        path=f"{path_to_artifact_contracts}/mocks/ERC20Mock.sol/ERC20Mock.json"
        contract_token = get_contract_instance(path,token_address)

        try:
            add_supported_token_1(token_address,contract_lending_pool)
        except Exception as e:
            print(f"{e} This error can be safely ignored")
        
    return contract_lending_pool, contract_token
    


if __name__ == "__main__":

    ## test accounts given by the hardhat node
    manager = UserLendingPool("manager",w3.eth.accounts[0])
    alice = UserLendingPool("alice",w3.eth.accounts[1])

    print(str(manager))
    print(str(alice))

    #print("Manager's contract address: ",manager.address)
    #print("Alice's address: ",alice.address)

    # get the contract objects
    contract_lending_pool, contract_token = setup_contracts(manager)

    # token name
    token_name = contract_token.functions.name().call()

    # token decimals
    decimals = contract_token.functions.decimals().call()
    print(f"No. of decimals of the token {token_name}: {decimals}")
    DECIMALS = 10 ** decimals # get this from ERC20

    # check balance of the users on tokens
    print(f"Manager's contract  balance of {token_name} is ",
          contract_token.functions.balanceOf(manager.address).call() // DECIMALS)
    print(f"Alice's balance on token {token_name} is ",
          contract_token.functions.balanceOf(alice.address).call() // DECIMALS)

    # transfer some coins to a user
    amount_to_transfer = 10000


    #print(token_name)
    token_address = contract_token.address
    print(f"Transfering {amount_to_transfer} units of token {token_name} from {manager.name} to {alice.name}")
    tx_hash = contract_token.functions.transfer(alice.address,
                                                amount_to_transfer * DECIMALS).transact({'from': manager.address})
    
    
    print(f"Manager's contract  balance for token {contract_token.address}",
          contract_token.functions.balanceOf(manager.address).call() // DECIMALS)
    print(f"Alice's balance for token {contract_token.address}",
          contract_token.functions.balanceOf(alice.address).call() // DECIMALS)
    

    ## supply require to approve for external transfers (contract)
    amount = 100 * DECIMALS
    tx_hash = contract_token.functions.approve(manager.address,amount).transact({'from':manager.address})
    
    token_price = contract_lending_pool.functions.getTokenPrice(token_address).call() #{'from':manager.address})
    print(f"Current Token Price {token_price}")

    total_supply = contract_token.functions.totalSupply().call()
    print(f"Total Supply of the token {token_name} is {total_supply // DECIMALS}")

    contract_token.functions.approve(contract_lending_pool.address,
                                    amount).transact({'from':manager.address})


    allowance = contract_token.functions.allowance(manager.address,
                                                   contract_lending_pool.address).call({'from':manager.address})
    
    print(f"Allowance for the contract {contract_lending_pool.address} to spend on behalf of user '{manager.name}':",
          allowance // DECIMALS," units")


    interest_rate = contract_lending_pool.functions.getTokenInterestRate(contract_token.address).call()
    print(f"Current interest rate of token {contract_token.address} =",interest_rate)






    contract_lending_pool.functions.supply(contract_token.address,
                                           amount).transact({'from':manager.address})


    #### checks user data
    user_data = contract_lending_pool.functions.getUserData(manager.address).call()
    print(f"Total collateral of user {manager.address}", user_data[0] // DECIMALS," Dai")

    amount_to_borrow = int(2.5 * DECIMALS)
    print_action("Manager",
                 "borrowing",
                 amount_to_borrow // DECIMALS,
                 contract_token.address)
    
    tx_hash = contract_lending_pool.functions.borrow(contract_token.address, amount_to_borrow).transact()
    print_receipt(tx_hash, "borrow")
    

    user_data = contract_lending_pool.functions.getUserData(manager.address).call()
    #print(user_data)
    print_user_data("manage", user_data)


    
    user = alice.address
    user_data = contract_lending_pool.functions.getUserData(user).call()

    print_user_data("alice", user_data)



    price = contract_lending_pool.functions.getTokenPrice(contract_token.address).call()

    # try to borrow without collateral
    try:
        contract_lending_pool.functions.borrow(contract_token.address, amount_to_borrow).transact({'from':user})
    except Exception as e:
        print("Borrowing cannot be done without collateral",e)

        ## TODO: Add collateral and retry



    ## Repay
    def repay(user, contract, token, amount):
        print(f"Repaying {amount} from {user.name} on token {token.address}")
        tx_hash = token.functions.approve(contract.address,amount).transact({'from':user.address})
        contract.functions.repay(token.address, amount).transact({'from':user.address})    
        user_data = contract.functions.getUserData(user.address).call()
        print_user_data(user.name, user_data)

        
    repay(manager, contract_lending_pool, contract_token, 2 * DECIMALS)

    print("Health Factor (3 good, less than 1 => liquidation) \n",
          contract_lending_pool.functions.healthFactor(manager.address).call() // DECIMALS / 100),
    
