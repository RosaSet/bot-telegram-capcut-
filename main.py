import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import BOT_TOKEN
import database as db
from handlers import user_handlers, admin_handlers

async def main():
    # Setup DB
    db.setup_db()
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Error: Please set your BOT_TOKEN in config.py")
        sys.exit(1)
        
    bot = Bot(token=BOT_TOKEN)
    
    # Remove Bot Menu Commands
    await bot.delete_my_commands()
    
    dp = Dispatcher()

    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)

    print("Bot is starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
