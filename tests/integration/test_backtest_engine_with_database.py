from decimal import Decimal

import pytest

from backtest.backtest_config import BacktestConfig
from backtest.backtest_engine import BacktestEngine
from database.candle_repository import get_recent_minute_candles
from strategy.moving_average_strategy import MovingAverageStrategy
from trading.order_types import OrderSide


MARKET = "KRW-BTC"
CANDLE_UNIT = 1
TEST_CANDLE_LIMIT = 200

SHORT_WINDOW = 5
LONG_WINDOW = 20


@pytest.fixture(scope="module")
def database_candles():
    candles = get_recent_minute_candles(
        market=MARKET,
        unit=CANDLE_UNIT,
        limit=TEST_CANDLE_LIMIT,
    )

    if len(candles) < LONG_WINDOW:
        pytest.skip(
            "이동평균 백테스트에 필요한 DB 캔들 수가 부족합니다. "
            f"필요: {LONG_WINDOW}개 이상, 현재: {len(candles)}개"
        )

    return candles


@pytest.fixture(scope="module")
def backtest_result(database_candles):
    config = BacktestConfig(
        market=MARKET,
        candle_type="minute",
        candle_unit=CANDLE_UNIT,
        initial_capital=1_000_000,
        order_amount_krw=100_000,
        buy_fee_rate=0.0005,
        sell_fee_rate=0.0005,
    )

    strategy = MovingAverageStrategy(
        short_window=SHORT_WINDOW,
        long_window=LONG_WINDOW,
    )

    engine = BacktestEngine(
        config=config,
        strategy=strategy,
    )

    return engine.run(database_candles)


def test_database_candles_are_returned(
    database_candles,
):
    assert len(database_candles) >= LONG_WINDOW
    assert len(database_candles) <= TEST_CANDLE_LIMIT


def test_database_candles_have_required_fields(
    database_candles,
):
    required_fields = {
        "market",
        "candle_type",
        "unit",
        "candle_date_time_utc",
        "trade_price",
    }

    for candle in database_candles:
        assert required_fields.issubset(
            candle.keys()
        )


def test_database_candles_match_requested_market_and_unit(
    database_candles,
):
    for candle in database_candles:
        assert candle["market"] == MARKET
        assert candle["candle_type"] == "minute"
        assert candle["unit"] == CANDLE_UNIT


def test_database_candles_are_oldest_to_newest(
    database_candles,
):
    candle_times = [
        candle["candle_date_time_utc"]
        for candle in database_candles
    ]

    assert candle_times == sorted(candle_times)


def test_database_candles_have_unique_times(
    database_candles,
):
    candle_times = [
        candle["candle_date_time_utc"]
        for candle in database_candles
    ]

    assert len(candle_times) == len(
        set(candle_times)
    )


def test_database_trade_price_can_be_converted_to_float(
    database_candles,
):
    for candle in database_candles:
        price = float(candle["trade_price"])

        assert price > 0


def test_database_numeric_values_may_be_decimal(
    database_candles,
):
    trade_price = database_candles[0][
        "trade_price"
    ]

    assert isinstance(
        trade_price,
        (Decimal, int, float),
    )


def test_backtest_result_uses_all_database_candles(
    database_candles,
    backtest_result,
):
    assert backtest_result.candle_count == len(
        database_candles
    )

    assert len(
        backtest_result.equity_curve
    ) == len(database_candles)


def test_backtest_result_period_matches_database_candles(
    database_candles,
    backtest_result,
):
    assert backtest_result.start_time == (
        database_candles[0][
            "candle_date_time_utc"
        ]
    )

    assert backtest_result.end_time == (
        database_candles[-1][
            "candle_date_time_utc"
        ]
    )

    assert backtest_result.last_price == pytest.approx(
        float(
            database_candles[-1][
                "trade_price"
            ]
        )
    )


def test_backtest_result_has_valid_asset_values(
    backtest_result,
):
    assert backtest_result.initial_capital == pytest.approx(
        1_000_000
    )

    assert backtest_result.final_cash >= 0
    assert backtest_result.final_position_volume >= 0
    assert backtest_result.final_position_value >= 0
    assert backtest_result.final_equity >= 0


def test_backtest_final_equity_matches_cash_and_position_value(
    backtest_result,
):
    expected_final_equity = (
        backtest_result.final_cash
        + backtest_result.final_position_value
    )

    assert backtest_result.final_equity == pytest.approx(
        expected_final_equity
    )


def test_backtest_cumulative_return_matches_final_equity(
    backtest_result,
):
    expected_return = (
        backtest_result.final_equity
        - backtest_result.initial_capital
    ) / backtest_result.initial_capital

    assert backtest_result.cumulative_return == pytest.approx(
        expected_return
    )


def test_backtest_trade_count_matches_trade_records(
    backtest_result,
):
    assert backtest_result.total_trade_count == len(
        backtest_result.trades
    )


def test_backtest_trade_records_are_valid(
    backtest_result,
):
    for trade in backtest_result.trades:
        assert trade.market == MARKET
        assert trade.side in {
            OrderSide.BUY,
            OrderSide.SELL,
        }

        assert trade.price > 0
        assert trade.volume > 0
        assert trade.gross_amount > 0
        assert trade.fee >= 0
        assert trade.cash_after >= 0
        assert trade.position_volume_after >= 0


def test_backtest_completed_trade_count_is_valid(
    backtest_result,
):
    assert backtest_result.completed_trade_count >= 0

    assert (
        backtest_result.completed_trade_count
        <= backtest_result.total_trade_count // 2
    )


def test_backtest_win_loss_counts_are_valid(
    backtest_result,
):
    assert backtest_result.winning_trade_count >= 0
    assert backtest_result.losing_trade_count >= 0

    assert (
        backtest_result.winning_trade_count
        + backtest_result.losing_trade_count
        <= backtest_result.completed_trade_count
    )


def test_backtest_win_rate_is_valid(
    backtest_result,
):
    assert 0.0 <= backtest_result.win_rate <= 1.0

    if backtest_result.completed_trade_count == 0:
        assert backtest_result.win_rate == pytest.approx(
            0.0
        )


def test_backtest_max_drawdown_is_valid(
    backtest_result,
):
    assert 0.0 <= backtest_result.max_drawdown <= 1.0


def test_backtest_equity_records_are_valid(
    backtest_result,
):
    for record in backtest_result.equity_curve:
        assert record.price > 0
        assert record.cash >= 0
        assert record.position_volume >= 0
        assert record.position_value >= 0
        assert record.total_equity >= 0

        expected_total_equity = (
            record.cash
            + record.position_value
        )

        assert record.total_equity == pytest.approx(
            expected_total_equity
        )


def test_backtest_open_position_flag_matches_volume(
    backtest_result,
):
    assert backtest_result.has_open_position == (
        backtest_result.final_position_volume > 0
    )