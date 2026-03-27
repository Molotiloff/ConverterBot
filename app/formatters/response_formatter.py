from decimal import Decimal
from html import escape

from app.models.result_model import ConversionResult
from app.utils.decimal_utils import (
    format_amount,
    format_decimal_2,
    format_int_with_apostrophe,
    format_percent,
)


class ResponseFormatter:
    XE_URL_TEMPLATE = (
        "https://www.xe.com/currencyconverter/convert/"
        "?Amount=1&From={from_currency}&To={to_currency}"
    )

    SKYEX_URL = "https://t.me/skyex_world"

    def build_inline_article_text(
        self,
        result: ConversionResult,
        image_url: str,
    ) -> str:
        safe_image_url = escape(image_url, quote=True)
        safe_skyex = escape(self.SKYEX_URL, quote=True)

        amount_str = escape(format_amount(result.amount))
        rate_str = escape(format_decimal_2(result.rate))
        converted_str = escape(format_decimal_2(result.converted))
        from_currency = escape(result.from_currency)
        to_currency = escape(result.to_currency)

        header = f"{amount_str} {from_currency} = {converted_str} {to_currency}"
        calc_block = self._build_calc_block(result)

        return (
            f'<a href="{safe_image_url}">&#8205;</a>\n'
            f"{header}\n"
            f"-----\n"
            f"{calc_block}\n\n"
            f"Кросс по xe.com 1 {from_currency} = {rate_str} {to_currency}\n"
            f"----\n"
            f'<a href="{safe_skyex}">Powered by SkyEX</a>'
        )

    def build_preview_text(self, result: ConversionResult) -> str:
        converted_str = format_decimal_2(result.converted)

        if result.percent is None:
            return (
                f"{format_amount(result.amount)} {result.from_currency} → "
                f"{converted_str} {result.to_currency}"
            )

        sign_symbol = "+" if result.sign > 0 else "-"
        suffix = "%%" if result.is_markup else "%"
        percent_str = format_percent(result.percent)

        return (
            f"{format_amount(result.amount)} {result.from_currency} → "
            f"{converted_str} {result.to_currency} "
            f"({sign_symbol}{percent_str}{suffix})"
        )

    def _build_calc_block(self, result: ConversionResult) -> str:
        if result.percent is None or result.gross is None:
            amount_str = escape(format_amount(result.amount))
            rate_str = escape(format_decimal_2(result.rate))
            converted_str = escape(format_decimal_2(result.converted))
            return f"{amount_str}*{rate_str} = {converted_str}"

        amount_str = escape(format_amount(result.amount))
        rate_str = escape(format_decimal_2(result.rate))
        converted_str = escape(format_decimal_2(result.converted))
        gross_str = escape(format_int_with_apostrophe(result.gross))

        percent_fraction = result.percent / Decimal("100")

        if result.is_markup:
            if result.sign > 0:
                divisor = format_decimal_2(Decimal("1") - percent_fraction)
            else:
                divisor = format_decimal_2(Decimal("1") + percent_fraction)

            divisor = escape(divisor)
            return f"{amount_str}*{rate_str}/{divisor} = {gross_str}"

        if result.sign > 0:
            multiplier = format_decimal_2(Decimal("1") + percent_fraction)
        else:
            multiplier = format_decimal_2(Decimal("1") - percent_fraction)

        multiplier = escape(multiplier)
        return f"{converted_str}*{multiplier} = {gross_str}"