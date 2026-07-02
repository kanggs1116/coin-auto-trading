from database.connection import get_connection

def save_markets(markets):
    conn = None

    sql = """
        INSERT INTO markets (
            market,
            korean_name,
            english_name,
            market_warning
        )
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (market)
        DO UPDATE SET
            korean_name = EXCLUDED.korean_name,
            english_name = EXCLUDED.english_name,
            market_warning = EXCLUDED.market_warning,
            updated_at = CURRENT_TIMESTAMP;
    """

    try:
        conn = get_connection()
        cur = conn.cursor()

        for item in markets:
            cur.execute(
                sql,
                (
                    item.get("market"),
                    item.get("korean_name"),
                    item.get("english_name"),
                    item.get("market_warning", "NONE"),
                ),
            )

        conn.commit()
        cur.close()

        print(f"마켓 데이터 저장 완료: {len(markets)}개")

    except Exception as e:
        if conn:
            conn.rollback()

        print("마켓 데이터 저장 실패")
        print(e)
        raise

    finally:
        if conn:
            conn.close()