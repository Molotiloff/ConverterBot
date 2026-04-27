from aiohttp import web


def require_bearer_token(request: web.Request, expected_token: str) -> None:
    header = request.headers.get("Authorization", "")
    scheme, _, token = header.partition(" ")

    if scheme.lower() != "bearer" or not token or token != expected_token:
        raise web.HTTPUnauthorized(
            text='{"error":{"code":"unauthorized","message":"Invalid API token"}}',
            content_type="application/json",
        )
