import re


class CurrencyNormalizer:
    _ALIASES = {
        "€": "EUR",
        "EUR": "EUR",
        "E": "EUR",

        "£": "GBP",
        "GBP": "GBP",

        "₣": "CHF",
        "CHF": "CHF",

        "¥": "CNY",
        "CNY": "CNY",

        "$": "USD",
        "USD": "USD",
        "D": "USD",
    }

    @classmethod
    def normalize_token(cls, token: str) -> str:
        cleaned = token.strip().upper()
        return cls._ALIASES.get(cleaned, cleaned)

    @classmethod
    def normalize_text(cls, text: str) -> str:
        # Нормализуем отдельные standalone токены валют,
        # не трогая числа и проценты.
        pattern = re.compile(r"(?<!\S)(€|£|₣|¥|\$|[A-Za-z]{1,3})(?!\S)")

        def repl(match: re.Match) -> str:
            token = match.group(1)
            return cls.normalize_token(token)

        return pattern.sub(repl, text)