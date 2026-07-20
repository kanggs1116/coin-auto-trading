from datetime import datetime

import pytest

from backtest.backtest_config import BacktestConfig
from backtest.backtest_models import (
    BacktestResult,
    EquityRecord,
    TradeRecord,
)
from run_backtest import (
    format_krw,
    format_percent,
    format_realized_pnl,
    format_volume,
    print_backtest_summary,
    print_trade_history,
)
from strategy.moving_average_strategy import MovingAverageStrategy
from trading.order_types import OrderSide


def test_format_krw():
    assert format_krw(1_000_000) == "1,000,000원"
    assert format_krw(-100_050) == "-100,050원"
    assert format_krw(50.4) == "50원"


def test_format_percent():
    assert format_percent(0.05) == "5.00%"
    assert format_percent(-0.001) == "-0.10%"
    assert format_percent(0.0) == "0.00%"


def test_format_volume():
    assert format_volume(0.001) == "0.00100000"
    assert format_volume(0.0) == "0.00000000"


def test_format_realized_pnl_none_returns_dash():
    assert format_realized_pnl(None) == "-"


def test_format_realized_pnl_value_returns_krw():
    assert format_realized_pnl(9_895) == "9,895원"


def make_result(
    trades=None,
) -> BacktestResult:
    start_time = datetime(
        2026,
        1,
        1,
        0,
        0,
    )
    end_time = datetime(
        2026,
        1,
        1,
        1,
        0,
    )

    if trades is None:
        trades = []

    equity_record = EquityRecord(
        timestamp=end_time,
        price=110_000_000,
        cash=1_009_895,
        position_volume=0.0,
        position_value=0.0,
        total_equity=1_009_895,
    )

    return BacktestResult(
        market="KRW-BTC",
        candle_count=61,
        start_time=start_time,
        end_time=end_time,
        initial_capital=1_000_000,
        final_cash=1_009_895,
        final_position_volume=0.0,
        last_price=110_000_000,
        final_position_value=0.0,
        final_equity=1_009_895,
        cumulative_return=0.009895,
        total_trade_count=len(trades),
        completed_trade_count=1 if len(trades) >= 2 else 0,
        winning_trade_count=1 if len(trades) >= 2 else 0,
        losing_trade_count=0,
        win_rate=1.0 if len(trades) >= 2 else 0.0,
        max_drawdown=0.00005,
        has_open_position=False,
        trades=trades,
        equity_curve=[equity_record],
    )


def test_print_backtest_summary_outputs_key_metrics(
    capsys,
):
    config = BacktestConfig()

    strategy = MovingAverageStrategy(
        short_window=5,
        long_window=20,
    )

    result = make_result()

    print_backtest_summary(
        result=result,
        config=config,
        strategy=strategy,
    )

    captured = capsys.readouterr()

    assert "[BACKTEST RESULT]" in captured.out
    assert "KRW-BTC" in captured.out
    assert "1,000,000원" in captured.out
    assert "1,009,895원" in captured.out
    assert "0.99%" in captured.out
    assert "0.01%" in captured.out


def test_print_trade_history_without_trades(
    capsys,
):
    print_trade_history([])

    captured = capsys.readouterr()

    assert "[TRADES]" in captured.out
    assert "체결된 거래가 없습니다." in captured.out


def test_print_trade_history_outputs_trade_data(
    capsys,
):
    timestamp = datetime(
        2026,
        1,
        1,
        0,
        0,
    )

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
        signal_reason="테스트용 매수",
    )

    print_trade_history([trade])

    captured = capsys.readouterr()

    assert "[TRADES]" in captured.out
    assert "[1] 매수" in captured.out
    assert "100,000,000원" in captured.out
    assert "0.00100000 BTC" in captured.out
    assert "-100,050원" in captured.out
    assert "테스트용 매수" in captured.out