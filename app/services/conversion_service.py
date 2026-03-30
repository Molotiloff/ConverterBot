from decimal import Decimal

from app.models.request_model import ConversionRequest
from app.models.result_model import ConversionResult
from app.utils.decimal_utils import quant_2, quant_3


class ConversionService:
    def __init__(self, xe_client):
        self.xe_client = xe_client

    def calculate(self, request: ConversionRequest) -> ConversionResult:
        rate_info = self.xe_client.get_pair_info(
            request.from_currency,
            request.to_currency,
        )

        converted = quant_2(request.amount * rate_info.rate)

        final_amount = None
        if request.percent is not None:
            percent_fraction = request.percent / Decimal("100")

            if request.is_markup:
                if request.sign > 0:
                    # +0.3%% -> converted / (1 - p)
                    denominator = Decimal("1") - percent_fraction
                else:
                    # -0.3%% -> converted / (1 + p)
                    denominator = Decimal("1") + percent_fraction

                if denominator <= 0:
                    raise ValueError("Некорректный процент для расчета")

                final_amount = quant_3(converted / denominator)

            else:
                if request.sign > 0:
                    # +0.3% -> converted * (1 + p)
                    final_amount = quant_3(converted * (Decimal("1") + percent_fraction))
                else:
                    # -0.3% -> converted * (1 - p)
                    final_amount = quant_3(converted * (Decimal("1") - percent_fraction))

        return ConversionResult(
            from_currency=request.from_currency,
            to_currency=request.to_currency,
            amount=request.amount,
            rate=rate_info.rate,
            converted=converted,
            percent=request.percent,
            final_amount=final_amount,
            sign=request.sign,
            is_markup=request.is_markup,
        )