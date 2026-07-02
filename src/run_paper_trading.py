from api.upbit_client import UpbitClient
from trading.paper_order_service import PaperOrderService
from trading.paper_trading_runner import PaperTradingRunner
from trading.position import PositionManager
from trading.risk_manager import RiskManager


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

#runner.run_once()
runner.run_forever()