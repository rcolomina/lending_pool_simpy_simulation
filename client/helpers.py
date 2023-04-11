from web3 import Web3
import random
random.seed(42)

# initialize drivers
rpc = 'http://127.0.0.1:8545'
w3 = Web3(Web3.HTTPProvider(rpc))

## aux functions
def print_receipt(tx_hash, topic):
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Transaction {topic} receipt mined:")
    print("Was transaction successful?", receipt["status"])



def get_random_choice(lrange=1/3.0, hrange=2/3.0, values=[]):
    r = random.uniform(0,1)
    return values[0] if r > hrange else values[1] if r > lrange else values[2]

from enums import RiskTolerance
from enums import MarketDirectionBelieve

def get_risk_tolerance(lrange = 1/3.0,
                       hrange = 2/3.0,
                       values=[RiskTolerance.high,
                               RiskTolerance.medium,
                               RiskTolerance.low]):
    return get_random_choice(lrange,hrange,values)

def get_market_direction_believe(lrange = 1/3.0,
                                 hrange = 2/3.0, 
                                 values=[MarketDirectionBelieve.bullish,
                                         MarketDirectionBelieve.choppy,
                                         MarketDirectionBelieve.bearish]):
    return get_random_choice(lrange, hrange ,values)


def change_price_token_model(current_price, volatity=10):
    # update market conditions
    percentage_change = (random.uniform(0,1) - 0.5) * volatility

    # TODO: Change in volatility ??
    #volatility = 
    
    return current_price * (1 + percentage_change / 100.0), volatility


    

    
