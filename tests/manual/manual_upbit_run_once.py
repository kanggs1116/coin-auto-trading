from api.upbit_client import UpbitClient
from trading.paper_order_service import PaperOrderService
from trading.paper_trading_runner import PaperTradingRunner
from trading.position import PositionManager
from trading.risk_manager import RiskManager


def main():
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

    print("[MANUAL TEST] Upbit 공개 API 기반 run_once 테스트 시작")
    print("[NOTICE] 실제 주문 API는 사용하지 않습니다.")
    print("[NOTICE] PaperOrderService 기반 모의 주문만 실행됩니다.")
    print()

    runner.run_once()

    print()
    print("[MANUAL TEST] run_once 테스트 종료")
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