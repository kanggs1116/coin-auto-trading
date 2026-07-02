from api.upbit_client import UpbitClient
from database.candle_repository import save_minute_candles


def main():
    market = "KRW-BTC"
    unit = 1
    count = 10

    client = UpbitClient()

    candles = client.get_minute_candles(
        market=market,
        unit=unit,
        count=count
    )

    save_minute_candles(candles, unit=unit)


if __name__ == "__main__":
    main()