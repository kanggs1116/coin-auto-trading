import time

from api.upbit_client import UpbitClient
from trading.paper_order_service import PaperOrderService
from trading.paper_trading_runner import PaperTradingRunner
from trading.position import PositionManager
from trading.risk_manager import RiskManager
from trading.trading_config import TRADING_INTERVAL_SECONDS


def main():
    repeat_count = 3

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

    print("[MANUAL TEST] 제한 반복 실행 테스트 시작")
    print("[NOTICE] 실제 주문 API는 사용하지 않습니다.")
    print("[NOTICE] PaperOrderService 기반 모의 주문만 실행됩니다.")
    print(f"[REPEAT COUNT] {repeat_count}")
    print(f"[INTERVAL] {TRADING_INTERVAL_SECONDS}초")
    print()

    for i in range(1, repeat_count + 1):
        print()
        print(f"[ITERATION] {i}/{repeat_count}")

        try:
            runner.run_once()

        except Exception as e:
            print(f"[ERROR] {e}")

        if i < repeat_count:
            print()
            print(f"[SLEEP] {TRADING_INTERVAL_SECONDS}초 대기")
            time.sleep(TRADING_INTERVAL_SECONDS)

    print()
    print("[MANUAL TEST] 제한 반복 실행 테스트 종료")
    print(f"[ORDER COUNT] {len(order_service.orders)}")

    position = position_manager.get_position("KRW-BTC")

    if position is None:
        print("[FINAL POSITION] 보유 포지션 없음")
    else:
        print("[FINAL POSITION]")
        print(f"보유 수량 : {position.volume:.8f}")
        print(f"평균 단가 : {position.avg_price:,.0f}원")


if __name__ == "__main__":
    main()