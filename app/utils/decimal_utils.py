from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


def parse_decimal(value: str) -> Decimal:
    normalized = value.replace(",", ".").strip()
    try:
        return Decimal(normalized)
    except InvalidOperation as e:
        raise ValueError(f"Некорректное число: {value}") from e


# ======================
# Quantization
# ======================

def quant_2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def quant_0(value: Decimal) -> Decimal:
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


# ======================
# Formatters
# ======================

def format_decimal_2(value: Decimal) -> str:
    """Всегда 2 знака после запятой"""
    return f"{quant_2(value):f}"


def format_decimal_compact(value: Decimal, places: int = 4) -> str:
    """
    Для формул:
    1.15164 -> 1.1516
    1.00300 -> 1.003
    1.00000 -> 1
    """
    quant = Decimal("1." + ("0" * places))
    normalized = value.quantize(quant, rounding=ROUND_HALF_UP)

    text = f"{normalized:f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text


def format_amount(value: Decimal) -> str:
    """
    1000 -> 1 000
    1000.50 -> 1000.5
    """
    if value == value.to_integral():
        return f"{int(value):,}".replace(",", " ")

    normalized = format(value.normalize(), "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")

    return normalized


def format_percent(value: Decimal) -> str:
    """
    0.3 -> 0,3
    1.00 -> 1
    """
    normalized = format(value.normalize(), "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")

    return normalized.replace(".", ",")