from decimal import Decimal
from unittest import TestCase

from app.api.schemas import build_request_from_payload, parse_bool, parse_percent_mode, result_to_payload
from app.models.result_model import ConversionResult


class ApiSchemasTest(TestCase):
    def test_build_request_from_structured_payload(self):
        request = build_request_from_payload({
            "from_currency": "eur",
            "to_currency": "$",
            "amount": "1000",
            "percent": "0.3",
            "sign": -1,
            "is_markup": False,
        })

        self.assertEqual(request.from_currency, "EUR")
        self.assertEqual(request.to_currency, "USD")
        self.assertEqual(request.amount, Decimal("1000"))
        self.assertEqual(request.percent, Decimal("0.3"))
        self.assertEqual(request.sign, -1)
        self.assertFalse(request.is_markup)

    def test_invalid_sign_raises_value_error(self):
        with self.assertRaisesRegex(ValueError, "sign"):
            build_request_from_payload({
                "from_currency": "EUR",
                "to_currency": "USD",
                "amount": "100",
                "sign": 0,
            })

    def test_percent_mode_percent_maps_to_regular_percent(self):
        request = build_request_from_payload({
            "from_currency": "EUR",
            "to_currency": "USD",
            "amount": "100",
            "percent": "0.3",
            "sign": -1,
            "percent_mode": "%",
        })

        self.assertFalse(request.is_markup)

    def test_percent_mode_double_percent_maps_to_markup(self):
        request = build_request_from_payload({
            "from_currency": "EUR",
            "to_currency": "USD",
            "amount": "100",
            "percent": "0.3",
            "sign": -1,
            "percent_mode": "%%",
        })

        self.assertTrue(request.is_markup)

    def test_percent_mode_conflict_with_legacy_is_markup_raises_value_error(self):
        with self.assertRaisesRegex(ValueError, "конфликтует"):
            parse_percent_mode({
                "percent_mode": "%%",
                "is_markup": False,
            })

    def test_parse_bool_accepts_json_and_string_values(self):
        self.assertTrue(parse_bool(True))
        self.assertTrue(parse_bool("true"))
        self.assertFalse(parse_bool(False))
        self.assertFalse(parse_bool("false"))

    def test_result_to_payload_keeps_decimals_as_strings(self):
        payload = result_to_payload(
            ConversionResult(
                from_currency="EUR",
                to_currency="USD",
                amount=Decimal("100"),
                rate=Decimal("1.1529"),
                converted=Decimal("115.29"),
                percent=Decimal("0.3"),
                final_amount=Decimal("114.944"),
                sign=-1,
                is_markup=False,
            ),
            image_url="https://example.ngrok.app/images/test.png",
        )

        self.assertEqual(payload["amount"], "100")
        self.assertEqual(payload["rate"], "1.1529")
        self.assertEqual(payload["converted"], "115.29")
        self.assertEqual(payload["percent_mode"], "%")
        self.assertEqual(payload["final_amount"], "114.944")
        self.assertEqual(payload["image_url"], "https://example.ngrok.app/images/test.png")
