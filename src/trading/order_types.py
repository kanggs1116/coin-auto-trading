from enum import Enum


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderState(Enum):
    CREATED = "CREATED"
    REQUESTED = "REQUESTED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"