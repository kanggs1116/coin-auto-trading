from trading.paper_order_service import PaperOrderService
from trading.position import PositionManager
from trading.risk_manager import RiskManager


position_manager = PositionManager()
risk_manager = RiskManager()

order_service = PaperOrderService(
    position_manager=position_manager,
    risk_manager=risk_manager,
)

order_service.update_current_price("KRW-BTC", 100000000.0)

buy_order = order_service.buy_market("KRW-BTC", 10000)
print("매수 주문:", buy_order)

position = position_manager.get_position("KRW-BTC")
print("현재 포지션:", position)

sell_order = order_service.sell_market("KRW-BTC", position.volume)
print("매도 주문:", sell_order)

position = position_manager.get_position("KRW-BTC")
print("매도 후 포지션:", position)