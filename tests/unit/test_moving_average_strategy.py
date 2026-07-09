import pytest

from strategy.moving_average_strategy import MovingAverageStrategy
from strategy.strategy_signal import SignalType


def make_candles(prices):
    return [{"trade_price": price} for price in prices]


def test_init_short_window_must_be_less_than_long_window():
    with pytest.raises(ValueError, match="short_window는 long_window보다 작아야 합니다."):
        MovingAverageStrategy(short_window=20, long_window=20)


def test_generate_signal_returns_hold_when_candles_are_not_enough():
    strategy = MovingAverageStrategy(short_window=5, long_window=20)

    candles = make_candles([100, 101, 102])

    signal = strategy.generate_signal(
        candles=candles,
        has_position=False,
    )

    assert signal.signal_type == SignalType.HOLD
    assert signal.reason != ""


def test_generate_signal_returns_buy_when_short_ma_is_greater_than_long_ma_without_position():
    strategy = MovingAverageStrategy(short_window=5, long_window=20)

    candles = make_candles([
        100, 100, 100, 100, 100,
        100, 100, 100, 100, 100,
        100, 100, 100, 100, 100,
        120, 121, 122, 123, 124,
    ])

    signal = strategy.generate_signal(
        candles=candles,
        has_position=False,
    )

    assert signal.signal_type == SignalType.BUY
    assert "매수 조건 충족" in signal.reason


def test_generate_signal_returns_sell_when_short_ma_is_less_than_long_ma_with_position():
    strategy = MovingAverageStrategy(short_window=5, long_window=20)

    candles = make_candles([
        120, 120, 120, 120, 120,
        120, 120, 120, 120, 120,
        120, 120, 120, 120, 120,
        100, 99, 98, 97, 96,
    ])

    signal = strategy.generate_signal(
        candles=candles,
        has_position=True,
    )

    assert signal.signal_type == SignalType.SELL
    assert "매도 조건 충족" in signal.reason


def test_generate_signal_returns_hold_when_short_ma_is_less_than_long_ma_without_position():
    strategy = MovingAverageStrategy(short_window=5, long_window=20)

    candles = make_candles([
        120, 120, 120, 120, 120,
        120, 120, 120, 120, 120,
        120, 120, 120, 120, 120,
        100, 99, 98, 97, 96,
    ])

    signal = strategy.generate_signal(
        candles=candles,
        has_position=False,
    )

    assert signal.signal_type == SignalType.HOLD
    assert "관망" in signal.reason


def test_generate_signal_returns_hold_when_short_ma_is_greater_than_long_ma_with_position():
    strategy = MovingAverageStrategy(short_window=5, long_window=20)

    candles = make_candles([
        100, 100, 100, 100, 100,
        100, 100, 100, 100, 100,
        100, 100, 100, 100, 100,
        120, 121, 122, 123, 124,
    ])

    signal = strategy.generate_signal(
        candles=candles,
        has_position=True,
    )

    assert signal.signal_type == SignalType.HOLD
    assert "관망" in signal.reason