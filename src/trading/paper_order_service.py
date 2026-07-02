from datetime import datetime
from uuid import uuid4

from trading.order_model import Order
from trading.order_service import OrderService
from trading.order_types import OrderSide, OrderType, OrderState
from trading.position import PositionManager
from trading.risk_manager import RiskManager


class PaperOrderService(OrderService):
    def __init__(
        self,
        position_manager: PositionManager,
        risk_manager: RiskManager,
        fee_rate: float = 0.0005,
    ):
        self.position_manager = position_manager
        self.risk_manager = risk_manager
        self.fee_rate = fee_rate
        self.orders: dict[str, Order] = {}
        self.current_prices: dict[str, float] = {}

    def get_current_price(self, market: str) -> float:
        price = self.current_prices.get(market)

        if price is None:
            raise ValueError(f"{market}의 현재가가 설정되지 않았습니다.")
            
        return price

    def buy_market(self, market: str, krw_amount: float) -> Order:
        current_position_krw = self.position_manager.get_position_value(market)
        self.risk_manager.validate_buy(krw_amount, current_position_krw)

        price = self.get_current_price(market)
        fee = krw_amount * self.fee_rate
        available_krw = krw_amount - fee
        volume = available_krw / price

        order = Order(
            order_id=str(uuid4()),
            market=market,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            state=OrderState.FILLED,
            price=None,
            volume=None,
            krw_amount=krw_amount,
            executed_price=price,
            executed_volume=volume,
            fee=fee,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.position_manager.apply_buy(market, price, volume)
        self.orders[order.order_id] = order

        return order

    def sell_market(self, market: str, volume: float) -> Order:
        current_volume = self.position_manager.get_volume(market)
        self.risk_manager.validate_sell(volume, current_volume)

        price = self.get_current_price(market)
        gross_amount = price * volume
        fee = gross_amount * self.fee_rate

        order = Order(
            order_id=str(uuid4()),
            market=market,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            state=OrderState.FILLED,
            price=None,
            volume=volume,
            krw_amount=None,
            executed_price=price,
            executed_volume=volume,
            fee=fee,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.position_manager.apply_sell(market, volume)
        self.orders[order.order_id] = order

        return order

    def get_order(self, order_id: str) -> Order:
        return self.orders[order_id]

    def cancel_order(self, order_id: str) -> Order:
        order = self.orders[order_id]

        if order.state == OrderState.FILLED:
            raise ValueError("이미 체결된 주문은 취소할 수 없습니다.")

        order.state = OrderState.CANCELED
        order.updated_at = datetime.now()

        return order

    def update_current_price(self, market: str, price: float) -> None:
        if price <= 0:
            raise ValueError("현재가는 0보다 커야 합니다.")

        self.current_prices[market] = price