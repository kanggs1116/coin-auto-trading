import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="trading_db",
    user="trading_user",
    password="trading_password"
)

print("DB 연결 성공!")

conn.close()