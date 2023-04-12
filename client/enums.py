from enum import Enum

class Token(Enum):
    Btc = 0
    Eth = 1
    Dai = 2
    RubenCoin = 3
    Almanak = 4
    ## add more tokens

class RiskTolerance(Enum):
    low = 0
    medium = 1
    high = 2

class MarketDirectionBelieve(Enum):
    bearish = 0
    choppy = 1
    bullish = 2

class InterestRatePref(Enum):
    low = 0
    medium = 1
    high = 2


class TypeInterestRatePref(Enum):
    VARIABLE = 1
    FIX = 2

