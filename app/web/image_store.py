from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass


@dataclass
class StoredImage:
    content: bytes
    content_type: str
    created_at: float
    expires_at: float


class ImageStore:
    def __init__(self, ttl_seconds: int = 1800, max_items: int = 500):
        self.ttl_seconds = ttl_seconds
        self.max_items = max_items
        self._items: dict[str, StoredImage] = {}
        self._lock = asyncio.Lock()

    async def put(
        self,
        content: bytes,
        content_type: str = "image/png",
        ttl_seconds: int | None = None,
    ) -> str:
        ttl = ttl_seconds or self.ttl_seconds
        now = time.time()
        image_id = uuid.uuid4().hex

        async with self._lock:
            self._items[image_id] = StoredImage(
                content=content,
                content_type=content_type,
                created_at=now,
                expires_at=now + ttl,
            )
            await self._cleanup_locked()

        return image_id

    async def get(self, image_id: str) -> StoredImage | None:
        now = time.time()

        async with self._lock:
            item = self._items.get(image_id)
            if item is None:
                return None

            if item.expires_at <= now:
                self._items.pop(image_id, None)
                return None

            return item

    async def delete(self, image_id: str) -> None:
        async with self._lock:
            self._items.pop(image_id, None)

    async def cleanup(self) -> int:
        async with self._lock:
            return await self._cleanup_locked()

    async def _cleanup_locked(self) -> int:
        now = time.time()
        expired_keys = [
            key for key, item in self._items.items()
            if item.expires_at <= now
        ]

        for key in expired_keys:
            self._items.pop(key, None)

        if len(self._items) > self.max_items:
            overflow = len(self._items) - self.max_items
            oldest_keys = sorted(
                self._items.keys(),
                key=lambda key: self._items[key].created_at,
            )[:overflow]
            for key in oldest_keys:
                self._items.pop(key, None)

        return len(expired_keys)