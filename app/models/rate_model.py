from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class RateInfo:
    from_currency: str
    to_currency: str
    rate: Decimal
    trend: str | None
    rate_change: Decimal
    percentage_change: Decimal