from web3 import Web3, AsyncWeb3
import pprint
import json

from token_wrapper import TokenWrapper

from helpers import print_receipt

# initialize drivers
rpc = 'http://127.0.0.1:8545'
w3 = Web3(Web3.HTTPProvider(rpc))

from setup_contracts import SetupContracts

class UserLendingPool:    
    def __init__(self,name, address):
        self.name = name
        self.address = address
        
    def __str__(self):
        return f"name='{self.name}'|address='{self.address}'"

    ## wallet of the user
    def get_balance_of_token(self, token): 
        token_name = token.functions.name().call()
        decimals   = token.functions.decimals().call()        
        return token.functions.balanceOf(self.address).call() // 10 ** decimals
            
class UserGenerator:
    def __init__(self):        
        self.names = ["Emma", "Olivia", "Ava",
                      "Isabella", "Sophia", "Mia",
                      "Charlotte", "Amelia", "Harper",
                      "Evelyn", "Abigail",
                      "Emily", "Elizabeth",
                      "Mila", "Ella", "Avery",
                      "Sofia", "Camila", "Aria",
                      "Scarlett"]
        
        self.current_index = 0
        self.num_accounts = len(w3.eth.accounts[0])
            
    def gen(self):
        print(f"w3 eth accounts available = {len(w3.eth.accounts)}")
        while True:
            n = self.current_index % self.num_accounts
            account = w3.eth.accounts[n]
            name = self.names[n % len(self.names)]
            yield UserLendingPool(name,account)
            self.current_index += 1

        
    
def print_user_data(user, user_data, DECIMALS):
    print(f"User: {user} | totalCollateral: {user_data[0] // decimals} DAIs",
          f"| totalBorrow: {user_data[1] // DECIMALS} DAIs")

def header(action, user, token, amount):
    DECIMALS = get_decimals(token)
    print(f"Action={action} the amount {amount } units from user address {user.address} ")
    print(f"token the {token.address}")

## add supply tokens to the pool
def print_action(actor, action, amount, token_address):
    print(f"{actor} is {action} an amount of {amount} units of the token address {token_address}")
    
def get_decimals(contract_token):
    decimals = contract_token.functions.decimals().call()
    #print(f"No. of decimals for token {token_name}: {decimals}")
    return 10 ** decimals 

def aprove(user, contract, token, amount):
    tx_hash = token.functions.approve(contract.address, amount).transact({'from':user.address})    

def log_in_out(func):
    def decorated_func(*args):
        print(">> ENTER", func.__name__)
        #print(args)
        header(func.__name__, args[0], args[2], args[3])
        result = func(*args)
        print("<< LEAVE", func.__name__)
        return result
    return decorated_func

@log_in_out
def supply(user, contract, token, amount, verbose=True):    
    print(" Amount to supply in units", amount)
    amount = int(amount * 1e18)
    print(" Amount to supply in weis", amount)
    
    aprove(user, contract, token, amount)
    contract.functions.supply(token.address,
                              amount).transact({'from':user.address})    

@log_in_out
def repay(user, contract, token, amount, verbose=True):
    aprove(user, contract, token, amount)
    contract.functions.repay(token.address, amount).transact({'from':user.address})

@log_in_out
def borrow(user, contract, token, amount, verbose=True):
    decimals = get_decimals(token)
    amount = int(decimals * amount)
    contract.functions.borrow(token.address, amount).transact({'from':user.address})

