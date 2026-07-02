from trading.order_model import Order
from trading.order_service import OrderService


class RealOrderService(OrderService):

    def buy_market(self, market: str, krw_amount: float) -> Order:
        raise NotImplementedError("실주문 기능은 아직 구현하지 않았습니다.")

    def sell_market(self, market: str, volume: float) -> Order:
        raise NotImplementedError("실주문 기능은 아직 구현하지 않았습니다.")

    def get_order(self, order_id: str) -> Order:
        raise NotImplementedError("실주문 조회 기능은 아직 구현하지 않았습니다.")

    def cancel_order(self, order_id: str) -> Order:
        raise NotImplementedError("실주문 취소 기능은 아직 구현하지 않았습니다.")