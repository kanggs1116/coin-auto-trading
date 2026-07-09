import pytest

from trading.order_types import OrderSide, OrderType, OrderState
from trading.paper_order_service import PaperOrderService
from trading.position import PositionManager
from trading.risk_manager import RiskManager


def create_order_service():
    position_manager = PositionManager()
    risk_manager = RiskManager()

    order_service = PaperOrderService(
        position_manager=position_manager,
        risk_manager=risk_manager,
    )

    return order_service, position_manager, risk_manager


def test_update_current_price_success():
    order_service, _, _ = create_order_service()

    order_service.update_current_price(
        market="KRW-BTC",
        price=10000000,
    )

    current_price = order_service.get_current_price("KRW-BTC")

    assert current_price == pytest.approx(10000000)


def test_update_current_price_zero_raises_error():
    order_service, _, _ = create_order_service()

    with pytest.raises(ValueError, match="현재가는 0보다 커야 합니다."):
        order_service.update_current_price(
            market="KRW-BTC",
            price=0,
        )


def test_update_current_price_negative_raises_error():
    order_service, _, _ = create_order_service()

    with pytest.raises(ValueError, match="현재가는 0보다 커야 합니다."):
        order_service.update_current_price(
            market="KRW-BTC",
            price=-1000,
        )


def test_get_current_price_without_price_raises_error():
    order_service, _, _ = create_order_service()

    with pytest.raises(ValueError, match="KRW-BTC의 현재가가 설정되지 않았습니다."):
        order_service.get_current_price("KRW-BTC")


def test_buy_market_creates_filled_buy_order():
    order_service, position_manager, _ = create_order_service()

    order_service.update_current_price(
        market="KRW-BTC",
        price=10000000,
    )

    order = order_service.buy_market(
        market="KRW-BTC",
        krw_amount=10000,
    )

    expected_fee = 10000 * 0.0005
    expected_volume = (10000 - expected_fee) / 10000000

    assert order.market == "KRW-BTC"
    assert order.side == OrderSide.BUY
    assert order.order_type == OrderType.MARKET
    assert order.state == OrderState.FILLED
    assert order.price is None
    assert order.volume is None
    assert order.krw_amount == pytest.approx(10000)
    assert order.executed_price == pytest.approx(10000000)
    assert order.executed_volume == pytest.approx(expected_volume)
    assert order.fee == pytest.approx(expected_fee)

    assert order_service.get_order(order.order_id) == order

    position = position_manager.get_position("KRW-BTC")
    assert position is not None
    assert position.volume == pytest.approx(expected_volume)
    assert position.avg_price == pytest.approx(10000000)


def test_buy_market_without_current_price_raises_error():
    order_service, _, _ = create_order_service()

    with pytest.raises(ValueError, match="KRW-BTC의 현재가가 설정되지 않았습니다."):
        order_service.buy_market(
            market="KRW-BTC",
            krw_amount=10000,
        )


def test_buy_market_below_min_order_raises_error():
    order_service, _, _ = create_order_service()

    order_service.update_current_price(
        market="KRW-BTC",
        price=10000000,
    )

    with pytest.raises(ValueError, match="최소 주문 금액 미만입니다."):
        order_service.buy_market(
            market="KRW-BTC",
            krw_amount=4000,
        )


def test_buy_market_over_max_order_raises_error():
    order_service, _, _ = create_order_service()

    order_service.update_current_price(
        market="KRW-BTC",
        price=10000000,
    )

    with pytest.raises(ValueError, match="1회 주문 한도를 초과했습니다."):
        order_service.buy_market(
            market="KRW-BTC",
            krw_amount=150000,
        )


def test_sell_market_creates_filled_sell_order():
    order_service, position_manager, _ = create_order_service()

    order_service.update_current_price(
        market="KRW-BTC",
        price=10000000,
    )

    buy_order = order_service.buy_market(
        market="KRW-BTC",
        krw_amount=10000,
    )

    sell_order = order_service.sell_market(
        market="KRW-BTC",
        volume=buy_order.executed_volume,
    )

    expected_gross_amount = 10000000 * buy_order.executed_volume
    expected_fee = expected_gross_amount * 0.0005

    assert sell_order.market == "KRW-BTC"
    assert sell_order.side == OrderSide.SELL
    assert sell_order.order_type == OrderType.MARKET
    assert sell_order.state == OrderState.FILLED
    assert sell_order.price is None
    assert sell_order.volume == pytest.approx(buy_order.executed_volume)
    assert sell_order.krw_amount is None
    assert sell_order.executed_price == pytest.approx(10000000)
    assert sell_order.executed_volume == pytest.approx(buy_order.executed_volume)
    assert sell_order.fee == pytest.approx(expected_fee)

    assert order_service.get_order(sell_order.order_id) == sell_order

    position = position_manager.get_position("KRW-BTC")
    assert position is None


def test_sell_market_without_position_raises_error():
    order_service, _, _ = create_order_service()

    order_service.update_current_price(
        market="KRW-BTC",
        price=10000000,
    )

    with pytest.raises(ValueError, match="보유 수량보다 많이 매도할 수 없습니다."):
        order_service.sell_market(
            market="KRW-BTC",
            volume=0.01,
        )


def test_sell_market_zero_volume_raises_error():
    order_service, _, _ = create_order_service()

    order_service.update_current_price(
        market="KRW-BTC",
        price=10000000,
    )

    with pytest.raises(ValueError, match="매도 수량은 0보다 커야 합니다."):
        order_service.sell_market(
            market="KRW-BTC",
            volume=0,
        )


def test_cancel_filled_order_raises_error():
    order_service, _, _ = create_order_service()

    order_service.update_current_price(
        market="KRW-BTC",
        price=10000000,
    )

    order = order_service.buy_market(
        market="KRW-BTC",
        krw_amount=10000,
    )

    with pytest.raises(ValueError, match="이미 체결된 주문은 취소할 수 없습니다."):
        order_service.cancel_order(order.order_id)