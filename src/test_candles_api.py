from api.upbit_client import UpbitClient


client = UpbitClient()
candles = client.get_minute_candles("KRW-BTC", unit=1, count=3)

for candle in candles:
    print(candle)