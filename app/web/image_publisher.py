from __future__ import annotations

import asyncio

import requests


class LocalImagePublisher:
    def __init__(self, image_store, public_base_url: str):
        self.image_store = image_store
        self.public_base_url = public_base_url.rstrip("/")

    async def publish(self, content: bytes, content_type: str = "image/png") -> str:
        image_id = await self.image_store.put(
            content=content,
            content_type=content_type,
        )
        return f"{self.public_base_url}/images/{image_id}.png"


class ApiImagePublisher:
    def __init__(self, base_url: str, api_token: str, timeout: int = 20):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout = timeout

    async def publish(self, content: bytes, content_type: str = "image/png") -> str:
        return await asyncio.to_thread(self._publish_sync, content, content_type)

    def _publish_sync(self, content: bytes, content_type: str) -> str:
        response = requests.post(
            f"{self.base_url}/api/v1/images",
            data=content,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": content_type,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        image_url = data.get("image_url")
        if not image_url:
            raise ValueError("API не вернул image_url")

        return image_url
