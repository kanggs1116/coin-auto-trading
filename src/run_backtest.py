from backtest.backtest_config import BacktestConfig
from backtest.backtest_engine import BacktestEngine
from backtest.backtest_models import BacktestResult, TradeRecord
from database.candle_repository import get_recent_minute_candles
from strategy.moving_average_strategy import MovingAverageStrategy
from trading.order_types import OrderSide


MARKET = "KRW-BTC"
CANDLE_UNIT = 1
CANDLE_LIMIT = 200

INITIAL_CAPITAL = 1_000_000
ORDER_AMOUNT_KRW = 100_000

BUY_FEE_RATE = 0.0005
SELL_FEE_RATE = 0.0005

SHORT_WINDOW = 5
LONG_WINDOW = 20


def format_krw(value: float) -> str:
    """
    원화 금액을 소수점 없이 천 단위 구분 기호와 함께 반환한다.
    """
    return f"{value:,.0f}원"


def format_percent(value: float) -> str:
    """
    0.05와 같은 비율을 5.00% 형식으로 반환한다.
    """
    return f"{value * 100:.2f}%"


def format_volume(value: float) -> str:
    """
    코인 수량을 소수점 8자리까지 반환한다.
    """
    return f"{value:.8f}"


def format_realized_pnl(value: float | None) -> str:
    """
    BUY 거래처럼 실현 손익이 없는 경우 '-'를 반환한다.
    """
    if value is None:
        return "-"

    return format_krw(value)


def print_backtest_summary(
    result: BacktestResult,
    config: BacktestConfig,
    strategy: MovingAverageStrategy,
) -> None:
    """
    백테스트 기본 정보, 자산 결과 및 거래 통계를 출력한다.
    """
    print("=" * 70)
    print("[BACKTEST RESULT]")
    print("=" * 70)

    print(f"시장                  : {result.market}")
    print(
        "캔들                  : "
        f"{config.candle_type} {config.candle_unit}분봉"
    )
    print(f"처리한 캔들 수        : {result.candle_count}개")
    print(f"시작 시각             : {result.start_time}")
    print(f"종료 시각             : {result.end_time}")
    print(f"단기 이동평균         : {strategy.short_window}")
    print(f"장기 이동평균         : {strategy.long_window}")

    print()
    print("[ASSET]")
    print(
        f"초기 자본             : "
        f"{format_krw(result.initial_capital)}"
    )
    print(
        f"1회 매수 체결금액     : "
        f"{format_krw(config.order_amount_krw)}"
    )
    print(
        f"매수 수수료율         : "
        f"{format_percent(config.buy_fee_rate)}"
    )
    print(
        f"매도 수수료율         : "
        f"{format_percent(config.sell_fee_rate)}"
    )
    print(
        f"최종 현금             : "
        f"{format_krw(result.final_cash)}"
    )
    print(
        f"최종 보유 수량        : "
        f"{format_volume(result.final_position_volume)} BTC"
    )
    print(
        f"마지막 종가           : "
        f"{format_krw(result.last_price)}"
    )
    print(
        f"포지션 평가금액       : "
        f"{format_krw(result.final_position_value)}"
    )
    print(
        f"최종 총자산           : "
        f"{format_krw(result.final_equity)}"
    )
    print(
        f"누적 수익률           : "
        f"{format_percent(result.cumulative_return)}"
    )

    print()
    print("[STATISTICS]")
    print(
        f"총 체결 횟수          : "
        f"{result.total_trade_count}회"
    )
    print(
        f"완료된 매매 횟수      : "
        f"{result.completed_trade_count}회"
    )
    print(
        f"승리 거래             : "
        f"{result.winning_trade_count}회"
    )
    print(
        f"손실 거래             : "
        f"{result.losing_trade_count}회"
    )
    print(
        f"승률                  : "
        f"{format_percent(result.win_rate)}"
    )
    print(
        f"최대 낙폭             : "
        f"{format_percent(result.max_drawdown)}"
    )
    print(
        "미청산 포지션         : "
        f"{'있음' if result.has_open_position else '없음'}"
    )


def print_trade_record(
    index: int,
    trade: TradeRecord,
) -> None:
    """
    한 건의 거래 내역을 사람이 읽기 쉬운 형태로 출력한다.
    """
    side_text = (
        "매수"
        if trade.side == OrderSide.BUY
        else "매도"
    )

    print("-" * 70)
    print(f"[{index}] {side_text}")
    print(f"거래 시각             : {trade.timestamp}")
    print(f"시장                  : {trade.market}")
    print(
        f"체결 가격             : "
        f"{format_krw(trade.price)}"
    )
    print(
        f"체결 수량             : "
        f"{format_volume(trade.volume)} BTC"
    )
    print(
        f"체결금액              : "
        f"{format_krw(trade.gross_amount)}"
    )
    print(
        f"수수료                : "
        f"{format_krw(trade.fee)}"
    )
    print(
        f"현금 흐름             : "
        f"{format_krw(trade.cash_flow)}"
    )
    print(
        f"거래 후 현금          : "
        f"{format_krw(trade.cash_after)}"
    )
    print(
        f"거래 후 보유 수량     : "
        f"{format_volume(trade.position_volume_after)} BTC"
    )
    print(
        f"실현 손익             : "
        f"{format_realized_pnl(trade.realized_pnl)}"
    )
    print(f"신호 사유             : {trade.signal_reason}")


def print_trade_history(
    trades: list[TradeRecord],
) -> None:
    """
    전체 거래 내역을 출력한다.
    """
    print()
    print("[TRADES]")

    if not trades:
        print("체결된 거래가 없습니다.")
        return

    for index, trade in enumerate(
        trades,
        start=1,
    ):
        print_trade_record(
            index=index,
            trade=trade,
        )


def main() -> None:
    """
    PostgreSQL에서 과거 캔들을 조회하고 백테스트를 실행한다.
    """
    config = BacktestConfig(
        market=MARKET,
        candle_type="minute",
        candle_unit=CANDLE_UNIT,
        initial_capital=INITIAL_CAPITAL,
        order_amount_krw=ORDER_AMOUNT_KRW,
        buy_fee_rate=BUY_FEE_RATE,
        sell_fee_rate=SELL_FEE_RATE,
    )

    strategy = MovingAverageStrategy(
        short_window=SHORT_WINDOW,
        long_window=LONG_WINDOW,
    )

    candles = get_recent_minute_candles(
        market=config.market,
        unit=config.candle_unit,
        limit=CANDLE_LIMIT,
    )

    if len(candles) < strategy.long_window:
        raise RuntimeError(
            "백테스트에 필요한 캔들 수가 부족합니다. "
            f"필요: {strategy.long_window}개 이상, "
            f"현재: {len(candles)}개"
        )

    engine = BacktestEngine(
        config=config,
        strategy=strategy,
    )

    result = engine.run(candles)

    print_backtest_summary(
        result=result,
        config=config,
        strategy=strategy,
    )

    print_trade_history(
        trades=result.trades,
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()