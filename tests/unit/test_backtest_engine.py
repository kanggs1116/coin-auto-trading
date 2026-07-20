from datetime import datetime, timedelta

import pytest

from backtest.backtest_config import BacktestConfig
from backtest.backtest_engine import BacktestEngine
from strategy.moving_average_strategy import (
    MovingAverageStrategy,
)
from strategy.strategy_signal import (
    SignalType,
    StrategySignal,
)
from trading.order_types import OrderSide

def make_candles(
    prices: list[float],
) -> list[dict]:
    start_time = datetime(
        2026,
        1,
        1,
        0,
        0,
    )

    return [
        {
            "candle_date_time_utc": (
                start_time
                + timedelta(minutes=index)
            ),
            "trade_price": price,
        }
        for index, price in enumerate(prices)
    ]


class RecordingHoldStrategy:
    def __init__(self):
        self.received_candle_counts = []
        self.received_position_states = []

    def generate_signal(
        self,
        candles,
        has_position,
    ):
        self.received_candle_counts.append(
            len(candles)
        )
        self.received_position_states.append(
            has_position
        )

        return StrategySignal(
            signal_type=SignalType.HOLD,
            reason="테스트용 HOLD",
        )


class AlwaysBuyStrategy:
    def generate_signal(
        self,
        candles,
        has_position,
    ):
        return StrategySignal(
            signal_type=SignalType.BUY,
            reason="테스트용 BUY",
        )


class AlwaysSellStrategy:
    def generate_signal(
        self,
        candles,
        has_position,
    ):
        return StrategySignal(
            signal_type=SignalType.SELL,
            reason="테스트용 SELL",
        )


def create_default_engine(
    strategy,
) -> BacktestEngine:
    config = BacktestConfig()

    return BacktestEngine(
        config=config,
        strategy=strategy,
    )


def test_run_empty_candles_raises_error():
    strategy = RecordingHoldStrategy()
    engine = create_default_engine(strategy)

    with pytest.raises(
        ValueError,
        match=(
            "백테스트에 사용할 캔들 "
            "데이터가 없습니다."
        ),
    ):
        engine.run([])


def test_run_missing_timestamp_raises_error():
    strategy = RecordingHoldStrategy()
    engine = create_default_engine(strategy)

    candles = [
        {
            "trade_price": 100,
        }
    ]

    with pytest.raises(
        ValueError,
        match="candle_date_time_utc",
    ):
        engine.run(candles)


def test_run_missing_trade_price_raises_error():
    strategy = RecordingHoldStrategy()
    engine = create_default_engine(strategy)

    candles = [
        {
            "candle_date_time_utc": datetime(
                2026,
                1,
                1,
            ),
        }
    ]

    with pytest.raises(
        ValueError,
        match="trade_price",
    ):
        engine.run(candles)


@pytest.mark.parametrize(
    "price",
    [
        0,
        -1,
        -100,
    ],
)
def test_run_non_positive_price_raises_error(
    price,
):
    strategy = RecordingHoldStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles([price])

    with pytest.raises(
        ValueError,
        match=(
            "trade_price는 0보다 "
            "커야 합니다."
        ),
    ):
        engine.run(candles)


def test_run_unsorted_candles_raises_error():
    strategy = RecordingHoldStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [100, 101, 102]
    )

    candles[1], candles[2] = (
        candles[2],
        candles[1],
    )

    with pytest.raises(
        ValueError,
        match=(
            "캔들은 중복 없이 과거에서 최신 "
            "순서로 정렬되어야 합니다."
        ),
    ):
        engine.run(candles)


def test_run_duplicate_candle_times_raises_error():
    strategy = RecordingHoldStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [100, 101]
    )

    candles[1][
        "candle_date_time_utc"
    ] = candles[0][
        "candle_date_time_utc"
    ]

    with pytest.raises(
        ValueError,
        match=(
            "캔들은 중복 없이 과거에서 최신 "
            "순서로 정렬되어야 합니다."
        ),
    ):
        engine.run(candles)


def test_run_passes_only_visible_candles_to_strategy():
    strategy = RecordingHoldStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [100, 101, 102, 103, 104]
    )

    engine.run(candles)

    assert (
        strategy.received_candle_counts
        == [1, 2, 3, 4, 5]
    )


def test_run_passes_false_position_state_during_hold():
    strategy = RecordingHoldStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [100, 101, 102]
    )

    engine.run(candles)

    assert (
        strategy.received_position_states
        == [False, False, False]
    )


