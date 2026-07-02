from abc import ABC, abstractmethod

from trading.order_model import Order


class OrderService(ABC):

    @abstractmethod
    def buy_market(self, market: str, krw_amount: float) -> Order:
        pass

    @abstractmethod
    def sell_market(self, market: str, volume: float) -> Order:
        pass

    @abstractmethod
    def get_order(self, order_id: str) -> Order:
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> Order:
        pass