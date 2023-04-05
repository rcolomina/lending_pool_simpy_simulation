from web3 import Web3, AsyncWeb3
import pprint
import json
    
## initialize w3 drivers locally
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

## aux functions
def print_receipt(tx_hash):
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)    
    print("Transaction receipt mined:")
    print(dict(receipt))
    print("\nWas transaction successful?")
    print(receipt["status"])

    
## build contract object from its abi
def get_contract_instance(path, address):
    abi = json.load(open(path))["abi"]
    return w3.eth.contract(address=address, abi=abi)


def add_supported_token_1(token_address,
                          contract_instance,
                          dummy_price_feed="0x1CBd3b2770909D4e10f157cABC84C7264073C9Ec"):
    tx_hash = contract_instance.functions.addSupportedToken(token_address,
                                                            dummy_price_feed).transact()
    print_receipt(tx_hash)


## add supply tokens to the pool
def print_action(actor, action, amount, token_address):
    print(f"{actor} is {action} an amount of {amount} of the token {token_address}")


def setup_contracts(owner):
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
    tx_hash = contract_lending_pool.functions.setPaused(2).transact({'from':owner})
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
            print("WARNING! ",e)
            print("this error can be ignored")
        
    return contract_lending_pool, contract_token
    




if __name__ == "__main__":

    ## accounts given by hardhat
    owner = w3.eth.accounts[0]
    alice = w3.eth.accounts[1]

    print("Owner's address: ",owner)
    print("Alice's address: ",alice)

    # get contracts
    contract_lending_pool, contract_token = setup_contracts(owner)

    decimals = contract_token.functions.decimals().call()
    print(f"No. of decimals of the token: {decimals}")

    DECIMALS = 10 ** decimals # get this from ERC20

    print("Owner's balance",contract_token.functions.balanceOf(owner).call() // DECIMALS)
    print("Alice's balance",contract_token.functions.balanceOf(alice).call() // DECIMALS)

    amount_to_transfer = 10000

    tx_hash = contract_token.functions.transfer(alice, amount_to_transfer * DECIMALS).transact({'from': owner})
    
    #tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    #//contract_token.functions.balanceOf(alice).call()
    #contract_token.functions.balanceOf(owner).call()

    print("after transaction")
    
    print(f"Owner's balance for token {contract_token.address}",
          contract_token.functions.balanceOf(owner).call() // DECIMALS)
    print(f"Alice's balance for token {contract_token.address}",
          contract_token.functions.balanceOf(alice).call() // DECIMALS)
    

    ## supply with require to approve for external transfers (contract)

    token_address = contract_token.address
    print(f"Token Address {token_address}")

    amount = 100 
    tx_hash = contract_token.functions.approve(owner,amount).transact({'from':owner})
    
    user_data = contract_lending_pool.functions.getTokenPrice(token_address).call({'from':owner})
    print("Token Price", user_data)

    total_supply = contract_token.functions.totalSupply().call()
    print(f"Total Supply of the token {token_address} is {total_supply // DECIMALS}")

    
    contract_token.functions.approve(contract_lending_pool.address,
                                    amount).transact({'from':owner})


    allowance = contract_token.functions.allowance(owner,
                                                   contract_lending_pool.address).call({'from':owner})
    print(f"Allowance after for spender {contract_lending_pool.address} on behalf of owner {owner}:",
          allowance // DECIMALS)
        
    contract_lending_pool.functions.supply(contract_token.address,
                                           amount).transact({'from':owner})
    #### checks user data
    user_data = contract_lending_pool.functions.getUserData(owner).call() #transact({'from':owner})
    print(f"Total collateral of user {owner}", user_data[0]) # // DECIMALS)
    #print_receipt(tx_hash)
    exit()
    #print(f"Owner of the contract {owner} user data: {user_borrows}")

    


    #borrow
    amount_to_borrow = 100
    print_action("Owner","borrowing",amount_to_borrow, contract_token.address)
    tx_hash = contract_lending_pool.functions.borrow(contract_token.address, amount_to_borrow).call()    
    print_receipt(tx_hash)
    #tx_hash = contract_lending_pool.functions.borrow(contract_token.address, amount_to_borrow).call()

    ### get user token borrow
    user = owner
    user_borrows = contract_lending_pool.functions.getUserData(user).call()
    print(f"Owner of the contract {user} user data: {user_borrows}")

    
    user = alice
    user_borrows = contract_lending_pool.functions.getUserData(user).call()
    print(f"Alice address {user} user data:  {user_borrows}")


    price = contract_lending_pool.functions.getTokenPrice(contract_token.address).call()
    print("price",price)
    
    #receipt = w3.eth.wait_for_transaction_receipt(tx_hash)    
    #print(receipt)
    #print(f"Token Price {contract_token.address} price is {token_price}")
    
    #receipt = w3.eth.getTransactionReceipt(tx_hash)
    #logs = contract_lending_pool.events.myEvent().processReceipt(receipt)


    #print(#logs)
    #print(uint256_bytes)
    
    #uint256_int = int.from_bytes(uint256_bytes, byteorder="big")
    #print(uint256_int)
    #hexstring = Web3.to_hex(uint256_bytes)
    #print(hexstring)

    #a_string = bytes.fromhex(hexstring)
    #a_string = a_string.decode("ascii")
    #print(a_string)

    print(contract_lending_pool.functions)
    
    exit()
    
    import codecs
    uint256_bytes = codecs.decode(uint256_str[2:], 'hex')
    uint256_int = int.from_bytes(uint256_bytes, 'big')
    print(uint256_int)
    
    #print(f"Total Dai of user {user} is {totalInDai}")


