import time

from api.upbit_client import UpbitClient
from trading.paper_order_service import PaperOrderService
from trading.paper_trading_runner import PaperTradingRunner
from trading.position import PositionManager
from trading.risk_manager import RiskManager
from trading.trading_config import TRADING_INTERVAL_SECONDS


def main():
    repeat_count = 5

    position_manager = PositionManager()
    risk_manager = RiskManager()

    order_service = PaperOrderService(
        position_manager=position_manager,
        risk_manager=risk_manager,
    )

    upbit_client = UpbitClient()

    runner = PaperTradingRunner(
        upbit_client=upbit_client,
        order_service=order_service,
        position_manager=position_manager,
    )

    elapsed_times = []
    failed_count = 0

    print("[PERFORMANCE TEST] run_once 실행 시간 측정 시작")
    print("[NOTICE] 실제 주문 API는 사용하지 않습니다.")
    print("[NOTICE] PaperOrderService 기반 모의 주문만 실행됩니다.")
    print(f"[REPEAT COUNT] {repeat_count}")
    print(f"[TRADING INTERVAL] {TRADING_INTERVAL_SECONDS}초")
    print()

    for i in range(1, repeat_count + 1):
        print("=" * 60)
        print(f"[ITERATION] {i}/{repeat_count}")

        start_time = time.perf_counter()

        try:
            runner.run_once()

        except Exception as e:
            failed_count += 1
            print(f"[ERROR] {e}")

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        elapsed_times.append(elapsed_time)

        print()
        print(f"[ELAPSED TIME] {elapsed_time:.4f}초")

        if i < repeat_count:
            time.sleep(1)

    success_count = repeat_count - failed_count

    print()
    print("=" * 60)
    print("[PERFORMANCE TEST RESULT]")
    print(f"총 실행 횟수 : {repeat_count}")
    print(f"성공 횟수 : {success_count}")
    print(f"실패 횟수 : {failed_count}")

    if elapsed_times:
        average_time = sum(elapsed_times) / len(elapsed_times)
        max_time = max(elapsed_times)
        min_time = min(elapsed_times)

        print(f"평균 실행 시간 : {average_time:.4f}초")
        print(f"최대 실행 시간 : {max_time:.4f}초")
        print(f"최소 실행 시간 : {min_time:.4f}초")

        if average_time < TRADING_INTERVAL_SECONDS:
            print("[RESULT] 평균 실행 시간이 거래 반복 주기보다 짧습니다.")
        else:
            print("[WARNING] 평균 실행 시간이 거래 반복 주기보다 깁니다.")

        if max_time < TRADING_INTERVAL_SECONDS:
            print("[RESULT] 최대 실행 시간도 거래 반복 주기보다 짧습니다.")
        else:
            print("[WARNING] 일부 실행 시간이 거래 반복 주기를 초과했습니다.")

    print(f"최종 주문 수 : {len(order_service.orders)}")

    position = position_manager.get_position("KRW-BTC")

    if position is None:
        print("최종 포지션 : 없음")
    else:
        print("최종 포지션 : 있음")
        print(f"보유 수량 : {position.volume:.8f}")
        print(f"평균 단가 : {position.avg_price:,.0f}원")


if __name__ == "__main__":
    main()