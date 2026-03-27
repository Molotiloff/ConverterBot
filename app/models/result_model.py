from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ConversionResult:
    from_currency: str
    to_currency: str
    amount: Decimal
    rate: Decimal
    converted: Decimal
    percent: Decimal | None = None
    gross: Decimal | None = None
    sign: int = -1
    is_markup: bool = False