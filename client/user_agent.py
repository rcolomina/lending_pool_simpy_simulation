import mesa

from enums import Token

from integration_test import ContractInterface

from agent_models import get_percentage_on_amount_to_deposit
from agent_models import get_loan_size_on_borrower

from helpers import get_risk_tolerance
from helpers import get_market_direction_believe
from helpers import get_interest_rate_preference

from enums import MarketDirectionBelieve


class UserAgent(mesa.Agent):
    def __init__(self,
                 unique_id,
                 model,                 
                 user_lending_pool):
        
        super().__init__(unique_id, model)
        self.user_lending_pool = user_lending_pool
        


        ## this controls the distribution
        ## on risk tolerance affecting the amount 
        self.risk_tolerance    = get_risk_tolerance()

        ## on market direcition affecting which coins should be selcted for both deposits and borrowings
        self.market_direction_believe = get_market_direction_believe()

        ## on interest rate preference (willingness to pay high interest rates)
        self.interest_rate_preference = get_interest_rate_preference()

        
        self.contract_interface = ContractInterface(self.user_lending_pool,
                                                    self.model.contract)
        self.user_name = self.user_lending_pool.name
        self.user_address = self.user_lending_pool.address
        
        self.total_borrowed = 0
        self.total_deposited = 0

    def __str__(self):
        return f"agent_id: {self.unique_id} | risk tolerance:{self.risk_tolerance} " + \
          "| market: {self.market_direction_believe}"
        
    def get_collateral_borrow_for_token(self, user_address, token_address):
        lending_pool_contract = self.model.contract
        token_collateral, token_borrow = lending_pool_contract.functions.getUserTokenCollateralAndBorrow(user_address,
                                                                                                       token_address).call()
        
        return token_collateral, token_borrow


    def deposit_on_token(self, token):

        ## simulation parameters depending on num tokens some are ignored
        if self.model.num_coins == 1 and token.address != self.model.token_dai.address:                
            return
        if self.model.num_coins == 2 and token.address == self.model.token_almanak_coin:
            return
        
        risk_tolerance = self.risk_tolerance 

        token_address = token.address

        ## expected interest rate for savings
        interest_rate = self.model.interest_rate_savings[token_address]
        
        percent_to_deposit = get_percentage_on_amount_to_deposit(interest_rate,
                                                                 risk_tolerance)

        ## total amount of funds (units) for a specific token
        total = token.functions.balanceOf(self.user_lending_pool.address).call() // 1e18
        
        amount_to_deposit = percent_to_deposit * int(total) / 100
        
        
        token_collateral, token_borrow = self.get_collateral_borrow_for_token(self.user_address,
                                                                              token_address)
        
        
        if token_collateral < amount_to_deposit * 1e18: # comparing on weis
            remaining_to_deposit = amount_to_deposit - token_collateral // 1e18
            print(f"Remaining to Deposit {remaining_to_deposit}")
            #self.deposit(remaining_to_deposit, token)

            try:
                if remaining_to_deposit > 0:
                    self.contract_interface.supply(token,remaining_to_deposit) # interact with the contract
                    self.total_deposited += remaining_to_deposit 
            except Exception as e:
                print(f"WARNING! Deposit was reverted {e}")
        else:
            print(f"{self.user_name} already deposited {token_collateral // 1e18} " + \
                  f"than its target amount {amount_to_deposit} for " + \
                  f"its risk tolerance ({self.risk_tolerance.name})" + \
                  f" on token {token_address}")


    def get_user_data(self):
        user_data = self.model.contract.functions.getUserData(self.user_address).call()        
        collateral = user_data[0] / 1e18 ## total deposited in DAI
        borrowed   = user_data[1] / 1e18 ## total borrowed in DAI
        print(f"User Data {self.user_name}: collateral {collateral} and borrowed {borrowed} in DAIS")
        return collateral, borrowed
        
    def borrow_on_token(self, token):

        ## simulation parameters depending on num tokens some are ignored
        if self.model.num_coins == 1 and token.address != self.model.token_dai.address:                
            return
        if self.model.num_coins == 2 and token.address == self.model.token_almanak_coin:
            return
                        
        collateral, borrowed = self.get_user_data()
        interest_rate_token  = self.model.interest_rate_borrowings[token.address]
        loan_size_target = get_loan_size_on_borrower(interest_rate_token,
                                                     collateral,
                                                     self.interest_rate_preference,
                                                     self.risk_tolerance)
        user_address = self.user_address
        
        if borrowed < loan_size_target:
            remaining_to_borrow = loan_size_target - borrowed
            print(f"Remaining to Borrow {remaining_to_borrow}")
            try:
                if remaining_to_borrow > 0:
                    self.contract_interface.borrow(token, remaining_to_borrow) # interact with the contract
                    self.total_borrowed += remaining_to_borrow
            except Exception as e:
                print(f"WARNING! Borrowing was reverted {e}")                
        else:
            print(f"{self.user_name} already borrowed {borrowed} " + \
                  f"than its target loan {loan_size_target} " + \
                  f"for its risk tolerance ({self.risk_tolerance.name})")
            


    def step(self):
        ## ASSUMPTIONS
        ##  Dai is stable coin pegged to dollar 
        ### RubenCoin and AlmanaCoin are correlated to BTC
        
        ## DEPOSITING        
        ## which one depoist (deposit the one that is going to lose value!)
        if self.market_direction_believe == MarketDirectionBelieve.bearish:
            self.deposit_on_token(self.model.token_dai)

        if self.market_direction_believe == MarketDirectionBelieve.choppy:
            self.deposit_on_token(self.model.token_dai)
            self.deposit_on_token(self.model.token_ruben_coin)
            self.deposit_on_token(self.model.token_almanak_coin)

        if self.market_direction_believe == MarketDirectionBelieve.bullish:
            self.deposit_on_token(self.model.token_ruben_coin)
            self.deposit_on_token(self.model.token_almanak_coin)

        ## TODO: ADD LOGIC TO REDEEM
        
        ### BORROWING                        
        if self.market_direction_believe == MarketDirectionBelieve.bearish:
            self.borrow_on_token(self.model.token_ruben_coin)
            self.borrow_on_token(self.model.token_almanak_coin)

        if self.market_direction_believe == MarketDirectionBelieve.choppy:
            self.borrow_on_token(self.model.token_dai)
            self.borrow_on_token(self.model.token_ruben_coin)
            self.borrow_on_token(self.model.token_almanak_coin)

        if self.market_direction_believe == MarketDirectionBelieve.bullish:
            self.borrow_on_token(self.model.token_dai)

        ## TODO: Add logic to repay


        # stats for batch processing
        collateral, borrowed = self.get_user_data()
        self.total_borrowed = borrowed
        self.total_deposited = collateral

            
    def repay_borrows(self):
        # TODO
        print(f"REPAY BORROWINGS {self.user_name}")
        #self.total_borrowed 
        #self.total_deposited 

    def remove_collateral(self):
        # TODO
        print(f"REMOVE COLLATERAL {self.user_name}")

