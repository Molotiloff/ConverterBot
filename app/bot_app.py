import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.clients import XeClient
from app.config import get_settings
from app.formatters import ResponseFormatter
from app.handlers.inline_handler import InlineQueryHandler
from app.handlers.message_handler import XeMessageHandler
from app.handlers.start_handler import start_handler
from app.parsers import CommandParser
from app.renderers import RateCardRenderer
from app.services import ConversionService
from app.web import ApiImagePublisher, ImageServer, ImageStore, LocalImagePublisher


class BotApp:
    def __init__(self):
        self.settings = get_settings()

        self.xe_client = XeClient(
            base_url=self.settings.xe_base_url,
            username=self.settings.xe_username,
            password=self.settings.xe_password,
        )
        self.parser = CommandParser()
        self.service = ConversionService(self.xe_client)
        self.formatter = ResponseFormatter()
        self.renderer = RateCardRenderer(
            xe_url_template=self.formatter.XE_URL_TEMPLATE,
            brand_name="SkyEX",
        )

        self.image_store = ImageStore(
            ttl_seconds=self.settings.image_ttl_seconds,
            max_items=self.settings.image_max_items,
        )
        self.image_server = None
        if self.settings.image_api_base_url:
            self.image_publisher = ApiImagePublisher(
                base_url=self.settings.image_api_base_url,
                api_token=self.settings.api_token,
            )
        else:
            self.image_server = ImageServer(
                host=self.settings.app_host,
                port=self.settings.app_port,
                image_store=self.image_store,
            )
            self.image_publisher = LocalImagePublisher(
                image_store=self.image_store,
                public_base_url=self.settings.public_base_url,
            )

        self.inline_handler = InlineQueryHandler(
            parser=self.parser,
            conversion_service=self.service,
            formatter=self.formatter,
            renderer=self.renderer,
            image_publisher=self.image_publisher,
        )

        self.message_handler = XeMessageHandler(
            parser=self.parser,
            conversion_service=self.service,
            formatter=self.formatter,
            renderer=self.renderer,
            image_publisher=self.image_publisher,
        )

        self.dispatcher = Dispatcher()
        self.bot = Bot(
            token=self.settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        self._register_handlers()

    def _register_handlers(self) -> None:
        self.dispatcher.message.register(start_handler, F.text == "/start")
        self.dispatcher.message.register(
            self.message_handler.handle,
            F.text.regexp(r"^/xe(?:@\w+)?\s+"),
        )
        self.dispatcher.inline_query.register(self.inline_handler.handle)

    async def run(self) -> None:
        logging.basicConfig(level=logging.INFO)

        if self.image_server:
            await self.image_server.start()
        try:
            await self.dispatcher.start_polling(self.bot)
        finally:
            if self.image_server:
                await self.image_server.stop()