def test_run_hold_scenario_creates_no_trades():
    strategy = RecordingHoldStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [100, 101, 102]
    )

    result = engine.run(candles)

    assert result.total_trade_count == 0
    assert result.completed_trade_count == 0
    assert result.trades == []
    assert result.has_open_position is False


def test_run_hold_scenario_keeps_initial_capital():
    strategy = RecordingHoldStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [100, 101, 102]
    )

    result = engine.run(candles)

    assert result.initial_capital == pytest.approx(
        1_000_000
    )
    assert result.final_cash == pytest.approx(
        1_000_000
    )
    assert result.final_position_value == pytest.approx(
        0.0
    )
    assert result.final_equity == pytest.approx(
        1_000_000
    )
    assert result.cumulative_return == pytest.approx(
        0.0
    )


def test_run_records_equity_for_every_candle():
    strategy = RecordingHoldStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [100, 101, 102]
    )

    result = engine.run(candles)

    assert len(result.equity_curve) == 3

    for index, record in enumerate(
        result.equity_curve
    ):
        assert record.timestamp == (
            candles[index][
                "candle_date_time_utc"
            ]
        )
        assert record.price == pytest.approx(
            candles[index]["trade_price"]
        )
        assert record.cash == pytest.approx(
            1_000_000
        )
        assert record.position_volume == pytest.approx(
            0.0
        )
        assert record.position_value == pytest.approx(
            0.0
        )
        assert record.total_equity == pytest.approx(
            1_000_000
        )


def test_run_sets_period_and_candle_summary():
    strategy = RecordingHoldStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [100, 101, 102]
    )

    result = engine.run(candles)

    assert result.market == "KRW-BTC"
    assert result.candle_count == 3
    assert result.start_time == candles[0][
        "candle_date_time_utc"
    ]
    assert result.end_time == candles[-1][
        "candle_date_time_utc"
    ]
    assert result.last_price == pytest.approx(
        102
    )


def test_run_hold_scenario_has_zero_statistics():
    strategy = RecordingHoldStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [100, 101, 102]
    )

    result = engine.run(candles)

    assert result.winning_trade_count == 0
    assert result.losing_trade_count == 0
    assert result.win_rate == pytest.approx(
        0.0
    )
    assert result.max_drawdown == pytest.approx(
        0.0
    )

def test_run_hold_scenario_has_zero_drawdown(): #거래 없을 때 MDD 0 테스트
    strategy = RecordingHoldStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [100, 101, 99, 102]
    )

    result = engine.run(candles)

    assert result.max_drawdown == pytest.approx(
        0.0
    )

def test_run_buy_fee_is_reflected_in_drawdown(): #최초 매수 수수료 MDD 반영 여부 테스트
    strategy = BuyOnceStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [100_000_000]
    )

    result = engine.run(candles)

    expected_drawdown = (
        50 / 1_000_000
    )

    assert result.max_drawdown == pytest.approx(
        expected_drawdown
    )

def test_run_calculates_max_drawdown_from_equity_curve(): #상승 후 하락하는 자산 곡선의 MDD 테스트
    strategy = BuyOnceStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [
            100_000_000,
            120_000_000,
            90_000_000,
        ]
    )

    result = engine.run(candles)

    peak_equity = 1_019_950
    trough_equity = 989_950

    expected_mdd = (
        peak_equity - trough_equity
    ) / peak_equity

    assert result.max_drawdown == pytest.approx(
        expected_mdd
    )

def test_run_drawdown_uses_latest_equity_peak(): #최고점 갱신 테스트
    strategy = BuyOnceStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [
            100_000_000,
            120_000_000,
            110_000_000,
            150_000_000,
            100_000_000,
        ]
    )

    result = engine.run(candles)

    peak_equity = (
        899_950 + 150_000
    )

    trough_equity = (
        899_950 + 100_000
    )

    expected_mdd = (
        peak_equity - trough_equity
    ) / peak_equity

    assert result.max_drawdown == pytest.approx(
        expected_mdd
    )

def test_run_with_real_moving_average_strategy_hold_scenario():
    strategy = MovingAverageStrategy(
        short_window=5,
        long_window=20,
    )

    engine = create_default_engine(strategy)

    candles = make_candles(
        [100 for _ in range(30)]
    )

    result = engine.run(candles)

    assert result.total_trade_count == 0
    assert result.final_equity == pytest.approx(
        1_000_000
    )
    assert len(result.equity_curve) == 30

