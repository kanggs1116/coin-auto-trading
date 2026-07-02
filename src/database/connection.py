import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    """
    PostgreSQL DB 연결 객체를 생성해서 반환하는 함수.
    사용 후에는 반드시 close() 해야 한다.
    """

    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )

        return conn

    except Exception as e:
        print("DB 연결 실패")
        print(e)
        raise