import asyncio
import logging
from aiogram import Bot, Dispatcher
from .config import BOT_TOKEN
from .db import init_db
from .handlers import start, menu, admin

logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    # Include routers: admin first, then others
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(menu.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