def test_run_profitable_trade_returns_final_metrics(): #수익 거래 후 최종 성과지표 테스트
    strategy = BuyThenSellStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [
            100_000_000,
            110_000_000,
        ]
    )

    result = engine.run(candles)

    expected_final_equity = 1_009_895
    expected_return = (
        expected_final_equity - 1_000_000
    ) / 1_000_000

    assert result.final_cash == pytest.approx(
        expected_final_equity
    )
    assert result.final_position_volume == pytest.approx(
        0.0
    )
    assert result.final_position_value == pytest.approx(
        0.0
    )
    assert result.final_equity == pytest.approx(
        expected_final_equity
    )
    assert result.cumulative_return == pytest.approx(
        expected_return
    )
    assert result.has_open_position is False

    assert result.total_trade_count == 2
    assert result.completed_trade_count == 1
    assert result.winning_trade_count == 1
    assert result.losing_trade_count == 0
    assert result.win_rate == pytest.approx(
        1.0
    )

def test_run_losing_trade_returns_negative_result(): #손실 거래의 최종 성과지표 테스트
    strategy = BuyThenSellStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [
            100_000_000,
            90_000_000,
        ]
    )

    result = engine.run(candles)

    assert result.final_equity < 1_000_000
    assert result.cumulative_return < 0

    assert result.completed_trade_count == 1
    assert result.winning_trade_count == 0
    assert result.losing_trade_count == 1
    assert result.win_rate == pytest.approx(
        0.0
    )

    assert result.max_drawdown > 0

def test_run_open_position_is_valued_at_last_price(): #미청산 포지션 최종 평가 테스트
    strategy = BuyOnceStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles(
        [
            100_000_000,
            110_000_000,
            130_000_000,
        ]
    )

    result = engine.run(candles)

    expected_volume = (
        100_000 / 100_000_000
    )

    expected_position_value = (
        expected_volume * 130_000_000
    )

    expected_final_equity = (
        899_950
        + expected_position_value
    )

    assert result.final_position_volume == pytest.approx(
        expected_volume
    )
    assert result.last_price == pytest.approx(
        130_000_000
    )
    assert result.final_position_value == pytest.approx(
        expected_position_value
    )
    assert result.final_equity == pytest.approx(
        expected_final_equity
    )
    assert result.has_open_position is True
    assert result.completed_trade_count == 0

#보합 거래 처리 테스트
def test_run_breakeven_trade_is_not_win_or_loss():
    config = BacktestConfig(
        buy_fee_rate=0.0,
        sell_fee_rate=0.0,
    )

    strategy = BuyThenSellStrategy()

    engine = BacktestEngine(
        config=config,
        strategy=strategy,
    )

    candles = make_candles(
        [
            100_000_000,
            100_000_000,
        ]
    )

    result = engine.run(candles)

    assert result.completed_trade_count == 1
    assert result.winning_trade_count == 0
    assert result.losing_trade_count == 0
    assert result.win_rate == pytest.approx(
        0.0
    )

    assert result.trades[1].realized_pnl == pytest.approx(
        0.0
    )
