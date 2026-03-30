from __future__ import annotations

from decimal import Decimal
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from app.models.result_model import ConversionResult
from app.utils.decimal_utils import (
    format_amount,
    format_decimal_2,
    format_decimal_3,
    format_decimal_compact,
    format_percent,
)


class RateCardRenderer:
    WIDTH = 1200
    HEIGHT_WITH_PERCENT = 520
    HEIGHT_NO_PERCENT = 460

    PADDING_X = 70
    PADDING_Y = 60

    BG_COLOR = "#111827"
    CARD_COLOR = "#1F2937"
    ACCENT_COLOR = "#8B5CF6"
    TEXT_PRIMARY = "#F9FAFB"
    TEXT_SECONDARY = "#D1D5DB"
    TEXT_MUTED = "#9CA3AF"
    DIVIDER = "#374151"

    def __init__(
        self,
        xe_url_template: str,
        brand_name: str = "SKYEX",
    ):
        self.xe_url_template = xe_url_template
        self.brand_name = brand_name

        self.font_title = self._load_font(56, bold=True)
        self.font_medium = self._load_font(38, bold=True)
        self.font_regular = self._load_font(34, bold=False)
        self.font_small = self._load_font(28, bold=False)

    def _load_font(self, size: int, bold: bool = False):
        candidates = (
            [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/Library/Fonts/Arial Bold.ttf",
                "arialbd.ttf",
            ]
            if bold
            else [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/Library/Fonts/Arial.ttf",
                "arial.ttf",
            ]
        )

        for path in candidates:
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue

        return ImageFont.load_default()

    def _text_bbox(self, draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        return right - left, bottom - top

    def _line(self, draw: ImageDraw.ImageDraw, y: int, width: int) -> None:
        draw.line(
            [(self.PADDING_X, y), (width - self.PADDING_X, y)],
            fill=self.DIVIDER,
            width=2,
        )

    def get_size(self, result: ConversionResult) -> tuple[int, int]:
        height = (
            self.HEIGHT_WITH_PERCENT
            if result.percent is not None and result.final_amount is not None
            else self.HEIGHT_NO_PERCENT
        )
        return self.WIDTH, height

    def _build_calc_block(self, result: ConversionResult) -> tuple[str, str | None]:
        amount_str = format_amount(result.amount)
        rate_formula_str = format_decimal_compact(result.rate, 4)
        converted_str = format_decimal_2(result.converted)

        first_line = f"{amount_str} × {rate_formula_str} = {converted_str}"

        if result.percent is None or result.final_amount is None:
            return first_line, None

        final_str = format_decimal_3(result.final_amount)
        percent_str = format_percent(result.percent)
        percent_fraction = result.percent / Decimal("100")

        if result.is_markup:
            if result.sign > 0:
                second_line = f"{converted_str}/(1-{percent_str}%) = {final_str}"
            else:
                divisor = format_decimal_compact(Decimal("1") + percent_fraction, 4)
                second_line = f"{converted_str}/{divisor} = {final_str}"
            return first_line, second_line

        if result.sign > 0:
            second_line = f"{converted_str}+{percent_str}% = {final_str}"
        else:
            second_line = f"{converted_str}-{percent_str}% = {final_str}"

        return first_line, second_line

    def render(self, result: ConversionResult) -> BytesIO:
        amount_str = format_amount(result.amount)
        final_str = (
            format_decimal_3(result.final_amount)
            if result.final_amount is not None
            else format_decimal_2(result.converted)
        )
        rate_str = format_decimal_compact(result.rate, 4)

        header_line = f"{amount_str} {result.from_currency} = {final_str} {result.to_currency}"
        cross_line = f"1 {result.from_currency} = {rate_str} {result.to_currency}"

        calc_1, calc_2 = self._build_calc_block(result)

        width, height = self.get_size(result)

        image = Image.new("RGB", (width, height), self.BG_COLOR)
        draw = ImageDraw.Draw(image)

        card_margin = 24
        draw.rounded_rectangle(
            [card_margin, card_margin, width - card_margin, height - card_margin],
            radius=36,
            fill=self.CARD_COLOR,
        )

        x = self.PADDING_X
        y = self.PADDING_Y

        draw.rounded_rectangle(
            [x, y, x + 180, y + 14],
            radius=7,
            fill=self.ACCENT_COLOR,
        )
        y += 42

        draw.text((x, y), header_line, font=self.font_title, fill=self.TEXT_PRIMARY)
        _, header_h = self._text_bbox(draw, header_line, self.font_title)
        y += header_h + 34

        draw.text((x, y), cross_line, font=self.font_medium, fill=self.TEXT_MUTED)
        _, cross_h = self._text_bbox(draw, cross_line, self.font_medium)
        y += cross_h + 34

        self._line(draw, y, width)
        y += 34

        draw.text((x, y), calc_1, font=self.font_regular, fill=self.TEXT_PRIMARY)
        _, calc1_h = self._text_bbox(draw, calc_1, self.font_regular)
        y += calc1_h + 20

        if calc_2:
            draw.text((x, y), calc_2, font=self.font_regular, fill=self.TEXT_PRIMARY)

        footer_text = f"Powered by {self.brand_name}"
        _, footer_h = self._text_bbox(draw, footer_text, self.font_small)
        footer_margin = 36
        footer_y = height - card_margin - footer_margin - footer_h

        self._line(draw, footer_y - 18, width)
        draw.text((x, footer_y), footer_text, font=self.font_small, fill=self.TEXT_SECONDARY)

        buffer = BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)
        return buffer