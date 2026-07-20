from typing import Any

from database.connection import get_connection


def save_minute_candles(candles, unit=1):
    conn = None

    sql = """
        INSERT INTO candles (
            market,
            candle_type,
            unit,
            candle_date_time_utc,
            candle_date_time_kst,
            opening_price,
            high_price,
            low_price,
            trade_price,
            candle_acc_trade_price,
            candle_acc_trade_volume,
            timestamp_ms
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (market, candle_type, unit, candle_date_time_utc)
        DO NOTHING;
    """

    try:
        conn = get_connection()
        cur = conn.cursor()

        for item in candles:
            cur.execute(
                sql,
                (
                    item.get("market"),
                    "minute",
                    unit,
                    item.get("candle_date_time_utc"),
                    item.get("candle_date_time_kst"),
                    item.get("opening_price"),
                    item.get("high_price"),
                    item.get("low_price"),
                    item.get("trade_price"),
                    item.get("candle_acc_trade_price"),
                    item.get("candle_acc_trade_volume"),
                    item.get("timestamp"),
                ),
            )

        conn.commit()
        cur.close()

        print(f"캔들 데이터 저장 완료: 요청 {len(candles)}개")

    except Exception as e:
        if conn:
            conn.rollback()

        print("캔들 데이터 저장 실패")
        print(e)
        raise

    finally:
        if conn:
            conn.close()


def get_recent_minute_candles(
    market: str,
    unit: int = 1,
    limit: int = 1000,
) -> list[dict[str, Any]]:
    """
    특정 시장의 가장 최근 분봉 캔들 N개를 조회한다.

    DB에서는 최근 데이터를 먼저 선택한 뒤,
    백테스트에서 바로 사용할 수 있도록 과거 → 최신 순서로 반환한다.

    Args:
        market:
            조회할 시장 코드.
            예: "KRW-BTC"

        unit:
            분봉 단위.
            예: 1, 3, 5, 10, 15, 30, 60, 240

        limit:
            조회할 최근 캔들 개수.

    Returns:
        과거 → 최신 순서로 정렬된 캔들 딕셔너리 목록.

    Raises:
        ValueError:
            market이 비어 있거나,
            지원하지 않는 분봉 단위이거나,
            limit이 1보다 작을 경우 발생한다.
    """
    if not market or not market.strip():
        raise ValueError("market은 비어 있을 수 없습니다.")

    allowed_units = {1, 3, 5, 10, 15, 30, 60, 240}

    if unit not in allowed_units:
        raise ValueError(
            "unit은 1, 3, 5, 10, 15, 30, 60, 240 중 하나여야 합니다."
        )

    if limit <= 0:
        raise ValueError("limit은 1 이상이어야 합니다.")

    sql = """
        SELECT
            id,
            market,
            candle_type,
            unit,
            candle_date_time_utc,
            candle_date_time_kst,
            opening_price,
            high_price,
            low_price,
            trade_price,
            candle_acc_trade_price,
            candle_acc_trade_volume,
            timestamp_ms,
            created_at
        FROM (
            SELECT
                id,
                market,
                candle_type,
                unit,
                candle_date_time_utc,
                candle_date_time_kst,
                opening_price,
                high_price,
                low_price,
                trade_price,
                candle_acc_trade_price,
                candle_acc_trade_volume,
                timestamp_ms,
                created_at
            FROM candles
            WHERE market = %s
              AND candle_type = 'minute'
              AND unit = %s
            ORDER BY candle_date_time_utc DESC
            LIMIT %s
        ) AS recent_candles
        ORDER BY candle_date_time_utc ASC;
    """

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            sql,
            (
                market.strip(),
                unit,
                limit,
            ),
        )

        rows = cur.fetchall()
        column_names = [
            description[0]
            for description in cur.description
        ]

        return [
            dict(zip(column_names, row))
            for row in rows
        ]

    except Exception:
        print("백테스트용 캔들 데이터 조회 실패")
        raise

    finally:
        if cur:
            cur.close()

        if conn:
            conn.close()