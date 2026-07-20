import pytest

from database.candle_repository import get_recent_minute_candles


MARKET = "KRW-BTC"
UNIT = 1
TEST_LIMIT = 10


def test_get_recent_minute_candles_returns_candles():
    candles = get_recent_minute_candles(
        market=MARKET,
        unit=UNIT,
        limit=TEST_LIMIT,
    )

    assert len(candles) > 0
    assert len(candles) <= TEST_LIMIT


def test_get_recent_minute_candles_returns_required_fields():
    candles = get_recent_minute_candles(
        market=MARKET,
        unit=UNIT,
        limit=TEST_LIMIT,
    )

    assert len(candles) > 0

    required_fields = {
        "market",
        "candle_type",
        "unit",
        "candle_date_time_utc",
        "candle_date_time_kst",
        "opening_price",
        "high_price",
        "low_price",
        "trade_price",
        "candle_acc_trade_price",
        "candle_acc_trade_volume",
        "timestamp_ms",
    }

    for candle in candles:
        assert required_fields.issubset(candle.keys())


def test_get_recent_minute_candles_returns_requested_market_and_unit():
    candles = get_recent_minute_candles(
        market=MARKET,
        unit=UNIT,
        limit=TEST_LIMIT,
    )

    assert len(candles) > 0

    for candle in candles:
        assert candle["market"] == MARKET
        assert candle["candle_type"] == "minute"
        assert candle["unit"] == UNIT


def test_get_recent_minute_candles_returns_oldest_to_newest():
    candles = get_recent_minute_candles(
        market=MARKET,
        unit=UNIT,
        limit=TEST_LIMIT,
    )

    assert len(candles) > 0

    candle_times = [
        candle["candle_date_time_utc"]
        for candle in candles
    ]

    assert candle_times == sorted(candle_times)


def test_get_recent_minute_candles_has_no_duplicate_times():
    candles = get_recent_minute_candles(
        market=MARKET,
        unit=UNIT,
        limit=TEST_LIMIT,
    )

    assert len(candles) > 0

    candle_times = [
        candle["candle_date_time_utc"]
        for candle in candles
    ]

    assert len(candle_times) == len(set(candle_times))


def test_get_recent_minute_candles_empty_market_raises_error():
    with pytest.raises(
        ValueError,
        match="market은 비어 있을 수 없습니다.",
    ):
        get_recent_minute_candles(
            market="",
            unit=UNIT,
            limit=TEST_LIMIT,
        )


def test_get_recent_minute_candles_invalid_unit_raises_error():
    with pytest.raises(
        ValueError,
        match="unit은 1, 3, 5, 10, 15, 30, 60, 240 중 하나여야 합니다.",
    ):
        get_recent_minute_candles(
            market=MARKET,
            unit=2,
            limit=TEST_LIMIT,
        )


def test_get_recent_minute_candles_zero_limit_raises_error():
    with pytest.raises(
        ValueError,
        match="limit은 1 이상이어야 합니다.",
    ):
        get_recent_minute_candles(
            market=MARKET,
            unit=UNIT,
            limit=0,
        )


def test_get_recent_minute_candles_negative_limit_raises_error():
    with pytest.raises(
        ValueError,
        match="limit은 1 이상이어야 합니다.",
    ):
        get_recent_minute_candles(
            market=MARKET,
            unit=UNIT,
            limit=-1,
        )