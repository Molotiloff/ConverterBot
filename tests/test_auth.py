from unittest import TestCase

from aiohttp import web

from app.api.auth import hash_token, require_bearer_token_hash


class FakeRequest:
    def __init__(self, authorization: str):
        self.headers = {"Authorization": authorization}


class AuthTest(TestCase):
    def test_hash_token_is_sha256_hex(self):
        self.assertEqual(
            hash_token("secret-token"),
            "930bbdc51b6aed5c2a5678fd6e28dee7a05e8a4b643cfc0b4427c3efb86c0d94",
        )

    def test_accepts_valid_plain_bearer_token(self):
        request = FakeRequest("Bearer secret-token")

        require_bearer_token_hash(request, hash_token("secret-token"))

    def test_rejects_invalid_bearer_token(self):
        request = FakeRequest("Bearer wrong-token")

        with self.assertRaises(web.HTTPUnauthorized):
            require_bearer_token_hash(request, hash_token("secret-token"))
