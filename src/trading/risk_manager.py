class RiskManager:
    def __init__(
        self,
        min_order_krw: float = 5000,
        max_order_krw: float = 100000,
        max_position_krw: float = 300000,
    ):
        self.min_order_krw = min_order_krw
        self.max_order_krw = max_order_krw
        self.max_position_krw = max_position_krw

    def validate_buy(self, krw_amount: float, current_position_krw: float = 0) -> None:
        if krw_amount < self.min_order_krw:
            raise ValueError("최소 주문 금액 미만입니다.")

        if krw_amount > self.max_order_krw:
            raise ValueError("1회 주문 한도를 초과했습니다.")

        if current_position_krw + krw_amount > self.max_position_krw:
            raise ValueError("종목별 최대 보유 금액을 초과합니다.")

    def validate_sell(self, sell_volume: float, current_volume: float) -> None:
        if sell_volume <= 0:
            raise ValueError("매도 수량은 0보다 커야 합니다.")

        if sell_volume > current_volume:
            raise ValueError("보유 수량보다 많이 매도할 수 없습니다.")