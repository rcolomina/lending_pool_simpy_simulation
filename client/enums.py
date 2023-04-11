from enum import Enum

class Token(Enum):
    Btc = 0
    Eth = 1
    Dai = 2
    RubenCoin = 3
    Alamanak = 4
    ## add more tokens

class RiskTolerance(Enum):
    low = 0
    medium = 1
    high = 2

class MarketDirectionBelieve(Enum):
    bearish = 0
    choppy = 1
    bullish = 2





################################
class IRPreference(Enum):
    VARIABLE = 1
    FIX = 2

class AFPreference(Enum):
    LOW = 1
    HIGH = 2

class Risk(Enum):
    LOW = 1
    HIGH = 2
