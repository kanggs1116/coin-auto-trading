import time

from strategy.moving_average_strategy import MovingAverageStrategy
from strategy.strategy_signal import SignalType
from trading.trading_config import (
    MARKET,
    CANDLE_UNIT,
    CANDLE_COUNT,
    SHORT_WINDOW,
    LONG_WINDOW,
    ORDER_AMOUNT_KRW,
    TRADING_INTERVAL_SECONDS,
)


class PaperTradingRunner:
    def __init__(
        self,
        upbit_client,
        order_service,
        position_manager,
    ):
        self.upbit_client = upbit_client
        self.order_service = order_service
        self.position_manager = position_manager

        self.strategy = MovingAverageStrategy(
            short_window=SHORT_WINDOW,
            long_window=LONG_WINDOW,
        )

    def run_once(self):
        candles = self.upbit_client.get_minute_candles(
            market=MARKET,
            unit=CANDLE_UNIT,
            count=CANDLE_COUNT,
        )

        candles = list(reversed(candles))
        current_price = float(candles[-1]["trade_price"])

        self.order_service.update_current_price(
            market=MARKET,
            price=current_price,
        )

        position = self.position_manager.get_position(MARKET)
        has_position = position is not None

        signal = self.strategy.generate_signal(
            candles=candles,
            has_position=has_position,
        )

        self._print_market_status(
            current_price=current_price,
            position=position,
            signal=signal,
        )

        if signal.signal_type == SignalType.BUY:
            order = self.order_service.buy_market(
                market=MARKET,
                krw_amount=ORDER_AMOUNT_KRW,
            )
            self._print_buy_order(order)

        elif signal.signal_type == SignalType.SELL:
            order = self.order_service.sell_market(
                market=MARKET,
                volume=position.volume,
            )
            self._print_sell_order(order)

        else:
            print("[ACTION] HOLD")

    def run_forever(self):
        print("[PAPER TRADING START]")

        while True:
            try:
                self.run_once()
                time.sleep(TRADING_INTERVAL_SECONDS)

            except KeyboardInterrupt:
                print("[PAPER TRADING STOP]")
                break

            except Exception as e:
                print(f"[ERROR] {e}")
                time.sleep(TRADING_INTERVAL_SECONDS)

    def _print_market_status(self, current_price, position, signal):
        print("=" * 60)
        print(f"[MARKET] {MARKET}")
        print(f"[PRICE] {current_price:,.0f}원")
        print()
        print("[POSITION]")

        if position is None:
            print("보유 포지션 없음")
        else:
            current_value = position.volume * current_price
            profit_loss = current_value - position.total_value
            profit_loss_rate = (profit_loss / position.total_value) * 100

            print(f"보유 수량 : {position.volume:.8f}")
            print(f"평균 단가 : {position.avg_price:,.0f}원")
            print(f"평가 금액 : {current_value:,.0f}원")
            print(f"평가 손익 : {profit_loss:,.0f}원")
            print(f"수익률 : {profit_loss_rate:.2f}%")

        print()
        print("[SIGNAL]")
        print(signal.signal_type.value)
        print()
        print("[REASON]")
        print(signal.reason)

    def _print_buy_order(self, order):
        print()
        print("[ORDER]")
        print("매수 완료")
        print(f"주문 금액 : {order.krw_amount:,.0f}원")
        print(f"체결 가격 : {order.executed_price:,.0f}원")
        print(f"체결 수량 : {order.executed_volume:.8f}")
        print(f"수수료 : {order.fee:,.0f}원")

    def _print_sell_order(self, order):
        print()
        print("[ORDER]")
        print("매도 완료")
        print(f"체결 가격 : {order.executed_price:,.0f}원")
        print(f"매도 수량 : {order.executed_volume:.8f}")
        print(f"수수료 : {order.fee:,.0f}원")