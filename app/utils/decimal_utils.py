from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


def parse_decimal(value: str) -> Decimal:
    normalized = value.replace(",", ".").strip()
    try:
        return Decimal(normalized)
    except InvalidOperation as e:
        raise ValueError(f"Некорректное число: {value}") from e


def quant_2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def quant_0(value: Decimal) -> Decimal:
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def format_decimal_2(value: Decimal) -> str:
    return f"{quant_2(value):f}"


def format_int_with_spaces(value: Decimal) -> str:
    n = int(quant_0(value))
    return f"{n:,}".replace(",", " ")


def format_amount(value: Decimal) -> str:
    if value == value.to_integral():
        return f"{int(value):,}".replace(",", " ")

    normalized = format(value.normalize(), "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    return normalized


def format_percent(value: Decimal) -> str:
    normalized = format(value.normalize(), "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    return normalized.replace(".", ",")


def format_int_with_apostrophe(value: Decimal) -> str:
    n = int(quant_0(value))
    return f"{n:,}".replace(",", "'")
