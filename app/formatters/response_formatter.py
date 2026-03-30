from decimal import Decimal
from html import escape

from app.models.result_model import ConversionResult
from app.utils.decimal_utils import (
    format_amount,
    format_decimal_2,
    format_decimal_3,
    format_decimal_compact,
    format_percent,
    format_url_amount,
)


class ResponseFormatter:
    XE_URL_TEMPLATE = (
        "https://www.xe.com/currencyconverter/convert/"
        "?Amount={amount}&From={from_currency}&To={to_currency}"
    )

    SKYEX_URL = "https://t.me/skyex_world"

    def build_inline_article_text(
        self,
        result: ConversionResult,
        image_url: str,
    ) -> str:
        safe_image_url = escape(image_url, quote=True)
        safe_skyex = escape(self.SKYEX_URL, quote=True)
        safe_xe_url = escape(self._build_xe_url(result), quote=True)

        amount_str = escape(format_amount(result.amount))
        from_currency = escape(result.from_currency)
        to_currency = escape(result.to_currency)

        final_str = (
            escape(format_decimal_3(result.final_amount))
            if result.final_amount is not None
            else escape(format_decimal_2(result.converted))
        )

        rate_str = escape(format_decimal_compact(result.rate, 4))
        header = f"{amount_str} {from_currency} = {final_str} {to_currency}"
        calc_block = self._build_calc_block(result)

        return (
            f'<a href="{safe_image_url}">&#8205;</a>\n'
            f"{header}\n"
            f"-----\n"
            f"{calc_block}\n\n"
            f"Кросс по "
            f'<a href="{safe_xe_url}">xe.com</a> '
            f"1 {from_currency} = {rate_str} {to_currency}\n"
            f"----\n"
            f'<a href="{safe_skyex}">Powered by SkyEX</a>'
        )

    def build_preview_text(self, result: ConversionResult) -> str:
        final_str = (
            format_decimal_3(result.final_amount)
            if result.final_amount is not None
            else format_decimal_2(result.converted)
        )

        if result.percent is None:
            return (
                f"{format_amount(result.amount)} {result.from_currency} → "
                f"{final_str} {result.to_currency}"
            )

        sign_symbol = "+" if result.sign > 0 else "-"
        suffix = "%%" if result.is_markup else "%"
        percent_str = format_percent(result.percent)

        return (
            f"{format_amount(result.amount)} {result.from_currency} → "
            f"{final_str} {result.to_currency} "
            f"({sign_symbol}{percent_str}{suffix})"
        )

    def _build_calc_block(self, result: ConversionResult) -> str:
        amount_str = escape(format_amount(result.amount))
        rate_formula_str = escape(format_decimal_compact(result.rate, 4))
        converted_str = escape(format_decimal_2(result.converted))

        first_line = f"{amount_str}*{rate_formula_str} = {converted_str}"

        if result.percent is None or result.final_amount is None:
            return first_line

        final_str = escape(format_decimal_3(result.final_amount))
        percent_str = escape(format_percent(result.percent))
        percent_fraction = result.percent / Decimal("100")

        if result.is_markup:
            if result.sign > 0:
                second_line = f"{converted_str}/(1-{percent_str}%) = {final_str}"
            else:
                divisor = escape(format_decimal_compact(Decimal("1") + percent_fraction, 4))
                second_line = f"{converted_str}/{divisor} = {final_str}"

            return f"{first_line}\n{second_line}"

        if result.sign > 0:
            second_line = f"{converted_str}+{percent_str}% = {final_str}"
        else:
            second_line = f"{converted_str}-{percent_str}% = {final_str}"

        return f"{first_line}\n{second_line}"

    def _build_xe_url(self, result: ConversionResult) -> str:
        return self.XE_URL_TEMPLATE.format(
            amount=format_url_amount(result.amount),
            from_currency=result.from_currency,
            to_currency=result.to_currency,
        )