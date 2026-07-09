import pytest

from trading.risk_manager import RiskManager


def test_validate_buy_success():
    risk_manager = RiskManager()

    risk_manager.validate_buy(
        krw_amount=10000,
        current_position_krw=0,
    )


def test_validate_buy_below_min_order_raises_error():
    risk_manager = RiskManager()

    with pytest.raises(ValueError, match="최소 주문 금액 미만입니다."):
        risk_manager.validate_buy(
            krw_amount=4000,
            current_position_krw=0,
        )


def test_validate_buy_over_max_order_raises_error():
    risk_manager = RiskManager()

    with pytest.raises(ValueError, match="1회 주문 한도를 초과했습니다."):
        risk_manager.validate_buy(
            krw_amount=150000,
            current_position_krw=0,
        )


def test_validate_buy_over_max_position_raises_error():
    risk_manager = RiskManager()

    with pytest.raises(ValueError, match="종목별 최대 보유 금액을 초과합니다."):
        risk_manager.validate_buy(
            krw_amount=100000,
            current_position_krw=250000,
        )


def test_validate_sell_success():
    risk_manager = RiskManager()

    risk_manager.validate_sell(
        sell_volume=0.01,
        current_volume=0.02,
    )


def test_validate_sell_zero_volume_raises_error():
    risk_manager = RiskManager()

    with pytest.raises(ValueError, match="매도 수량은 0보다 커야 합니다."):
        risk_manager.validate_sell(
            sell_volume=0,
            current_volume=0.02,
        )


def test_validate_sell_negative_volume_raises_error():
    risk_manager = RiskManager()

    with pytest.raises(ValueError, match="매도 수량은 0보다 커야 합니다."):
        risk_manager.validate_sell(
            sell_volume=-0.01,
            current_volume=0.02,
        )


def test_validate_sell_over_current_volume_raises_error():
    risk_manager = RiskManager()

    with pytest.raises(ValueError, match="보유 수량보다 많이 매도할 수 없습니다."):
        risk_manager.validate_sell(
            sell_volume=0.03,
            current_volume=0.02,
        )