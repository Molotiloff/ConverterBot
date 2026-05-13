from __future__ import annotations

import hashlib
import hmac

from aiohttp import web


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def require_bearer_token_hash(request: web.Request, expected_token_hash: str) -> None:
    header = request.headers.get("Authorization", "")
    scheme, _, token = header.partition(" ")

    if (
        scheme.lower() != "bearer"
        or not token
        or not hmac.compare_digest(hash_token(token), expected_token_hash)
    ):
        raise web.HTTPUnauthorized(
            text='{"error":{"code":"unauthorized","message":"Invalid API token"}}',
            content_type="application/json",
        )
