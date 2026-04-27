import logging

from aiohttp import web

from app.api import create_api_app
from app.clients import XeClient
from app.config import get_api_settings
from app.formatters import ResponseFormatter
from app.parsers import CommandParser
from app.renderers import RateCardRenderer
from app.services import ConversionService
from app.web import ImageStore


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    settings = get_api_settings()
    xe_client = XeClient(
        base_url=settings.xe_base_url,
        username=settings.xe_username,
        password=settings.xe_password,
    )
    parser = CommandParser()
    conversion_service = ConversionService(xe_client)
    formatter = ResponseFormatter()
    renderer = RateCardRenderer(
        xe_url_template=formatter.XE_URL_TEMPLATE,
        brand_name="SkyEX",
    )
    image_store = ImageStore(
        ttl_seconds=settings.image_ttl_seconds,
        max_items=settings.image_max_items,
    )

    app = create_api_app(
        api_token=settings.api_token,
        public_base_url=settings.public_base_url,
        parser=parser,
        conversion_service=conversion_service,
        renderer=renderer,
        image_store=image_store,
        rate_limit_requests=settings.api_rate_limit_requests,
        rate_limit_seconds=settings.api_rate_limit_seconds,
    )

    web.run_app(app, host=settings.api_host, port=settings.api_port)


if __name__ == "__main__":
    main()
