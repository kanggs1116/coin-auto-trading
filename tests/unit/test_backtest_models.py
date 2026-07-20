from datetime import datetime

import pytest

from backtest.backtest_models import (
    BacktestResult,
    EquityRecord,
    TradeRecord,
)
from trading.order_types import OrderSide


def test_trade_record_stores_buy_trade_data():
    timestamp = datetime(2026, 1, 1, 0, 0)

    trade = TradeRecord(
        timestamp=timestamp,
        market="KRW-BTC",
        side=OrderSide.BUY,
        price=100_000_000,
        volume=0.001,
        gross_amount=100_000,
        fee=50,
        cash_flow=-100_050,
        cash_after=899_950,
        position_volume_after=0.001,
        realized_pnl=None,
        signal_reason="매수 조건 충족",
    )

    assert trade.timestamp == timestamp
    assert trade.market == "KRW-BTC"
    assert trade.side == OrderSide.BUY
    assert trade.price == pytest.approx(100_000_000)
    assert trade.volume == pytest.approx(0.001)
    assert trade.gross_amount == pytest.approx(100_000)
    assert trade.fee == pytest.approx(50)
    assert trade.cash_flow == pytest.approx(-100_050)
    assert trade.cash_after == pytest.approx(899_950)
    assert trade.position_volume_after == pytest.approx(0.001)
    assert trade.realized_pnl is None
    assert trade.signal_reason == "매수 조건 충족"


def test_trade_record_stores_sell_trade_data():
    timestamp = datetime(2026, 1, 1, 1, 0)

    trade = TradeRecord(
        timestamp=timestamp,
        market="KRW-BTC",
        side=OrderSide.SELL,
        price=110_000_000,
        volume=0.001,
        gross_amount=110_000,
        fee=55,
        cash_flow=109_945,
        cash_after=1_009_895,
        position_volume_after=0.0,
        realized_pnl=9_895,
        signal_reason="매도 조건 충족",
    )

    assert trade.side == OrderSide.SELL
    assert trade.cash_flow == pytest.approx(109_945)
    assert trade.position_volume_after == pytest.approx(0.0)
    assert trade.realized_pnl == pytest.approx(9_895)


def test_equity_record_stores_account_state():
    timestamp = datetime(2026, 1, 1, 0, 1)

    record = EquityRecord(
        timestamp=timestamp,
        price=110_000_000,
        cash=899_950,
        position_volume=0.001,
        position_value=110_000,
        total_equity=1_009_950,
    )

    assert record.timestamp == timestamp
    assert record.price == pytest.approx(110_000_000)
    assert record.cash == pytest.approx(899_950)
    assert record.position_volume == pytest.approx(0.001)
    assert record.position_value == pytest.approx(110_000)
    assert record.total_equity == pytest.approx(1_009_950)


def test_backtest_result_stores_summary_and_records():
    start_time = datetime(2026, 1, 1, 0, 0)
    end_time = datetime(2026, 1, 1, 1, 0)

    buy_trade = TradeRecord(
        timestamp=start_time,
        market="KRW-BTC",
        side=OrderSide.BUY,
        price=100_000_000,
        volume=0.001,
        gross_amount=100_000,
        fee=50,
        cash_flow=-100_050,
        cash_after=899_950,
        position_volume_after=0.001,
    )

    equity_record = EquityRecord(
        timestamp=end_time,
        price=110_000_000,
        cash=899_950,
        position_volume=0.001,
        position_value=110_000,
        total_equity=1_009_950,
    )

    result = BacktestResult(
        market="KRW-BTC",
        candle_count=61,
        start_time=start_time,
        end_time=end_time,
        initial_capital=1_000_000,
        final_cash=899_950,
        final_position_volume=0.001,
        last_price=110_000_000,
        final_position_value=110_000,
        final_equity=1_009_950,
        cumulative_return=0.00995,
        total_trade_count=1,
        completed_trade_count=0,
        winning_trade_count=0,
        losing_trade_count=0,
        win_rate=0.0,
        max_drawdown=0.002,
        has_open_position=True,
        trades=[buy_trade],
        equity_curve=[equity_record],
    )

    assert result.market == "KRW-BTC"
    assert result.candle_count == 61
    assert result.initial_capital == pytest.approx(1_000_000)
    assert result.final_equity == pytest.approx(1_009_950)
    assert result.cumulative_return == pytest.approx(0.00995)
    assert result.total_trade_count == 1
    assert result.completed_trade_count == 0
    assert result.has_open_position is True
    assert result.trades == [buy_trade]
    assert result.equity_curve == [equity_record]


def test_backtest_result_uses_independent_default_lists():
    start_time = datetime(2026, 1, 1, 0, 0)
    end_time = datetime(2026, 1, 1, 0, 1)

    first = BacktestResult(
        market="KRW-BTC",
        candle_count=2,
        start_time=start_time,
        end_time=end_time,
        initial_capital=1_000_000,
        final_cash=1_000_000,
        final_position_volume=0.0,
        last_price=100_000_000,
        final_position_value=0.0,
        final_equity=1_000_000,
        cumulative_return=0.0,
        total_trade_count=0,
        completed_trade_count=0,
        winning_trade_count=0,
        losing_trade_count=0,
        win_rate=0.0,
        max_drawdown=0.0,
        has_open_position=False,
    )

    second = BacktestResult(
        market="KRW-BTC",
        candle_count=2,
        start_time=start_time,
        end_time=end_time,
        initial_capital=1_000_000,
        final_cash=1_000_000,
        final_position_volume=0.0,
        last_price=100_000_000,
        final_position_value=0.0,
        final_equity=1_000_000,
        cumulative_return=0.0,
        total_trade_count=0,
        completed_trade_count=0,
        winning_trade_count=0,
        losing_trade_count=0,
        win_rate=0.0,
        max_drawdown=0.0,
        has_open_position=False,
    )

    assert first.trades is not second.trades
    assert first.equity_curve is not second.equity_curve