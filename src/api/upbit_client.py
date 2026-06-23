from typing import Any

import requests


class UpbitClient:
    BASE_URL = "https://api.upbit.com/v1"

    def __init__(self):
        self.session = requests.Session()

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.BASE_URL}{path}"

        try:
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise RuntimeError("Upbit API 요청 시간이 초과되었습니다.")

        except requests.exceptions.HTTPError as e:
            raise RuntimeError(
                f"Upbit API HTTP 오류: {response.status_code}, {response.text}"
            ) from e

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Upbit API 요청 실패: {e}") from e

    def get_markets(self, is_details: bool = False) -> list[dict[str, Any]]:
        return self._get(
            "/market/all",
            params={"is_details": str(is_details).lower()},
        )

    def get_krw_markets(self) -> list[str]:
        markets = self.get_markets()
        return [
            market["market"]
            for market in markets
            if market["market"].startswith("KRW-")
        ]

    def get_ticker(self, markets: list[str]) -> list[dict[str, Any]]:
        return self._get(
            "/ticker",
            params={"markets": ",".join(markets)},
        )

    def get_minute_candles(
        self,
        market: str = "KRW-BTC",
        unit: int = 1,
        count: int = 10,
    ) -> list[dict[str, Any]]:
        if unit not in [1, 3, 5, 10, 15, 30, 60, 240]:
            raise ValueError("unit은 1, 3, 5, 10, 15, 30, 60, 240 중 하나여야 합니다.")

        return self._get(
            f"/candles/minutes/{unit}",
            params={
                "market": market,
                "count": count,
            },
        )