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

from helpers import get_risk_tolerance
from helpers import get_market_direction_believe


class LendingPlatform(mesa.Model):
    def __init__(self, N):

        ## Generate the users        
        self.num_agents = N
        self.schedule = mesa.time.RandomActivation(self)

        ## Set a manager for the platfrom
        ug = UserGenerator().gen()
        self.manager = next(ug)

        ## Setup tokens (Dai, Eth,...)
        self.contract, self.tokens = self._setup_tokens()
        self.token     = self.tokens[0]
        
        self.token_dai           = self.tokens[0]
        self.token_ruben_coin    = self.tokens[1]
        self.token_alamanak_coin = self.tokens[2]
        
        #self.token_eth = self.toekn

        ## Setup contract manager

        ## TODO: Set user on the contract
        ## define initial conditions of the lending platform
        
        ## TODO: set tokens Dai, Eth and Btc on the contracts
        self.deposited = {Token.Dai: 1000000, Token.Eth: 50000}
        
        self.borrowed  = {Token.Dai:  500000, Token.Eth: 25000}

        ## make initial deposit from the manager
        self.contract_interface = ContractInterface(self.manager,
                                                    self.contract)

        ## supply base amount of tokns by the manager
        amount_to_deposit = 10 # units to deposit to the contract
        self.contract_interface.supply(self.token_dai,
                                       amount_to_deposit)

        print("Lending Pool Manager Data", self.contract_interface.get_user_data())

        token_vault = self.contract.functions.getTokenVault(self.token_dai.address).call()
        
        print(f"TOKEN VAULT INFO from {self.token_dai.address} = {token_vault}")
        print(" -Assets 1", token_vault[0][0] // 1e18)
        print(" -Assets 2", token_vault[0][1] // 1e18)
        print(" -Borrows 1&2", token_vault[1])
        print(" -Interest Rate Info 2", token_vault[2])

        
        # volatilty of dai 0.1, vol. of eth 10
        ## TODO: Set this on the contract
        init_eth_price = 1800 # in units of dai        
        self.market_conditions = {Token.Eth :{"price": 1800,
                                              "volatility":10}}
        
        self.agents = self._setup_users()
        for agent in self.agents:
            self.schedule.add(agent)
        
    def step(self):
        # go through tokens change price
        for k,v in self.market_conditions.items():
            print(k,v)        
            #self._change_price(self.etoken)
                                  
        self._update_interset_rate()
        self.schedule.step()

    def _transferring_funds_to_user(self,token, user_lending_pool, units_to_transfer=10000):


        ## Transfer Dai coin from manager (issuer) to the list of user
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
                print(f"No transfer done on user {name}. Balance is already {user_balance}")
        
        ## TODO: transfer funds from other coins


    def _setup_users(self):
        agents = []
        # create and set initial conditions for each agent
        # TODO: make this more interesting
        
        ug = UserGenerator().gen()

        for user_index in range(self.num_agents):                                                
            user_lending_pool = next(ug)            

            ## TRANSFER DAI TO USER
            units_to_transfer = 10000            
            token = self.token_dai            
            self._transferring_funds_to_user(token,
                                              user_lending_pool,
                                              units_to_transfer)
            
            total_user_dai = user_lending_pool.get_balance_of_token(self.token)
            #print(f"Balance of user {user_lending_pool.name} on dai is {total_user_dai}")
                  
            ## TODO: Transfer other coins to the user
            total_user_eth = 10000

                        
            wallet = {Token.Dai:total_user_dai,
                      Token.Eth:total_user_eth}

            risk_tolerance = get_risk_tolerance()
            market_direction_believe = get_market_direction_believe()
            agent = UserAgent(user_index,
                              self, ## mesa model
                              wallet,
                              market_direction_believe,
                              risk_tolerance,
                              user_lending_pool)
            
            print(agent)
            
            agents.append(agent)

        return agents

    def _setup_tokens(self):
                
        setup    = SetupContracts(self.manager)
        contract = setup.contract()
        tokens   = setup.tokens()

        return contract, tokens

    def utilization_rate(self, token):
        # TODO: Get this on chain        
        # For a market m, Um = L / A where L total loands, and A gross deposits
        Eps = 0.01 # to avoid dived by zero
        return self.borrowed[token] / (self.deposited[token] + Eps)

    
    def _change_price(self, token):

        current_price = self.market_conditions[token]["price"]
        volatility    = self.market_conditions[token]["volatility"]
        
        new_price = change_price_token_model(current_price, volatity) 

        print(f"New price for {token}", new_price)
        self.market_conditions[Token] = {token:{"price": current_price,
                                                "volatility": 10}}
        
        

    def _update_interset_rate(self):
        contract_interface = ContractInterface(self.manager, self.contract)
        
        ## on borrowings        
        total_deposits_on_dai = contract_interface.total_deposited_on_token(self.token_dai)
        
        total_loans_on_dai = contract_interface.total_borrowed_on_token(self.token_dai)
        
        self.borrowing_interest_rate_dai = get_interest_rate(total_deposits_on_dai,
                                                             total_loans_on_dai,
                                                             type_interest="borrowings") # alpha, beta?

        self.savings_interest_rate_dai = get_interest_rate(total_deposits_on_dai,
                                                           total_loans_on_dai,
                                                           type_interest="savings") # alpha, beta?


        #total_deposits_on_eth = contract_interface.total_deposited_on_token(self.token_ethToken.Eth)
        #total_loans_on_eth = contract_interface.total_deposited_on_token(Token.Eth)        
        #self.borrowing_interest_rate_eth = get_interest_rate(total_deposits_on_eth,
        #                                                     total_loans_on_eth,
        #                                                     type_interest="borrowings") # alpha, beta?
        
        ## on savings




if __name__ == "__main__":
    # Setup scenario of the simulation
    # model = LendingPlatform(15)
    model = LendingPlatform(5)

    # Number of simulations per scenario
    for _ in range(1):
        model.step()


# #### move to analysis
# exit()

# import matplotlib
# import matplotlib.pyplot as plt
# matplotlib.use('Qt5Agg')

# agent_wealth = [a.wallet[Token.Eth.value] for a in model.schedule.agents]
# print(agent_wealth)

# plt.hist(agent_wealth)

# agent_risk_tolerance = [a.risk_tolerance for a in model.schedule.agents]

# print(agent_risk_tolerance)
# plt.hist(agent_risk_tolerance)
# plt.show()


# def scenario_generator(volatility, trend, type_interest, liquidity):

#     ## Fill params for volatility (low, medium, high)
#     ## Fill params for trend (bullish, choppy, bearish)
#     ## Fill params for interest (low, medium, high)
#     ## Fill params for liquitity (low, medium, high)

#     # volatity will be related to the amount of loans on assets
#     # trend will be related to risky assets 
    
#     if name == "low_volatility":
#         pass
#     if name == "high_volatility":
#         pass
#     if name == "bearish":
#         pass
#     if name == "bullish":
#         pass
#     if name == "high_interest":
#         pass
    
#     print("Scenario number not defined")
#     return None
