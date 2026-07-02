from strategy.strategy_signal import StrategySignal, SignalType


class MovingAverageStrategy:
    def __init__(self, short_window: int = 5, long_window: int = 20):
        if short_window >= long_window:
            raise ValueError("short_window는 long_window보다 작아야 합니다.")

        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, candles: list[dict], has_position: bool) -> StrategySignal:
        if len(candles) < self.long_window:
            return StrategySignal(
                signal_type=SignalType.HOLD,
                reason="이동평균 계산에 필요한 캔들 수가 부족합니다."
            )

        prices = [float(candle["trade_price"]) for candle in candles]

        short_ma = sum(prices[-self.short_window:]) / self.short_window
        long_ma = sum(prices[-self.long_window:]) / self.long_window

        if not has_position and short_ma > long_ma:
            return StrategySignal(
                signal_type=SignalType.BUY,
                reason=f"매수 조건 충족: 단기 MA({short_ma:.2f}) > 장기 MA({long_ma:.2f})"
            )

        if has_position and short_ma < long_ma:
            return StrategySignal(
                signal_type=SignalType.SELL,
                reason=f"매도 조건 충족: 단기 MA({short_ma:.2f}) < 장기 MA({long_ma:.2f})"
            )

        return StrategySignal(
            signal_type=SignalType.HOLD,
            reason=f"관망: 단기 MA({short_ma:.2f}), 장기 MA({long_ma:.2f})"
        )