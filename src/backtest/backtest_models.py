from dataclasses import dataclass, field
from datetime import datetime

from trading.order_types import OrderSide


@dataclass(frozen=True)
class TradeRecord:
    timestamp: datetime
    market: str
    side: OrderSide

    price: float
    volume: float
    gross_amount: float
    fee: float
    cash_flow: float

    cash_after: float
    position_volume_after: float

    realized_pnl: float | None = None
    signal_reason: str = ""


@dataclass(frozen=True)
class EquityRecord:
    timestamp: datetime
    price: float

    cash: float
    position_volume: float
    position_value: float
    total_equity: float


@dataclass(frozen=True)
class BacktestResult:
    market: str
    candle_count: int
    start_time: datetime
    end_time: datetime

    initial_capital: float
    final_cash: float
    final_position_volume: float
    last_price: float
    final_position_value: float
    final_equity: float
    cumulative_return: float

    total_trade_count: int
    completed_trade_count: int
    winning_trade_count: int
    losing_trade_count: int
    win_rate: float
    max_drawdown: float

    has_open_position: bool

    trades: list[TradeRecord] = field(default_factory=list)
    equity_curve: list[EquityRecord] = field(default_factory=list)