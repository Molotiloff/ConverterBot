import asyncio
import uuid

from aiogram.enums import ParseMode
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)


class InlineQueryHandler:
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

    async def handle(self, inline_query: InlineQuery):
        query = (inline_query.query or "").strip()

        if not query:
            await inline_query.answer(
                results=[],
                cache_time=1,
                is_personal=True,
            )
            return

        try:
            request_model = self.parser.parse(query)

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

            preview_text = self.formatter.build_preview_text(result)
            message_text = self.formatter.build_inline_article_text(
                result=result,
                image_url=image_url,
            )

            article = InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="Посчитать конвертацию",
                description=preview_text,
                input_message_content=InputTextMessageContent(
                    message_text=message_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=False,
                ),
            )

            await inline_query.answer(
                results=[article],
                cache_time=1,
                is_personal=True,
            )

        except Exception as e:
            await inline_query.answer(
                results=[],
                switch_pm_text=f"Ошибка: {e}",
                switch_pm_parameter="error",
                cache_time=1,
                is_personal=True,
            )