class ContractInterface:
    def __init__(self, user, contract):
        self.user = user
        self.contract = contract

    #def header_action(self, func):
    #    def wrapper():
    #        header("Supplying",  self.user, token, amount)                
        
    def supply(self, token, amount):
        supply(self.user, self.contract, token, amount)

    def withdraw(self, token, amount):
        pass

    def borrow(self, token, amount):
        borrow(self.user, self.contract, token, amount)
        
    def repay(self, token, amount):
        repay(self.user, self.contract, token, amount)

    def get_user_data(self): 
        supply, borrow = self.contract.functions.getUserData(self.user.address).call()
        unit_of_account = 1e18
        return {"totalCollateral":supply // unit_of_account,
                "totalBorrow":    borrow // unit_of_account}

    def get_token_vault(self,token_address, weis=False):
        ## vault returns (amount,shares) for both deposits and borrows
        return self.contract.functions.getTokenVault(token_address).call() 

    def get_total_assets_amount(self,token, weis=False):
        #factor = 10 ** token.functions.decimals().call() if weis else 1
        factor = 1e18 
        return self.contract.functions.getTokenTotalAssetsAmount(token.address).call() // factor
        
    def get_total_borrow_amount(self,token, weis=False):
        #factor = 10 ** token.functions.decimals().call() if weis else 1
        factor = 1e18 
        return self.contract.functions.getTokenTotalBorrowAmount(token.address).call() // factor
    
            

if __name__ == "__main__":

    ## test accounts given by the hardhat node
    ug = UserGenerator().gen()
    manager = next(ug) 
    leader = next(ug) 

    print(str(manager))
    print(str(leader))

    # get contract objects for the lending pool and test token
    setup = SetupContracts(manager)
    contract_lending_pool = setup.contract()
    tokens = setup.tokens()
    contract_token = tokens[0]

    # form token wrapper to get info
    token_wrapper = TokenWrapper(contract_token)
    token_name = token_wrapper.name 
    decimals = token_wrapper.decimals 
    
    # check token balance of the users
    for user in [manager, leader]:
        for token in tokens:
            token_wrapper = TokenWrapper(token)    
            token_name = token_wrapper.name 
            decimals = token_wrapper.decimals 
                    
            print(f"{user.name}'s balance of {token_name} is = ",
                user.get_balance_of_token(token))
            #print(f"No. of decimals for token {token_name}: {decimals}")
            
    DECIMALS = 10 ** decimals 

    # transfer some coins to a user
    units = 10
    token_wrapper.transfer_from_to(manager, leader, units) #amount_units_to_transfer)

    exit()
    #amount_to_transfer = units * DECIMALS

    #token_address = contract_token.address
    #print(f"Transfering {amount_to_transfer // DECIMALS} units of token ",
    #      f"{token_name} from {manager.name} to {leader.name}")
    
    #tx_hash = contract_token.functions.transfer(leader.address,
    #                                            amount_to_transfer).transact({'from': manager.address})
        
    #print(f"Manager's contract  balance for token {contract_token.address}",
    #      manager.get_balance_of_token(contract_token))
    #print(f"Leader's balance for token {contract_token.address}",
    #      leader.get_balance_of_token(contract_token))     
    #contract_token.functions.balanceOf(leader.address).call() // DECIMALS)

    ## supply require to approve for external transfers (contract)
    user     = manager
    contract = contract_lending_pool
    token    = contract_token
    units    = 100
    amount   = units * DECIMALS
    
    supply(user, contract,  token, amount)
    

    # amount = 10000 * DECIMALS
    # tx_hash = contract_token.functions.approve(manager.address,
    #                                            amount).transact({'from':manager.address})
    
    # token_price = contract_lending_pool.functions.getTokenPrice(token_address).call() #{'from':manager.address})
    # print(f"Current Token Price in DAIS {token_price}")

    # total_supply = contract_token.functions.totalSupply().call()
    # print(f"Total Supply of the token {token_name} is {total_supply // DECIMALS}")

    # #contract_token.functions.approve(contract_lending_pool.address,
    # #                                amount).transact({'from':manager.address})

    # allowance = contract_token.functions.allowance(manager.address,
    #                                                contract_lending_pool.address).call({'from':manager.address})
    
    # print(f"Allowance for the contract {contract_lending_pool.address}",
    #       f" to spend on behalf of user '{manager.name}':",
    #       allowance // DECIMALS," units")

    # contract_lending_pool.functions.supply(contract_token.address,
    #                                        amount).transact({'from':manager.address})
    #exit()

    #### checks user data
    user_data = contract_lending_pool.functions.getUserData(manager.address).call()
    print(f"Total collateral of user '{manager.name}' is ", user_data[0] // DECIMALS," Dai")

    ## Borrow
    user = manager
    contract = contract_lending_pool
    token = contract_token
    amount = 1000 * DECIMALS 
    borrow(user, contract, token, amount)

    #exit()
    
    # amount_to_borrow = 1000 * DECIMALS
    # print_action("Manager",
    #              "borrowing",
    #              amount_to_borrow // DECIMALS,
    #              contract_token.address)
    
    # tx_hash = contract_lending_pool.functions.borrow(contract_token.address,
    #                                                  amount_to_borrow).transact()
    # print_receipt(tx_hash, "borrow")
    

    # user_data = contract_lending_pool.functions.getUserData(manager.address).call()
    # print_user_data("manage", user_data)



    ## Repay
    user = manager
    contract = contract_lending_pool
    token = contract_token
    units = 2
    amount = units * DECIMALS
    repay(user, contract, token, amount)


    ## health factor
    print("Health Factor (3 good, less than 1 => liquidation) \n",
          contract_lending_pool.functions.healthFactor(manager.address).call() // DECIMALS ),


    # try to borrow without collateral
    user = leader.address
    user_data = contract_lending_pool.functions.getUserData(user).call()
    print_user_data("leader", user_data, DECIMALS)

    price = contract_lending_pool.functions.getTokenPrice(contract_token.address).call()

    amount_to_borrow = 2 * DECIMALS
    
    try:
        contract_lending_pool.functions.borrow(contract_token.address,
                                               amount_to_borrow).transact({'from':user})
        
    except Exception as e:
        print("Borrowing cannot be done without collateral",e,
              "\n This error can be safely ignored")

        ## TODO: Add collateral and retry


    ## CHECK INTEREST RATES
    print("Accruing Interest")
    contract_lending_pool.functions.accrueInterest(contract_token.address).transact()
    
    print(f"Check Interest Rates on the token {contract_token.address}")
    interest_rate = contract_lending_pool.functions.getTokenInterestRate(contract_token.address).call()
    print("Interest Rate Per Second",interest_rate)


    notFinish = True
    while notFinish:
        ## CHECK INTEREST RATES
        #print("Accruing Interest")
        tx_hash = contract_lending_pool.functions.accrueInterest(contract_token.address).transact() 
        #print_receipt(tx_hash, "accrueInterest")
       

        value = contract_lending_pool.functions.getTokenInterestRate(contract_token.address).call()
        print(f"Check Interest Rates Per Second of the token {contract_token.address} is {value} %")

        value = contract_lending_pool.functions.getTokenTotalAssetsAmount(contract_token.address).call()
        print(f"Check total Assets of the token {contract_token.address} are {value // DECIMALS} units ")

        value = contract_lending_pool.functions.getTokenTotalBorrowAmount(contract_token.address).call()
        print(f"Check total Borrow of the token {contract_token.address} are {value // DECIMALS} units ")
        
        notFinish = False
        
