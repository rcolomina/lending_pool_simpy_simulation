from enums import RiskTolerance
from enums import MarketDirectionBelieve

    
def get_percentage_on_amount_to_deposit(interest_rate,
                                        risk_tolerance, 
                                        alpha=1.0, 
                                        beta=10):
    
    max_deposit = 95 # let's get crazy on the pool
        
    if risk_tolerance == RiskTolerance.high:
        alpha *= 10 # let's give it a go even though interest rate 0
        beta  *= 2 # let's go in asap
    elif risk_tolerance == RiskTolerance.medium:
        max_deposit /= 2 # half of may money is good investiment 
        alpha *= 5 # let's give it a go even though interest rate 0
        beta  *= 1 # moderate go all in 
    elif risk_tolerance == RiskTolerance.low: 
        max_deposit /= 4 # never invest more than you afford to lose
        alpha *= 2 # No positive interest rate NO interest on investment
        beta  /= 2 # very moderate
    else:
        print("ERROR on risk tolerance value")
        # TODO: Raise error

    # linear model on interest rate
    model =  alpha + beta * interest_rate
    
    return min(max_deposit, model )



def get_loan_size_on_borrower(interest_rate_preference):
    pass
    
