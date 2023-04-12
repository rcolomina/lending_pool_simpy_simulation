## Models can be found at the reference Document section 4
#  arXiv:2006.13922v3 [q-fin.GN] 15 Oct 2020

def get_utilization_rate(total_deposits, total_loans, eps=0.001):
    # For a market m, Um = L / A where L total loands, and A gross deposits
    #    Eps = 0.01 # to avoid dived by zero
    if not isinstance(eps, float):
        raise TypeError(f"Eps has to be a float, not {type(eps)}")
    
    return total_loans / (total_deposits + eps)

def get_interest_rate(total_deposits, total_loans,
                      alpha=1.0, beta=5.0, eps=0.001, type_interest = "borrowings"):

    utilization_rate = get_utilization_rate(total_deposits, total_loans, eps=eps)

    interest_borrowing_market = alpha + beta * utilization_rate

    if type_interest == "borrowings":
        return interest_borrowing_market
    elif type_interest == "savings":
        return interest_borrowing_market * utilization_rate
    else:
        raise ValueError("Type of Interest is not considered")
    



    
    
