from strategy.moving_average_strategy import MovingAverageStrategy
from strategy.strategy_signal import SignalType


strategy = MovingAverageStrategy(short_window=3, long_window=5)

buy_candles = [
    {"trade_price": 100},
    {"trade_price": 100},
    {"trade_price": 100},
    {"trade_price": 120},
    {"trade_price": 130},
]

buy_signal = strategy.generate_signal(
    candles=buy_candles,
    has_position=False,
)

print("매수 신호 테스트:", buy_signal)
assert buy_signal.signal_type == SignalType.BUY


sell_candles = [
    {"trade_price": 130},
    {"trade_price": 120},
    {"trade_price": 100},
    {"trade_price": 90},
    {"trade_price": 80},
]

sell_signal = strategy.generate_signal(
    candles=sell_candles,
    has_position=True,
)

print("매도 신호 테스트:", sell_signal)
assert sell_signal.signal_type == SignalType.SELL


hold_signal = strategy.generate_signal(
    candles=buy_candles,
    has_position=True,
)

print("관망 신호 테스트:", hold_signal)
assert hold_signal.signal_type == SignalType.HOLD

print("이동평균 전략 테스트 완료")