'''
def test_run_buy_signal_raises_not_implemented_error():
    strategy = AlwaysBuyStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles([100])

    with pytest.raises(
        NotImplementedError,
        match=(
            "BUY 체결 로직은 아직 "
            "구현되지 않았습니다."
        ),
    ):
        engine.run(candles)
'''
'''
def test_run_sell_signal_raises_not_implemented_error():
    strategy = AlwaysSellStrategy()
    engine = create_default_engine(strategy)

    candles = make_candles([100])

    with pytest.raises(
        NotImplementedError,
        match=(
            "SELL 체결 로직은 아직 "
            "구현되지 않았습니다."
        ),
    ):
        engine.run(candles)
'''
class BuyOnceStrategy:
    def generate_signal(
        self,
        candles,
        has_position,
    ):
        if not has_position:
            return StrategySignal(
                signal_type=SignalType.BUY,
                reason="테스트용 최초 매수",
            )

        return StrategySignal(
            signal_type=SignalType.HOLD,
            reason="테스트용 포지션 유지",
        )

    def test_run_buy_signal_creates_buy_trade(): #BUY 거래 생성 테스트
        strategy = BuyOnceStrategy()
        engine = create_default_engine(strategy)

        candles = make_candles(
            [100_000_000]
        )

        result = engine.run(candles)

        assert result.total_trade_count == 1
        assert len(result.trades) == 1

        trade = result.trades[0]

        assert trade.side == OrderSide.BUY
        assert trade.market == "KRW-BTC"
        assert trade.price == pytest.approx(
            100_000_000
        )
        assert trade.gross_amount == pytest.approx(
            100_000
        )
        assert trade.realized_pnl is None
        assert trade.signal_reason == "테스트용 최초 매수"

    def test_run_buy_calculates_fee(): #매수 수수료 계산 테스트
        strategy = BuyOnceStrategy()
        engine = create_default_engine(strategy)

        candles = make_candles(
            [100_000_000]
        )

        result = engine.run(candles)

        trade = result.trades[0]

        expected_fee = (
            100_000 * 0.0005
        )

        assert trade.fee == pytest.approx(
            expected_fee
        )

    def test_run_buy_calculates_volume(): #매수 수량 계산 테스트
        strategy = BuyOnceStrategy()
        engine = create_default_engine(strategy)

        price = 100_000_000

        candles = make_candles([price])

        result = engine.run(candles)

        trade = result.trades[0]

        expected_volume = (
            100_000 / price
        )

        assert trade.volume == pytest.approx(
            expected_volume
        )
        assert result.final_position_volume == pytest.approx(
            expected_volume
        )

    def test_run_buy_deducts_gross_amount_and_fee_from_cash(): #매수 후 현금 테스트
        strategy = BuyOnceStrategy()
        engine = create_default_engine(strategy)

        candles = make_candles(
            [100_000_000]
        )

        result = engine.run(candles)

        expected_fee = (
            100_000 * 0.0005
        )

        expected_cash = (
            1_000_000
            - 100_000
            - expected_fee
        )

        trade = result.trades[0]

        assert trade.cash_flow == pytest.approx(
            -(100_000 + expected_fee)
        )
        assert trade.cash_after == pytest.approx(
            expected_cash
        )
        assert result.final_cash == pytest.approx(
            expected_cash
        )

    def test_run_buy_reduces_equity_by_buy_fee(): #매수 직후 자산 테스트
        strategy = BuyOnceStrategy()
        engine = create_default_engine(strategy)

        price = 100_000_000

        candles = make_candles([price])

        result = engine.run(candles)

        expected_fee = (
            100_000 * 0.0005
        )

        assert result.final_position_value == pytest.approx(
            100_000
        )
        assert result.final_equity == pytest.approx(
            1_000_000 - expected_fee
        )
        assert result.cumulative_return == pytest.approx(
            -expected_fee / 1_000_000
        )

    def test_run_buy_leaves_open_position(): #미청산 포지션 확인 테스트
        strategy = BuyOnceStrategy()
        engine = create_default_engine(strategy)

        candles = make_candles(
            [100_000_000]
        )

        result = engine.run(candles)

        assert result.has_open_position is True
        assert result.final_position_volume > 0
        assert result.completed_trade_count == 0
        assert result.winning_trade_count == 0
        assert result.losing_trade_count == 0
        assert result.win_rate == pytest.approx(
            0.0
        )

    def test_run_does_not_buy_again_when_position_exists(): #포지션 보유 중 추가 매수 방지 테스트
        strategy = AlwaysBuyStrategy()
        engine = create_default_engine(strategy)

        candles = make_candles(
            [
                100_000_000,
                101_000_000,
                102_000_000,
            ]
        )

        result = engine.run(candles)

        assert result.total_trade_count == 1
        assert len(result.trades) == 1
        assert result.trades[0].side == OrderSide.BUY

    def test_run_records_equity_after_buy(): #자산 곡선 반영 테스트
        strategy = BuyOnceStrategy()
        engine = create_default_engine(strategy)

        prices = [
            100_000_000,
            110_000_000,
        ]

        candles = make_candles(prices)

        result = engine.run(candles)

        expected_volume = (
            100_000 / 100_000_000
        )

        first_record = result.equity_curve[0]
        second_record = result.equity_curve[1]

        assert first_record.cash == pytest.approx(
            899_950
        )
        assert first_record.position_volume == pytest.approx(
            expected_volume
        )
        assert first_record.position_value == pytest.approx(
            100_000
        )
        assert first_record.total_equity == pytest.approx(
            999_950
        )

        assert second_record.cash == pytest.approx(
            899_950
        )
        assert second_record.position_value == pytest.approx(
            110_000
        )
        assert second_record.total_equity == pytest.approx(
            1_009_950
        )

