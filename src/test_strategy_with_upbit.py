from api.upbit_client import UpbitClient
from strategy.moving_average_strategy import MovingAverageStrategy

upbit = UpbitClient()

strategy = MovingAverageStrategy(
    short_window=5,
    long_window=20,
)

candles = upbit.get_minute_candles(
    market="KRW-BTC",
    unit=1,
    count=30,
)

# Upbit는 최신 → 과거 순으로 반환하므로 과거 → 최신으로 변경
candles = list(reversed(candles))

signal = strategy.generate_signal(
    candles=candles,
    has_position=False,
)

print("=" * 50)
print("이동평균 전략 테스트 (실제 Upbit 데이터)")
print("=" * 50)

print(f"캔들 개수 : {len(candles)}")
print(f"최신 종가 : {candles[-1]['trade_price']:,}원")
print()

print(signal)