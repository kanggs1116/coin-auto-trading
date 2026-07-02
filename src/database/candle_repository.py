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