class BuyThenSellStrategy:
    def __init__(self):
        self.call_count = 0

    def generate_signal(
        self,
        candles,
        has_position,
    ):
        self.call_count += 1

        if self.call_count == 1:
            return StrategySignal(
                signal_type=SignalType.BUY,
                reason="테스트용 매수",
            )

        if self.call_count == 2:
            return StrategySignal(
                signal_type=SignalType.SELL,
                reason="테스트용 매도",
            )

        return StrategySignal(
            signal_type=SignalType.HOLD,
            reason="테스트용 관망",
        )
    
    def test_run_sell_signal_creates_sell_trade(): #SELL 거래 생성 테스트
        strategy = BuyThenSellStrategy()
        engine = create_default_engine(strategy)

        candles = make_candles(
            [
                100_000_000,
                110_000_000,
            ]
        )

        result = engine.run(candles)

        assert result.total_trade_count == 2
        assert len(result.trades) == 2

        buy_trade = result.trades[0]
        sell_trade = result.trades[1]

        assert buy_trade.side == OrderSide.BUY
        assert sell_trade.side == OrderSide.SELL

        assert sell_trade.price == pytest.approx(
            110_000_000
        )
        assert sell_trade.volume == pytest.approx(
            buy_trade.volume
        )
        assert sell_trade.position_volume_after == pytest.approx(
            0.0
        )
        assert sell_trade.signal_reason == "테스트용 매도"

    def test_run_sell_calculates_fee(): #매도 수수료 테스트
        strategy = BuyThenSellStrategy()
        engine = create_default_engine(strategy)

        candles = make_candles(
            [
                100_000_000,
                110_000_000,
            ]
        )

        result = engine.run(candles)

        sell_trade = result.trades[1]

        expected_volume = (
            100_000 / 100_000_000
        )

        expected_gross_amount = (
            110_000_000 * expected_volume
        )

        expected_fee = (
            expected_gross_amount * 0.0005
        )

        assert sell_trade.gross_amount == pytest.approx(
            expected_gross_amount
        )
        assert sell_trade.fee == pytest.approx(
            expected_fee
        )

    def test_run_sell_adds_net_proceeds_to_cash(): #매도 후 현금 테스트
        strategy = BuyThenSellStrategy()
        engine = create_default_engine(strategy)

        candles = make_candles(
            [
                100_000_000,
                110_000_000,
            ]
        )

        result = engine.run(candles)

        expected_buy_fee = (
            100_000 * 0.0005
        )

        cash_after_buy = (
            1_000_000
            - 100_000
            - expected_buy_fee
        )

        expected_volume = (
            100_000 / 100_000_000
        )

        sell_gross_amount = (
            110_000_000 * expected_volume
        )

        expected_sell_fee = (
            sell_gross_amount * 0.0005
        )

        expected_net_proceeds = (
            sell_gross_amount
            - expected_sell_fee
        )

        expected_final_cash = (
            cash_after_buy
            + expected_net_proceeds
        )

        sell_trade = result.trades[1]

        assert sell_trade.cash_flow == pytest.approx(
            expected_net_proceeds
        )
        assert sell_trade.cash_after == pytest.approx(
            expected_final_cash
        )
        assert result.final_cash == pytest.approx(
            expected_final_cash
        )

    def test_run_sell_calculates_realized_pnl(): #실현 손익 테스트
        strategy = BuyThenSellStrategy()
        engine = create_default_engine(strategy)

        candles = make_candles(
            [
                100_000_000,
                110_000_000,
            ]
        )

        result = engine.run(candles)

        buy_total_cost = (
            100_000
            + 100_000 * 0.0005
        )

        volume = (
            100_000 / 100_000_000
        )

        sell_gross_amount = (
            110_000_000 * volume
        )

        sell_fee = (
            sell_gross_amount * 0.0005
        )

        sell_net_proceeds = (
            sell_gross_amount - sell_fee
        )

        expected_realized_pnl = (
            sell_net_proceeds - buy_total_cost
        )

        sell_trade = result.trades[1]

        assert sell_trade.realized_pnl == pytest.approx(
            expected_realized_pnl
        )

    def test_run_sell_closes_position(): #매도 후 포지션 제거 테스트
        strategy = BuyThenSellStrategy()
        engine = create_default_engine(strategy)

        candles = make_candles(
            [
                100_000_000,
                110_000_000,
            ]
        )

        result = engine.run(candles)

        assert result.final_position_volume == pytest.approx(
            0.0
        )
        assert result.final_position_value == pytest.approx(
            0.0
        )
        assert result.has_open_position is False

    def test_run_profitable_sell_updates_trade_statistics(): #완료 거래와 승률 테스트
        strategy = BuyThenSellStrategy()
        engine = create_default_engine(strategy)

        candles = make_candles(
            [
                100_000_000,
                110_000_000,
            ]
        )

        result = engine.run(candles)

        assert result.total_trade_count == 2
        assert result.completed_trade_count == 1
        assert result.winning_trade_count == 1
        assert result.losing_trade_count == 0
        assert result.win_rate == pytest.approx(
            1.0
        )

    def test_run_losing_sell_updates_trade_statistics(): #손실 거래 테스트
        strategy = BuyThenSellStrategy()
        engine = create_default_engine(strategy)

        candles = make_candles(
            [
                100_000_000,
                90_000_000,
            ]
        )

        result = engine.run(candles)

        assert result.completed_trade_count == 1
        assert result.winning_trade_count == 0
        assert result.losing_trade_count == 1
        assert result.win_rate == pytest.approx(
            0.0
        )

        sell_trade = result.trades[1]

        assert sell_trade.realized_pnl < 0

    def test_run_sell_without_position_does_not_create_trade(): #포지션이 없는 SELL 신호 테스트
        strategy = AlwaysSellStrategy()
        engine = create_default_engine(strategy)

        candles = make_candles(
            [100_000_000]
        )

        result = engine.run(candles)

        assert result.total_trade_count == 0
        assert result.trades == []
        assert result.final_cash == pytest.approx(
            1_000_000
        )
        assert result.final_position_volume == pytest.approx(
            0.0
        )
        assert result.has_open_position is False

    def test_run_records_equity_after_sell(): #매도 시점 자산 곡선 테스트
        strategy = BuyThenSellStrategy()
        engine = create_default_engine(strategy)

        candles = make_candles(
            [
                100_000_000,
                110_000_000,
            ]
        )

        result = engine.run(candles)

        second_record = result.equity_curve[1]

        assert second_record.position_volume == pytest.approx(
            0.0
        )
        assert second_record.position_value == pytest.approx(
            0.0
        )
        assert second_record.cash == pytest.approx(
            result.final_cash
        )
        assert second_record.total_equity == pytest.approx(
            result.final_cash
        )

    def test_run_completed_trade_calculates_final_equity_and_return(): #최종 자산과 수익률 테스트
        strategy = BuyThenSellStrategy()
        engine = create_default_engine(strategy)

        candles = make_candles(
            [
                100_000_000,
                110_000_000,
            ]
        )

        result = engine.run(candles)

        expected_realized_pnl = 9_895

        assert result.final_equity == pytest.approx(
            1_000_000 + expected_realized_pnl
        )

        assert result.cumulative_return == pytest.approx(
            expected_realized_pnl / 1_000_000
        )

    def test_run_with_moving_average_strategy_completes_trade(): #실제 이동평균전략 매수/매도 통합 단위 테스트
        strategy = MovingAverageStrategy(
            short_window=2,
            long_window=3,
        )

        engine = create_default_engine(strategy)

        candles = make_candles(
            [
                100,
                100,
                110,
                120,
                90,
                80,
            ]
        )

        result = engine.run(candles)

        assert result.total_trade_count == 2
        assert result.completed_trade_count == 1
        assert result.has_open_position is False
        assert result.trades[0].side == OrderSide.BUY
        assert result.trades[1].side == OrderSide.SELL

#여러 완료 거래를 위한 테스트 전략
class SequenceStrategy:
    def __init__(self, signals):
        self.signals = signals
        self.index = 0

    def generate_signal(
        self,
        candles,
        has_position,
    ):
        signal_type = self.signals[
            self.index
        ]
        self.index += 1

        return StrategySignal(
            signal_type=signal_type,
            reason=f"테스트 신호: {signal_type.value}",
        )

#여러 거래 승률 테스트
def test_run_calculates_statistics_for_multiple_trades():
    strategy = SequenceStrategy(
        [
            SignalType.BUY,
            SignalType.SELL,
            SignalType.BUY,
            SignalType.SELL,
        ]
    )

    engine = create_default_engine(strategy)

    candles = make_candles(
        [
            100_000_000,
            110_000_000,
            100_000_000,
            90_000_000,
        ]
    )

    result = engine.run(candles)

    assert result.total_trade_count == 4
    assert result.completed_trade_count == 2
    assert result.winning_trade_count == 1
    assert result.losing_trade_count == 1
    assert result.win_rate == pytest.approx(
        0.5
    )