import pytest

from trading.position import PositionManager


def test_get_position_when_empty_returns_none():
    position_manager = PositionManager()

    position = position_manager.get_position("KRW-BTC")

    assert position is None


def test_get_volume_when_empty_returns_zero():
    position_manager = PositionManager()

    volume = position_manager.get_volume("KRW-BTC")

    assert volume == 0.0


def test_get_position_value_when_empty_returns_zero():
    position_manager = PositionManager()

    position_value = position_manager.get_position_value("KRW-BTC")

    assert position_value == 0.0


def test_apply_buy_creates_position():
    position_manager = PositionManager()

    position_manager.apply_buy(
        market="KRW-BTC",
        price=10000,
        volume=0.5,
    )

    position = position_manager.get_position("KRW-BTC")

    assert position is not None
    assert position.market == "KRW-BTC"
    assert position.volume == pytest.approx(0.5)
    assert position.avg_price == pytest.approx(10000)


def test_apply_buy_updates_average_price():
    position_manager = PositionManager()

    position_manager.apply_buy(
        market="KRW-BTC",
        price=10000,
        volume=1,
    )

    position_manager.apply_buy(
        market="KRW-BTC",
        price=20000,
        volume=1,
    )

    position = position_manager.get_position("KRW-BTC")

    assert position is not None
    assert position.volume == pytest.approx(2)
    assert position.avg_price == pytest.approx(15000)


def test_get_position_value_returns_total_value_based_on_avg_price():
    position_manager = PositionManager()

    position_manager.apply_buy(
        market="KRW-BTC",
        price=10000,
        volume=2,
    )

    position_value = position_manager.get_position_value("KRW-BTC")

    assert position_value == pytest.approx(20000)


def test_apply_sell_reduces_volume():
    position_manager = PositionManager()

    position_manager.apply_buy(
        market="KRW-BTC",
        price=10000,
        volume=1,
    )

    position_manager.apply_sell(
        market="KRW-BTC",
        volume=0.4,
    )

    position = position_manager.get_position("KRW-BTC")

    assert position is not None
    assert position.volume == pytest.approx(0.6)
    assert position.avg_price == pytest.approx(10000)


def test_apply_sell_all_removes_position():
    position_manager = PositionManager()

    position_manager.apply_buy(
        market="KRW-BTC",
        price=10000,
        volume=1,
    )

    position_manager.apply_sell(
        market="KRW-BTC",
        volume=1,
    )

    position = position_manager.get_position("KRW-BTC")

    assert position is None


def test_apply_sell_without_position_raises_error():
    position_manager = PositionManager()

    with pytest.raises(ValueError, match="보유 포지션이 없습니다."):
        position_manager.apply_sell(
            market="KRW-BTC",
            volume=1,
        )


def test_apply_sell_over_volume_raises_error():
    position_manager = PositionManager()

    position_manager.apply_buy(
        market="KRW-BTC",
        price=10000,
        volume=1,
    )

    with pytest.raises(ValueError, match="보유 수량보다 많이 매도할 수 없습니다."):
        position_manager.apply_sell(
            market="KRW-BTC",
            volume=2,
        )