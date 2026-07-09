import pytest

from trading.paper_trading_runner import PaperTradingRunner
from trading.paper_order_service import PaperOrderService
from trading.position import PositionManager
from trading.risk_manager import RiskManager
from trading.order_types import OrderSide


class FakeUpbitClient:
    def __init__(self, candles):
        self.candles = candles

    def get_minute_candles(self, market, unit, count):
        return self.candles


def make_upbit_style_candles(prices_old_to_new):
    """
    PaperTradingRunner 내부에서 reversed(candles)를 수행하므로,
    FakeUpbitClient는 실제 Upbit API처럼 최신순 데이터를 반환해야 한다.
    """
    candles_old_to_new = [
        {"trade_price": price}
        for price in prices_old_to_new
    ]

    return list(reversed(candles_old_to_new))


def create_runner(candles):
    position_manager = PositionManager()
    risk_manager = RiskManager()

    order_service = PaperOrderService(
        position_manager=position_manager,
        risk_manager=risk_manager,
    )

    upbit_client = FakeUpbitClient(candles)

    runner = PaperTradingRunner(
        upbit_client=upbit_client,
        order_service=order_service,
        position_manager=position_manager,
    )

    return runner, order_service, position_manager


def test_run_once_buy_scenario_creates_position():
    prices_old_to_new = [
        10000, 10000, 10000, 10000, 10000,
        10000, 10000, 10000, 10000, 10000,
        10000, 10000, 10000, 10000, 10000,
        12000, 12100, 12200, 12300, 12400,
        12500, 12600, 12700, 12800, 12900,
        13000, 13100, 13200, 13300, 13400,
    ]

    candles = make_upbit_style_candles(prices_old_to_new)
    runner, order_service, position_manager = create_runner(candles)

    runner.run_once()

    position = position_manager.get_position("KRW-BTC")

    assert position is not None
    assert position.volume > 0
    assert position.avg_price == pytest.approx(13400)

    assert len(order_service.orders) == 1

    order = list(order_service.orders.values())[0]
    assert order.side == OrderSide.BUY
    assert order.executed_price == pytest.approx(13400)


def test_run_once_hold_scenario_does_not_create_order():
    prices_old_to_new = [
        10000 for _ in range(30)
    ]

    candles = make_upbit_style_candles(prices_old_to_new)
    runner, order_service, position_manager = create_runner(candles)

    runner.run_once()

    position = position_manager.get_position("KRW-BTC")

    assert position is None
    assert len(order_service.orders) == 0


def test_run_once_sell_scenario_removes_position():
    prices_buy_old_to_new = [
        10000, 10000, 10000, 10000, 10000,
        10000, 10000, 10000, 10000, 10000,
        10000, 10000, 10000, 10000, 10000,
        12000, 12100, 12200, 12300, 12400,
        12500, 12600, 12700, 12800, 12900,
        13000, 13100, 13200, 13300, 13400,
    ]

    buy_candles = make_upbit_style_candles(prices_buy_old_to_new)
    runner, order_service, position_manager = create_runner(buy_candles)

    runner.run_once()

    assert position_manager.get_position("KRW-BTC") is not None
    assert len(order_service.orders) == 1

    prices_sell_old_to_new = [
        13000, 13000, 13000, 13000, 13000,
        13000, 13000, 13000, 13000, 13000,
        13000, 13000, 13000, 13000, 13000,
        10000, 9900, 9800, 9700, 9600,
        9500, 9400, 9300, 9200, 9100,
        9000, 8900, 8800, 8700, 8600,
    ]

    runner.upbit_client.candles = make_upbit_style_candles(prices_sell_old_to_new)

    runner.run_once()

    position = position_manager.get_position("KRW-BTC")

    assert position is None
    assert len(order_service.orders) == 2

    orders = list(order_service.orders.values())
    sell_order = orders[-1]

    assert sell_order.side == OrderSide.SELL
    assert sell_order.executed_price == pytest.approx(8600)


def test_run_once_updates_current_price():
    prices_old_to_new = [
        10000 for _ in range(29)
    ] + [12345]

    candles = make_upbit_style_candles(prices_old_to_new)
    runner, order_service, _ = create_runner(candles)

    runner.run_once()

    current_price = order_service.get_current_price("KRW-BTC")

    assert current_price == pytest.approx(12345)