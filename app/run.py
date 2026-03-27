import asyncio

from app.bot_app import BotApp


async def main():
    app = BotApp()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())