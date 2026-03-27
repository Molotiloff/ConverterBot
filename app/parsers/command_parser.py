import re

from app.models.request_model import ConversionRequest
from app.utils.decimal_utils import parse_decimal


class CommandParser:
    DEFAULT_TARGET_CURRENCY = "USD"

    REQUEST_RE = re.compile(
        r"""
        ^\s*
        (?:
            (?P<from_only>[A-Za-z]{3})\s+
            (?P<amount_only>[0-9]+(?:[.,][0-9]+)?)
            (?:
                \s*(?P<sign_only>[+-])\s*
                (?P<percent_only>[0-9]+(?:[.,][0-9]+)?)
                (?P<mode_only>%%|%)
            )?
        |
            (?P<from_pair>[A-Za-z]{3})\s+
            (?P<to_pair>[A-Za-z]{3})\s+
            (?P<amount_pair>[0-9]+(?:[.,][0-9]+)?)
            (?:
                \s*(?P<sign_pair>[+-])\s*
                (?P<percent_pair>[0-9]+(?:[.,][0-9]+)?)
                (?P<mode_pair>%%|%)
            )?
        )
        \s*$
        """,
        re.VERBOSE | re.IGNORECASE,
    )

    def parse(self, text: str) -> ConversionRequest:
        cleaned = text.strip()

        cleaned = re.sub(r"^/xe(?:@\w+)?\s+", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^@\w+\s+", "", cleaned, flags=re.IGNORECASE)

        match = self.REQUEST_RE.match(cleaned)
        if not match:
            raise ValueError(
                "Неверный формат.\n"
                "Примеры:\n"
                "AED 1000\n"
                "EUR AED 1000\n"
                "EUR 100-0.3%\n"
                "EUR 100-0.3%%\n"
                "EUR 100+0.3%\n"
                "EUR 100+0.3%%\n"
                "EUR AED 1000-0.2%\n"
                "EUR AED 1000+0.2%%"
            )

        if match.group("from_only"):
            from_currency = match.group("from_only").upper()
            to_currency = self.DEFAULT_TARGET_CURRENCY
            amount = parse_decimal(match.group("amount_only"))
            sign_raw = match.group("sign_only")
            percent_raw = match.group("percent_only")
            mode_raw = match.group("mode_only")
        else:
            from_currency = match.group("from_pair").upper()
            to_currency = match.group("to_pair").upper()
            amount = parse_decimal(match.group("amount_pair"))
            sign_raw = match.group("sign_pair")
            percent_raw = match.group("percent_pair")
            mode_raw = match.group("mode_pair")

        percent = parse_decimal(percent_raw) if percent_raw is not None else None
        sign = 1 if sign_raw == "+" else -1
        is_markup = mode_raw == "%%"

        if amount <= 0:
            raise ValueError("Сумма должна быть больше 0")

        if percent is not None:
            if percent < 0:
                raise ValueError("Процент не может быть отрицательным")
            if percent >= 100:
                raise ValueError("Процент должен быть меньше 100%")

        return ConversionRequest(
            from_currency=from_currency,
            to_currency=to_currency,
            amount=amount,
            percent=percent,
            sign=sign,
            is_markup=is_markup,
        )