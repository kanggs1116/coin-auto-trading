from typing import Any

from backtest.backtest_config import BacktestConfig
from backtest.backtest_models import (
    BacktestResult,
    EquityRecord,
    TradeRecord,
)
from strategy.strategy_signal import SignalType
from trading.order_types import OrderSide


PNL_EPSILON = 1e-9


class BacktestEngine:
    def __init__(
        self,
        config: BacktestConfig,
        strategy: Any,
    ):
        self.config = config
        self.strategy = strategy

    def run(
        self,
        candles: list[dict],
    ) -> BacktestResult:
        """
        과거 캔들을 시간순으로 순회하면서 백테스트를 실행한다.

        현재 구현 범위:
        - BUY 시장가 가상 체결
        - SELL 전량 가상 체결
        - 매수·매도 수수료 반영
        - 실현 손익 계산
        - 거래 및 자산 변화 기록
        """
        self._validate_candles(candles)

        cash = float(self.config.initial_capital)

        position_volume = 0.0
        entry_price = 0.0
        entry_total_cost = 0.0
        entry_fee = 0.0

        completed_trade_count = 0
        winning_trade_count = 0
        losing_trade_count = 0

        trades: list[TradeRecord] = []
        equity_curve: list[EquityRecord] = []

        for index, current_candle in enumerate(candles):
            visible_candles = candles[:index + 1]

            has_position = position_volume > 0

            signal = self.strategy.generate_signal(
                candles=visible_candles,
                has_position=has_position,
            )

            current_price = float(
                current_candle["trade_price"]
            )
            current_time = current_candle[
                "candle_date_time_utc"
            ]

            if signal.signal_type == SignalType.BUY:
                (
                    cash,
                    position_volume,
                    entry_price,
                    entry_total_cost,
                    entry_fee,
                    buy_trade,
                ) = self._execute_buy(
                    timestamp=current_time,
                    price=current_price,
                    cash=cash,
                    position_volume=position_volume,
                    entry_price=entry_price,
                    entry_total_cost=entry_total_cost,
                    entry_fee=entry_fee,
                    signal_reason=signal.reason,
                )

                if buy_trade is not None:
                    trades.append(buy_trade)

            elif signal.signal_type == SignalType.SELL:
                (
                    cash,
                    position_volume,
                    realized_pnl,
                    sell_trade,
                ) = self._execute_sell(
                    timestamp=current_time,
                    price=current_price,
                    cash=cash,
                    position_volume=position_volume,
                    entry_total_cost=entry_total_cost,
                    signal_reason=signal.reason,
                )

                if sell_trade is not None:
                    trades.append(sell_trade)
                    completed_trade_count += 1

                    if realized_pnl > PNL_EPSILON:
                        winning_trade_count += 1
                    elif realized_pnl < -PNL_EPSILON:
                        losing_trade_count += 1

                    entry_price = 0.0
                    entry_total_cost = 0.0
                    entry_fee = 0.0

            position_value = (
                position_volume * current_price
            )

            total_equity = (
                cash + position_value
            )

            equity_curve.append(
                EquityRecord(
                    timestamp=current_time,
                    price=current_price,
                    cash=cash,
                    position_volume=position_volume,
                    position_value=position_value,
                    total_equity=total_equity,
                )
            )

        first_candle = candles[0]
        last_candle = candles[-1]

        last_price = float(
            last_candle["trade_price"]
        )

        final_position_value = (
            position_volume * last_price
        )

        final_equity = (
            cash + final_position_value
        )

        cumulative_return = (
            final_equity
            - self.config.initial_capital
        ) / self.config.initial_capital

        win_rate = (
            winning_trade_count
            / completed_trade_count
            if completed_trade_count > 0
            else 0.0
        )

        max_drawdown = (
            self._calculate_max_drawdown(
                equity_curve
            )
        )

        return BacktestResult(
            market=self.config.market,
            candle_count=len(candles),
            start_time=first_candle[
                "candle_date_time_utc"
            ],
            end_time=last_candle[
                "candle_date_time_utc"
            ],
            initial_capital=float(
                self.config.initial_capital
            ),
            final_cash=cash,
            final_position_volume=position_volume,
            last_price=last_price,
            final_position_value=final_position_value,
            final_equity=final_equity,
            cumulative_return=cumulative_return,
            total_trade_count=len(trades),
            completed_trade_count=completed_trade_count,
            winning_trade_count=winning_trade_count,
            losing_trade_count=losing_trade_count,
            win_rate=win_rate,
            max_drawdown=max_drawdown,
            has_open_position=position_volume > 0,
            trades=trades,
            equity_curve=equity_curve,
        )

    def _execute_buy(
        self,
        timestamp,
        price: float,
        cash: float,
        position_volume: float,
        entry_price: float,
        entry_total_cost: float,
        entry_fee: float,
        signal_reason: str,
    ) -> tuple[
        float,
        float,
        float,
        float,
        float,
        TradeRecord | None,
    ]:
        """
        BUY 신호를 시장가로 가상 체결한다.

        포지션이 이미 있거나 수수료 포함 필요 현금이 부족하면
        기존 상태를 유지하고 거래를 생성하지 않는다.
        """
        if position_volume > 0:
            return (
                cash,
                position_volume,
                entry_price,
                entry_total_cost,
                entry_fee,
                None,
            )

        gross_amount = float(
            self.config.order_amount_krw
        )

        fee = (
            gross_amount
            * self.config.buy_fee_rate
        )

        total_cash_outflow = (
            gross_amount + fee
        )

        if cash < total_cash_outflow:
            return (
                cash,
                position_volume,
                entry_price,
                entry_total_cost,
                entry_fee,
                None,
            )

        volume = (
            gross_amount / price
        )

        cash_after = (
            cash - total_cash_outflow
        )

        trade = TradeRecord(
            timestamp=timestamp,
            market=self.config.market,
            side=OrderSide.BUY,
            price=price,
            volume=volume,
            gross_amount=gross_amount,
            fee=fee,
            cash_flow=-total_cash_outflow,
            cash_after=cash_after,
            position_volume_after=volume,
            realized_pnl=None,
            signal_reason=signal_reason,
        )

        return (
            cash_after,
            volume,
            price,
            total_cash_outflow,
            fee,
            trade,
        )

    def _execute_sell(
        self,
        timestamp,
        price: float,
        cash: float,
        position_volume: float,
        entry_total_cost: float,
        signal_reason: str,
    ) -> tuple[
        float,
        float,
        float,
        TradeRecord | None,
    ]:
        """
        현재 보유 수량 전부를 시장가로 가상 매도한다.

        포지션이 없으면 거래를 생성하지 않고 기존 상태를 반환한다.
        """
        if position_volume <= 0:
            return (
                cash,
                position_volume,
                0.0,
                None,
            )

        gross_amount = (
            price * position_volume
        )

        fee = (
            gross_amount
            * self.config.sell_fee_rate
        )

        net_proceeds = (
            gross_amount - fee
        )

        cash_after = (
            cash + net_proceeds
        )

        realized_pnl = (
            net_proceeds - entry_total_cost
        )

        trade = TradeRecord(
            timestamp=timestamp,
            market=self.config.market,
            side=OrderSide.SELL,
            price=price,
            volume=position_volume,
            gross_amount=gross_amount,
            fee=fee,
            cash_flow=net_proceeds,
            cash_after=cash_after,
            position_volume_after=0.0,
            realized_pnl=realized_pnl,
            signal_reason=signal_reason,
        )

        return (
            cash_after,
            0.0,
            realized_pnl,
            trade,
        )

    def _validate_candles(
        self,
        candles: list[dict],
    ) -> None:
        if not candles:
            raise ValueError(
                "백테스트에 사용할 캔들 데이터가 없습니다."
            )

        required_fields = {
            "candle_date_time_utc",
            "trade_price",
        }

        previous_time = None

        for index, candle in enumerate(candles):
            missing_fields = (
                required_fields - candle.keys()
            )

            if missing_fields:
                missing_text = ", ".join(
                    sorted(missing_fields)
                )

                raise ValueError(
                    f"{index}번 캔들에 필수 필드가 없습니다: "
                    f"{missing_text}"
                )

            current_time = candle[
                "candle_date_time_utc"
            ]

            current_price = float(
                candle["trade_price"]
            )

            if current_price <= 0:
                raise ValueError(
                    f"{index}번 캔들의 trade_price는 "
                    "0보다 커야 합니다."
                )

            if (
                previous_time is not None
                and current_time <= previous_time
            ):
                raise ValueError(
                    "캔들은 중복 없이 과거에서 최신 "
                    "순서로 정렬되어야 합니다."
                )

            previous_time = current_time

    def _calculate_max_drawdown(
        self,
        equity_curve: list[EquityRecord],
    ) -> float:
        """
        초기 자본과 시점별 총자산을 기준으로 최대 낙폭을 계산한다.

        Returns:
            0 이상 1 이하의 비율.
            예: 0.15는 MDD 15%를 의미한다.
        """
        peak_equity = float(
            self.config.initial_capital
        )
        max_drawdown = 0.0

        for record in equity_curve:
            current_equity = record.total_equity

            if current_equity > peak_equity:
                peak_equity = current_equity

            drawdown = (
                peak_equity - current_equity
            ) / peak_equity

            if drawdown > max_drawdown:
                max_drawdown = drawdown

        return max_drawdown