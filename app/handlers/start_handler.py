from aiogram.types import Message


async def start_handler(message: Message):
    await message.reply(
        "Примеры:\n\n"
        "<code>/xe AED 1000</code>\n"
        "<code>/xe EUR AED 1000</code>\n"
        "<code>/xe € $ 100</code>\n"
        "<code>/xe D € 100+0.3%%</code>\n"
        "<code>/xe EUR 100-0.3%</code>\n"
        "<code>/xe EUR 100-0.3%%</code>\n"
        "<code>/xe EUR 100+0.3%</code>\n"
        "<code>/xe EUR 100+0.3%%</code>\n\n"
        "Коды валют:\n"
        "<code>€ → EUR</code>\n"
        "<code>£ → GBP</code>\n"
        "<code>₣ → CHF</code>\n"
        "<code>¥ → CNY</code>\n"
        "<code>$, d → USD</code>\n\n"
    )