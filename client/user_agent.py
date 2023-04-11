import mesa

from enums import Token

from integration_test import ContractInterface
from agent_models import get_percentage_on_amount_to_deposit


class UserAgent(mesa.Agent):
    def __init__(self,unique_id,
                 model,
                 wallet,
                 market_direction_believe,
                 risk_tolerance,
                 user_lending_pool):
        
        super().__init__(unique_id, model)

        self.risk_tolerance = risk_tolerance # for lenders
        self.market_direction_believe = market_direction_believe
        #self.interest_rate_preference = interest_rate_preference # for borrowers 

        self.wallet = wallet
        
        self.borrowed = {Token.Eth:0,Token.Dai:0}
        self.collateral = {Token.Eth:0,Token.Dai:0}

        self.user    = user_lending_pool
        self.name    = user_lending_pool.name
        self.address = user_lending_pool.address

        self.contract_interface = ContractInterface(self.user,
                                                    self.model.contract)

    def __str__(self):
        return f"name: {self.name} | wallet: {self.wallet} | borrowed: {self.borrowed} | collateral: {self.collateral} | risk tolerance: {self.risk_tolerance} | direction: {self.market_direction_believe}"

    def print_agent(self):
        print("**AGENT**")
        print(f" -Hi, I am {self.name} with id {self.unique_id} DAI {self.wallet[Token.Dai]} ")
        print(f" -my wallet contains --> {self.wallet}")
        print(f" -my address risk tolerance (as lender) is {self.risk_tolerance}")
        print("*********")
        
    def total_borrowed(self):
        return sum([v for _,v in self.borrowed.items()]) # Review: This does make sense

    def total_collateral(self):
        return sum([v for _,v in self.collateral.items()]) # Review: This does make sense

    def health_factor(self): 
        ## TODO: Integrate this with the contract
        LIQUIDATION_THRESHOLD = 0.8 # TODO: Get this from the model
        if self.totalBorrowAmount() == 0:
            return 100        
        return self.total_collateral() * LIQUIDATION_THRESHOLD / self.totalBorrowAmount()

    def get_units_of_token(token):
        balance = token.functions.balanceOf(self.user.address).call() // 1e18
        return balance #self.model.
    
    def step(self):
        risk_tolerance = self.risk_tolerance # for the lender                
        market_conditions = self.model.market_conditions
    
        ## TO DEPOSIT

        ## TODO: Check which coin to deposit on 
        
        ### go through the tokens checking the interest rate        
        interest_rate = self.model.savings_interest_rate_dai # on token


        ## depends on available funds, risk tolerance
        percent_to_deposit = get_percentage_on_amount_to_deposit(interest_rate,
                                                                 risk_tolerance)

        total_dai = self.wallet[Token.Dai]
        print("Users Dai", total_dai )
        print("Percent % to risk on deposit: ",percent_to_deposit)
        amount_to_deposit = percent_to_deposit * total_dai / 100


        print("ON USER DEPOSIT PARAMS")
        print(" Unique Id",self.unique_id)
        print(" Name",self.name)
        print(" Amount to deposit ", amount_to_deposit)
        print(" Risk Tolerance", self.risk_tolerance)
        
        ## if t/i high/low => deposit more/less of the availabe fundsore deposit        
        print(f" User balance of token {self.model.token_dai.address} for the user ",
              f"{self.user.name} is {total_dai}")

        #return        
        self.deposit(amount_to_deposit, Token.Dai)
        
        ## TO BORROW
        ## depends on loan size, interrest rate preference

        # decide what to depoist and what to borrow and how much of each

         ## if high risk tolerance deposit 80%
          ### check believes
            ## if bullish/bearish deposit eth/dai and borrow dai/eth
            ## if choppy  deposit the highest t/i and borrow on the lowest t/i
         
          ## loan size needs 30%, 40%, 60% of the deposit funds
         
         ## if low rish tolerance
           ## go for the best t/i on stable coin at 50%, 70%, 90% of available funds
         
         
        #if self.risk_tolerance > 0.5: # make this decision more interesting
        #    token_to_borrow = Token.Eth                        
                
            # select token to borrow depending on risk tolerance
        #    if token_to_borrow == Token.Eth:
        #        ethereum = self.model.tokens[0])
        #        loan_size = 0.5 # This should be a fraction of the total collateral for this user
        #        self.borrow(loan_size, ethereum)
        #else:
            
        #    pass
                
    def borrow(self, loan_size, token):        
        # TODO: check health risk
        # move loan size to token        
        token_price = 1 #1800
        self.borrowed[Token.Dai] += loan_size
        self.wallet[Token.Dai] += loan_size
        #self.wallet[Token.Dai] -= loan_size * token_price
        
        if token == Token.Dai:            
            self.contract_interface.borrow(self.model.token,
                                           loan_size)
        

    def deposit(self, amount, token):

        token_price = 1
        #self.deposited
        self.wallet[Token.Dai] -= amount * token_price
        if token == Token.Dai:
            #print(""self.model.token)
            print(f"amount {amount}")
            self.contract_interface.supply(self.model.token_dai,
                                           amount)

            #if self.dai >= amount: # only if there are enough funds
                # ok do the borrow
            #    self.borrow = {"dai":amount}
            #else:
            #    print(f"{self.name} doesn't have enough funds")
        

    
