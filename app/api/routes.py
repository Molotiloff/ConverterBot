from __future__ import annotations

import asyncio
import logging
from json import JSONDecodeError

import requests
from aiohttp import web
from aiohttp.web_exceptions import HTTPBadRequest

from app.api.auth import require_bearer_token_hash
from app.api.schemas import build_request_from_payload, parse_bool, result_to_payload

logger = logging.getLogger(__name__)


def json_error(status: int, code: str, message: str) -> web.Response:
    return web.json_response(
        {"error": {"code": code, "message": message}},
        status=status,
    )


async def health_handler(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


async def convert_handler(request: web.Request) -> web.Response:
    require_bearer_token_hash(request, request.app["api_token_hash"])

    try:
        payload = await request.json()
    except (JSONDecodeError, HTTPBadRequest):
        return json_error(400, "invalid_json", "Некорректный JSON")

    if not isinstance(payload, dict):
        return json_error(400, "invalid_payload", "JSON body должен быть объектом")

    try:
        if payload.get("text") is not None:
            request_model = request.app["parser"].parse(str(payload["text"]))
        else:
            request_model = build_request_from_payload(payload)

        result = await asyncio.to_thread(
            request.app["conversion_service"].calculate,
            request_model,
        )

        image_url = None
        if parse_bool(payload.get("include_image"), default=False):
            image_buffer = await asyncio.to_thread(
                request.app["renderer"].render,
                result,
            )
            image_id = await request.app["image_store"].put(
                content=image_buffer.getvalue(),
                content_type="image/png",
            )
            image_url = f'{request.app["public_base_url"]}/images/{image_id}.png'

        return web.json_response(result_to_payload(result, image_url=image_url))

    except ValueError as e:
        return json_error(400, "validation_error", str(e))
    except requests.RequestException as e:
        logger.exception("XE request failed")
        return json_error(502, "xe_error", str(e))
    except Exception:
        logger.exception("Unexpected API error")
        return json_error(500, "internal_error", "Внутренняя ошибка сервиса")


async def upload_image_handler(request: web.Request) -> web.Response:
    require_bearer_token_hash(request, request.app["api_token_hash"])

    content_type = request.headers.get("Content-Type", "").split(";", 1)[0]
    if content_type != "image/png":
        return json_error(400, "invalid_content_type", "Поддерживается только image/png")

    content = await request.read()
    if not content:
        return json_error(400, "empty_image", "Тело запроса с картинкой пустое")

    image_id = await request.app["image_store"].put(
        content=content,
        content_type="image/png",
    )
    image_url = f'{request.app["public_base_url"]}/images/{image_id}.png'

    return web.json_response({"image_url": image_url})


async def image_handler(request: web.Request) -> web.Response:
    image_id = request.match_info["image_id"]
    item = await request.app["image_store"].get(image_id)

    if item is None:
        raise web.HTTPNotFound(text="Image not found or expired")

    return web.Response(
        body=item.content,
        content_type=item.content_type,
        headers={"Cache-Control": "public, max-age=300"},
    )


def setup_routes(app: web.Application) -> None:
    app.router.add_get("/health", health_handler)
    app.router.add_post("/api/v1/convert", convert_handler)
    app.router.add_post("/api/v1/images", upload_image_handler)
    app.router.add_get("/images/{image_id:[0-9a-f]+}.{ext}", image_handler)
