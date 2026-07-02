from api.upbit_client import UpbitClient
from database.market_repository import save_markets


def main():
    client = UpbitClient()
    markets = client.get_markets()

    save_markets(markets)


if __name__ == "__main__":
    main()