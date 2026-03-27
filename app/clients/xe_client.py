import base64
from decimal import Decimal

import requests

from app.models.rate_model import RateInfo


class XeClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
    ):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/146.0.0.0 Safari/537.36"
            ),
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Authorization": self._build_auth_header(username, password),
            "Referer": "https://www.xe.com/currencyconverter/",
        })

    @staticmethod
    def _build_auth_header(username: str, password: str) -> str:
        raw = f"{username}:{password}"
        encoded = base64.b64encode(raw.encode()).decode()
        return f"Basic {encoded}"

    def get_pair_info(self, from_currency: str, to_currency: str) -> RateInfo:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        params = [
            ("currencyPairs", f"{from_currency}/{to_currency}"),
            ("to", to_currency),
        ]

        response = self.session.get(self.base_url, params=params, timeout=20)
        response.raise_for_status()

        data = response.json()
        if not data:
            raise ValueError("XE вернул пустой ответ")

        for item in data:
            if item.get("from") == from_currency and item.get("to") == to_currency:
                return RateInfo(
                    from_currency=item["from"],
                    to_currency=item["to"],
                    rate=Decimal(str(item["rate"])),
                    trend=item.get("trend"),
                    rate_change=Decimal(str(item.get("rateChange", 0))),
                    percentage_change=Decimal(str(item.get("percentageChange", 0))),
                )

        raise ValueError(f"Пара {from_currency}/{to_currency} не найдена в ответе XE")