import mesa

import random
random.seed(42)

from agent_models import get_percentage_on_amount_to_deposit

from integration_test import UserGenerator
from integration_test import SetupContracts
from integration_test import ContractInterface

from agent_models import RiskTolerance as rt
from agent_models import MarketDirectionBelieve as mdb

from interest_rate_models import get_interest_rate

from user_agent import UserAgent

from enums import Token

import pandas as pd



class LendingPlatform(mesa.Model):
    def __init__(self, n_users, n_coins, airdrop):

        ## Generate the users        
        self.num_agents = n_users
        self.num_coins  = n_coins
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True

        ## Set a manager for the platfrom
        ug = UserGenerator().gen()
        self.manager = next(ug)

        ## Setup tokens (Dai, ...)
        self.contract, self.tokens = self._setup_tokens()

        ## token contracts
        self.token               = self.tokens[0]
        self.token_dai           = self.tokens[0]
        self.token_ruben_coin    = self.tokens[1]
        self.token_almanak_coin  = self.tokens[2]

        ## token addresses
        self.token_dai_addr           = self.tokens[0].address
        self.token_ruben_coin_addr    = self.tokens[1].address
        self.token_almanak_coin_addr  = self.tokens[2].address

        ## Airdrop  this is an example based on hardhat distribution on the tokens manager
        initial = 1000
        self.airdrop_units_per_token = initial + airdrop * 100 

        ## Store interset rate
        self.interest_rate_borrowings = {} 
        self.interest_rate_savings = {} 

        ## make initial deposit from the manager
        self.contract_interface = ContractInterface(self.manager, self.contract)

        print("Lending Pool User Data of the Contract Manager",
              self.contract_interface.get_user_data())
        
        # volatilty of dai 0.1, vol. of eth 10
        ## TODO: Set this on the contract
        #init_eth_price = 1800 # in units of dai        
        self.market_conditions = {} # {Token.Eth :{"price": 1800,"volatility":10}}
        
        ## ADD AGENTS TO THE SCHEDULE
        self.agents = self._setup_users()

        ## write down agents for analysis
        data = [{"id":u.unique_id,
                 "name":u.user_name,"address":u.user_address,
                 "risk_tolerance":u.risk_tolerance,
                 "market":u.market_direction_believe,
                 "interest_preferece":u.interest_rate_preference} for u in self.agents]
        
        df = pd.DataFrame(data)
        ofname_for_agents = "lending-pool-agents.csv"
        df.to_csv(ofname_for_agents)

        ## data collector for mesa batch running
        model_reporters = {"Interest-Rates-Borrowins":"interest_rate_borrowings",
                           "Interest-Rates-Savings":"interest_rate_savings",
                           "AddressDai":"token_dai_addr",
                           "AddressRubenCoin":"token_ruben_coin_addr",
                           "AddressAlmanakCoin":"token_almanak_coin_addr"}


        self.datacollector = mesa.DataCollector(model_reporters = model_reporters, 
                                                agent_reporters = {"Borrowed":"total_borrowed",
                                                                   "Deposited":"total_deposited"})

        for agent in self.agents:
            self.schedule.add(agent)
        
    def step(self):
        # go through tokens changines its prices
        #for k,v in self.market_conditions.items():
        #    print(k,v)        
        #    self._change_price(self.etoken)
        self.datacollector.collect(self)
                                  
        self._update_interset_rate()
        self._liquidate_agents()
        self.schedule.step()

        ### remove
        for agent in self.agents:
            agent.repay_borrows()
            agent.remove_collateral()

    def _transferring_funds_to_user(self,token,
                                    user_lending_pool,
                                    units_to_transfer=1000):

        ## Transfer coins from manager (issuer) to the list of protocol users
        from integration_test import TokenWrapper
        token_wrapper = TokenWrapper(token)
        if self.manager.name != user_lending_pool.name:
            # if target has less than units_to_transfer transfer the rest
            user_balance = token_wrapper.get_balance_of_user(user_lending_pool)
            name = user_lending_pool.name
            if user_balance < units_to_transfer:
                balance_diff = units_to_transfer - user_balance
                token_wrapper.transfer_from_to(self.manager,
                                               user_lending_pool,
                                               balance_diff)
                
                print(f"Transferred done of {balance_diff} on user {name}")
            else:
                print(f"No transfer done for user {name}." + \
                      f" Token balance {token.address} is already {user_balance} units")


    def _setup_users(self):
        # create and set initial conditions for each agent
        
        agents = []
        
        ug = UserGenerator().gen()

        ### INITIAL AIRDROP of the coins to all the users
        starting_units = self.airdrop_units_per_token 
        target_tokens = [(self.token_dai,           starting_units),
                         (self.token_almanak_coin,  starting_units),
                         (self.token_ruben_coin,    starting_units)]
        
        for user_index in range(self.num_agents):                                                
            user_lending_pool = next(ug)            
    
            for token_and_amount in target_tokens:
                token_to_transfer  = token_and_amount[0]
                units_to_transfer  = token_and_amount[1]
                
                ## TRANSFER TOKENS TO USERS TO PLAY WITH                                        
                self._transferring_funds_to_user(token_to_transfer,
                                                 user_lending_pool,
                                                 units_to_transfer)

            agent = UserAgent(user_index, self,user_lending_pool)
            agents.append(agent)
            
        return agents

    def _setup_tokens(self):
                
        setup    = SetupContracts(self.manager)
        contract = setup.contract()
        tokens   = setup.tokens()

        return contract, tokens

    
    def _change_price(self, token):

        current_price = self.market_conditions[token]["price"]
        volatility    = self.market_conditions[token]["volatility"]
        
        new_price = change_price_token_model(current_price, volatity) 

        print(f"New price for {token}", new_price)
        self.market_conditions[Token] = {token:{"price": current_price,
                                                "volatility": 10}}
                
    def _update_interset_rate(self):
        contract_interface = ContractInterface(self.manager, self.contract)

        ## UPDATE ALL COINS
        for token in self.tokens:
            self._update_interset_rate_on_token(token)

        def print_items(d):
            for k,v in d.items():
                print(k,v)
                
        print("Borrowings Interest Rates")
        print_items(self.interest_rate_borrowings)
        
        print("Savings Interest Rates")
        print_items(self.interest_rate_savings)



    def _update_interset_rate_on_token(self, token):

        deposits = self.contract_interface.get_total_assets_amount(token)        
        loans = self.contract_interface.get_total_borrow_amount(token)
        
        print(f"Total of (Deposits, Loands) = ({deposits},{loans}) for token {token.address}")

        interest_rate_on_borrowings = get_interest_rate(deposits,loans,
                                                        type_interest = "borrowings")

        interest_rate_on_savings = get_interest_rate(deposits,loans,
                                                     type_interest = "savings")

        self.interest_rate_borrowings[token.address] = interest_rate_on_borrowings 
        self.interest_rate_savings[token.address]    = interest_rate_on_savings


    def _liquidate_agents(self):
        # TODO: Go through out all the agents seeing whether conditions for liquidatioan are met
        for agent in self.agents:
            account = agent.user_address
            health_factor = self.contract.functions.healthFactor(account).call() // 1e18
            print("Calculate Health Factor =", health_factor)
            
            #self.contract.functions.liquidate(account, collateral, user_borrow_token, amount_to_liquidate).transact
        

