from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from trading.order_types import OrderSide, OrderType, OrderState


@dataclass
class Order:
    order_id: str
    market: str
    side: OrderSide
    order_type: OrderType
    state: OrderState

    price: Optional[float]
    volume: Optional[float]
    krw_amount: Optional[float]

    executed_price: Optional[float] = None
    executed_volume: Optional[float] = None
    fee: float = 0.0

    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()