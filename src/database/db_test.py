from connection import get_connection


def test_db_connection():
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT current_database();")
        result = cur.fetchone()

        print("DB 연결 성공")
        print(f"현재 연결된 DB: {result[0]}")

        cur.close()

    except Exception as e:
        print("DB 연결 테스트 실패")
        print(e)

    finally:
        if conn:
            conn.close()
            print("DB 연결 종료")


if __name__ == "__main__":
    test_db_connection()