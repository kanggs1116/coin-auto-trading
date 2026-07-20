from dataclasses import dataclass


ALLOWED_MINUTE_UNITS = {
    1,
    3,
    5,
    10,
    15,
    30,
    60,
    240,
}


@dataclass(frozen=True)
class BacktestConfig:
    market: str = "KRW-BTC"
    candle_type: str = "minute"
    candle_unit: int = 1

    initial_capital: float = 1_000_000
    order_amount_krw: float = 100_000

    buy_fee_rate: float = 0.0005
    sell_fee_rate: float = 0.0005

    def __post_init__(self) -> None:
        self._validate_market()
        self._validate_candle_type()
        self._validate_candle_unit()
        self._validate_initial_capital()
        self._validate_fee_rates()
        self._validate_order_amount()

    def _validate_market(self) -> None:
        if not self.market or not self.market.strip():
            raise ValueError("market은 비어 있을 수 없습니다.")

    def _validate_candle_type(self) -> None:
        if self.candle_type != "minute":
            raise ValueError(
                "현재 백테스트 MVP에서는 candle_type='minute'만 지원합니다."
            )

    def _validate_candle_unit(self) -> None:
        if self.candle_unit not in ALLOWED_MINUTE_UNITS:
            raise ValueError(
                "candle_unit은 1, 3, 5, 10, 15, 30, 60, 240 중 하나여야 합니다."
            )

    def _validate_initial_capital(self) -> None:
        if self.initial_capital <= 0:
            raise ValueError("initial_capital은 0보다 커야 합니다.")

    def _validate_fee_rates(self) -> None:
        if not 0 <= self.buy_fee_rate < 1:
            raise ValueError(
                "buy_fee_rate는 0 이상 1 미만이어야 합니다."
            )

        if not 0 <= self.sell_fee_rate < 1:
            raise ValueError(
                "sell_fee_rate는 0 이상 1 미만이어야 합니다."
            )

    def _validate_order_amount(self) -> None:
        if self.order_amount_krw <= 0:
            raise ValueError("order_amount_krw는 0보다 커야 합니다.")

        required_cash = self.order_amount_krw * (
            1 + self.buy_fee_rate
        )

        if required_cash > self.initial_capital:
            raise ValueError(
                "초기 자본은 1회 매수 체결금액과 매수 수수료의 합 이상이어야 합니다."
            )