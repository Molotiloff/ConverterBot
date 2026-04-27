import asyncio

from aiogram.enums import ParseMode
from aiogram.types import Message


class XeMessageHandler:
    def __init__(
        self,
        parser,
        conversion_service,
        formatter,
        renderer,
        image_publisher,
    ):
        self.parser = parser
        self.conversion_service = conversion_service
        self.formatter = formatter
        self.renderer = renderer
        self.image_publisher = image_publisher

    async def handle(self, message: Message):
        try:
            request_model = self.parser.parse(message.text or "")

            result = await asyncio.to_thread(
                self.conversion_service.calculate,
                request_model,
            )

            image_buffer = await asyncio.to_thread(
                self.renderer.render,
                result,
            )

            image_url = await self.image_publisher.publish(
                content=image_buffer.getvalue(),
                content_type="image/png",
            )

            response_text = self.formatter.build_inline_article_text(
                result=result,
                image_url=image_url,
            )

            await message.reply(
                response_text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False,
            )

        except Exception as e:
            await message.reply(f"Ошибка: {e}")
