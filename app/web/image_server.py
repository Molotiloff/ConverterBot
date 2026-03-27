from __future__ import annotations

import asyncio
import contextlib

from aiohttp import web

from app.web.image_store import ImageStore


class ImageServer:
    def __init__(self, host: str, port: int, image_store: ImageStore):
        self.host = host
        self.port = port
        self.image_store = image_store

        self._app = web.Application()
        self._app.router.add_get(
            "/images/{image_id:[0-9a-f]+}.{ext}",
            self.handle_get_image,
        )

        self._runner: web.AppRunner | None = None
        self._site: web.TCPSite | None = None
        self._cleanup_task: asyncio.Task | None = None

    async def start(self) -> None:
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()

        self._site = web.TCPSite(self._runner, host=self.host, port=self.port)
        await self._site.start()

        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self) -> None:
        if self._cleanup_task:
            self._cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._cleanup_task

        if self._runner:
            await self._runner.cleanup()

    async def handle_get_image(self, request: web.Request) -> web.Response:
        image_id = request.match_info["image_id"]
        item = await self.image_store.get(image_id)

        if item is None:
            raise web.HTTPNotFound(text="Image not found or expired")

        return web.Response(
            body=item.content,
            content_type=item.content_type,
            headers={
                "Cache-Control": "public, max-age=300",
            },
        )

    async def _cleanup_loop(self) -> None:
        while True:
            await asyncio.sleep(60)
            await self.image_store.cleanup()