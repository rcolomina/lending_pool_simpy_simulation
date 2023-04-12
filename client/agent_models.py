from enums import RiskTolerance
from enums import MarketDirectionBelieve
from enums import InterestRatePref



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
    
    return min(max_deposit, model)




def max_percentage_of_collateral(risk_tolerance,
                                 lp = 0.3, mp = 0.5, hp = 0.7):

    return lp if risk_tolerance==RiskTolerance.low else mp if risk_tolerance==RiskTolerance.medium else hp

def get_loan_size_on_borrower(interest_rate,
                              collateral,
                              interest_preference,
                              risk_tolerance, lrange_ir = 2, hrange_ir = 10, ):


    if interest_rate <= lrange_ir:
        return collateral * max_percentage_of_collateral(risk_tolerance)

        
    elif interest_rate <= hrange_ir:
        if interest_preference == InterestRatePref.low:            
            return 0.0 # no borrowings
        else:
            return collateral * max_percentage_of_collateral(risk_tolerance)
    else:
        if interest_preference == InterestRatePref.high:
            return collateral * max_percentage_of_collateral(risk_tolerance)
        else:
            return 0.0 # no borrowings


        

     

    
    
