from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.models.request_model import ConversionRequest
from app.models.result_model import ConversionResult
from app.utils import CurrencyNormalizer, parse_decimal


def parse_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ("1", "true", "yes", "on"):
            return True
        if normalized in ("0", "false", "no", "off"):
            return False

    raise ValueError("Boolean поле должно быть true или false")


def parse_percent_mode(payload: dict[str, Any]) -> bool:
    mode = payload.get("percent_mode")
    has_legacy_markup = payload.get("is_markup") is not None
    legacy_is_markup = parse_bool(payload.get("is_markup"), default=False)

    if mode is None:
        return legacy_is_markup

    normalized = str(mode).strip().lower()
    modes = {
        "%": False,
        "percent": False,
        "commission": False,
        "fee": False,
        "%%": True,
        "markup": True,
    }

    if normalized not in modes:
        raise ValueError("percent_mode должен быть '%' или '%%'")

    is_markup = modes[normalized]
    if has_legacy_markup and legacy_is_markup != is_markup:
        raise ValueError("percent_mode конфликтует с is_markup")

    return is_markup


def build_request_from_payload(payload: dict[str, Any]) -> ConversionRequest:
    try:
        from_currency = CurrencyNormalizer.normalize_token(str(payload["from_currency"]))
        to_currency = CurrencyNormalizer.normalize_token(str(payload["to_currency"]))
        amount = parse_decimal(str(payload["amount"]))
    except KeyError as e:
        raise ValueError(f"Обязательное поле отсутствует: {e.args[0]}") from e

    percent = None
    if payload.get("percent") is not None:
        percent = parse_decimal(str(payload["percent"]))

    sign = int(payload.get("sign", -1))
    if sign not in (-1, 1):
        raise ValueError("sign должен быть -1 или 1")

    request = ConversionRequest(
        from_currency=from_currency,
        to_currency=to_currency,
        amount=amount,
        percent=percent,
        sign=sign,
        is_markup=parse_percent_mode(payload),
    )
    validate_request(request)
    return request


def validate_request(request: ConversionRequest) -> None:
    if request.amount <= 0:
        raise ValueError("Сумма должна быть больше 0")

    if request.percent is not None:
        if request.percent < 0:
            raise ValueError("Процент не может быть отрицательным")
        if request.percent >= Decimal("100"):
            raise ValueError("Процент должен быть меньше 100%")


def result_to_payload(
    result: ConversionResult,
    image_url: str | None = None,
) -> dict[str, Any]:
    final_amount = result.final_amount if result.final_amount is not None else result.converted

    payload = {
        "from_currency": result.from_currency,
        "to_currency": result.to_currency,
        "amount": str(result.amount),
        "rate": str(result.rate),
        "converted": str(result.converted),
        "percent": str(result.percent) if result.percent is not None else None,
        "percent_mode": "%%" if result.is_markup else "%",
        "final_amount": str(final_amount),
        "sign": result.sign,
        "is_markup": result.is_markup,
    }

    if image_url is not None:
        payload["image_url"] = image_url

    return payload
