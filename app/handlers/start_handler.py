from aiogram.types import Message


async def start_handler(message: Message):
    await message.reply(
        "Примеры:\n\n"
        "<code>/xe AED 1000</code>\n"
        "<code>/xe EUR AED 1000</code>\n"
        "<code>/xe EUR AED 1000-0.2%</code>\n\n"
        "Inline:\n"
        "<code>@Post_CS_Bot AED 1000</code>\n"
        "<code>@Post_CS_Bot EUR AED 1000</code>\n"
        "<code>@Post_CS_Bot EUR AED 1000-0.2%</code>"
    )