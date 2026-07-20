import pytest

from backtest.backtest_config import BacktestConfig


def test_backtest_config_uses_default_values():
    config = BacktestConfig()

    assert config.market == "KRW-BTC"
    assert config.candle_type == "minute"
    assert config.candle_unit == 1

    assert config.initial_capital == pytest.approx(
        1_000_000
    )
    assert config.order_amount_krw == pytest.approx(
        100_000
    )

    assert config.buy_fee_rate == pytest.approx(
        0.0005
    )
    assert config.sell_fee_rate == pytest.approx(
        0.0005
    )


def test_backtest_config_accepts_custom_values():
    config = BacktestConfig(
        market="KRW-ETH",
        candle_type="minute",
        candle_unit=5,
        initial_capital=2_000_000,
        order_amount_krw=200_000,
        buy_fee_rate=0.0004,
        sell_fee_rate=0.0006,
    )

    assert config.market == "KRW-ETH"
    assert config.candle_type == "minute"
    assert config.candle_unit == 5

    assert config.initial_capital == pytest.approx(
        2_000_000
    )
    assert config.order_amount_krw == pytest.approx(
        200_000
    )

    assert config.buy_fee_rate == pytest.approx(
        0.0004
    )
    assert config.sell_fee_rate == pytest.approx(
        0.0006
    )


@pytest.mark.parametrize(
    "market",
    [
        "",
        "   ",
    ],
)
def test_backtest_config_empty_market_raises_error(
    market,
):
    with pytest.raises(
        ValueError,
        match="market은 비어 있을 수 없습니다.",
    ):
        BacktestConfig(
            market=market,
        )


def test_backtest_config_unsupported_candle_type_raises_error():
    with pytest.raises(
        ValueError,
        match="현재 백테스트 MVP에서는 candle_type='minute'만 지원합니다.",
    ):
        BacktestConfig(
            candle_type="day",
        )


@pytest.mark.parametrize(
    "candle_unit",
    [
        0,
        2,
        7,
        120,
    ],
)
def test_backtest_config_invalid_candle_unit_raises_error(
    candle_unit,
):
    with pytest.raises(
        ValueError,
        match=(
            "candle_unit은 1, 3, 5, 10, 15, "
            "30, 60, 240 중 하나여야 합니다."
        ),
    ):
        BacktestConfig(
            candle_unit=candle_unit,
        )


@pytest.mark.parametrize(
    "initial_capital",
    [
        0,
        -1,
        -1_000_000,
    ],
)
def test_backtest_config_non_positive_initial_capital_raises_error(
    initial_capital,
):
    with pytest.raises(
        ValueError,
        match="initial_capital은 0보다 커야 합니다.",
    ):
        BacktestConfig(
            initial_capital=initial_capital,
        )


@pytest.mark.parametrize(
    "order_amount_krw",
    [
        0,
        -1,
        -100_000,
    ],
)
def test_backtest_config_non_positive_order_amount_raises_error(
    order_amount_krw,
):
    with pytest.raises(
        ValueError,
        match="order_amount_krw는 0보다 커야 합니다.",
    ):
        BacktestConfig(
            order_amount_krw=order_amount_krw,
        )


@pytest.mark.parametrize(
    "buy_fee_rate",
    [
        -0.0001,
        1,
        1.5,
    ],
)
def test_backtest_config_invalid_buy_fee_rate_raises_error(
    buy_fee_rate,
):
    with pytest.raises(
        ValueError,
        match="buy_fee_rate는 0 이상 1 미만이어야 합니다.",
    ):
        BacktestConfig(
            buy_fee_rate=buy_fee_rate,
        )


@pytest.mark.parametrize(
    "sell_fee_rate",
    [
        -0.0001,
        1,
        1.5,
    ],
)
def test_backtest_config_invalid_sell_fee_rate_raises_error(
    sell_fee_rate,
):
    with pytest.raises(
        ValueError,
        match="sell_fee_rate는 0 이상 1 미만이어야 합니다.",
    ):
        BacktestConfig(
            sell_fee_rate=sell_fee_rate,
        )


def test_backtest_config_order_total_cost_cannot_exceed_initial_capital():
    with pytest.raises(
        ValueError,
        match=(
            "초기 자본은 1회 매수 체결금액과 "
            "매수 수수료의 합 이상이어야 합니다."
        ),
    ):
        BacktestConfig(
            initial_capital=100_000,
            order_amount_krw=100_000,
            buy_fee_rate=0.0005,
        )


def test_backtest_config_allows_order_when_total_cost_equals_initial_capital():
    order_amount = 100_000
    buy_fee_rate = 0.0005

    required_cash = order_amount * (
        1 + buy_fee_rate
    )

    config = BacktestConfig(
        initial_capital=required_cash,
        order_amount_krw=order_amount,
        buy_fee_rate=buy_fee_rate,
    )

    assert config.initial_capital == pytest.approx(
        required_cash
    )