from api.upbit_client import UpbitClient


def main():
    client = UpbitClient()

    print("=== KRW 마켓 목록 일부 조회 ===")
    krw_markets = client.get_krw_markets()
    print(krw_markets[:10])

    print("\n=== BTC 현재가 조회 ===")
    ticker = client.get_ticker(["KRW-BTC"])
    btc = ticker[0]

    print("마켓:", btc["market"])
    print("현재가:", btc["trade_price"])

    print("\n=== BTC 1분봉 최근 5개 조회 ===")
    candles = client.get_minute_candles(
        market="KRW-BTC",
        unit=1, ##분봉 단위
        count=5, ##조회 개수
    )

    for candle in candles:
        print(
            candle["candle_date_time_kst"],
            "시가:", candle["opening_price"],
            "고가:", candle["high_price"],
            "저가:", candle["low_price"],
            "종가:", candle["trade_price"],
            "거래량:", candle["candle_acc_trade_volume"],
        )


if __name__ == "__main__":
    main()