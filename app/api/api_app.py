from __future__ import annotations

import asyncio
import contextlib

from aiohttp import web

from app.api.rate_limit import RateLimiter, build_rate_limit_middleware
from app.api.routes import setup_routes


async def _cleanup_images(app: web.Application) -> None:
    while True:
        await asyncio.sleep(60)
        await app["image_store"].cleanup()


async def _start_cleanup(app: web.Application) -> None:
    app["image_cleanup_task"] = asyncio.create_task(_cleanup_images(app))


async def _stop_cleanup(app: web.Application) -> None:
    task = app.get("image_cleanup_task")
    if task is None:
        return

    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task


def create_api_app(
    *,
    api_token_hash: str,
    public_base_url: str,
    parser,
    conversion_service,
    renderer,
    image_store,
    rate_limit_requests: int,
    rate_limit_seconds: int,
) -> web.Application:
    rate_limiter = RateLimiter(
        max_requests=rate_limit_requests,
        window_seconds=rate_limit_seconds,
    )
    app = web.Application(
        middlewares=[build_rate_limit_middleware(rate_limiter)],
        client_max_size=2 * 1024 * 1024,
    )
    app["api_token_hash"] = api_token_hash
    app["public_base_url"] = public_base_url.rstrip("/")
    app["parser"] = parser
    app["conversion_service"] = conversion_service
    app["renderer"] = renderer
    app["image_store"] = image_store

    setup_routes(app)
    app.on_startup.append(_start_cleanup)
    app.on_cleanup.append(_stop_cleanup)

    return app
