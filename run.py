import os
import logging
import asyncio
import aioredis

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from database.database_manager import async_main
from bot.handlers.player.registration_handlers import player
from bot.handlers.admin.admin_handlers import admin
from bot.handlers.player.game_processing_handlers import menu
from bot.handlers.player.payment_handlers import payment
from bot.handlers.player.casino_handler import casino
from bot.handlers.player.inventory_handler import inventory
from bot.handlers.player.music_handler import music
from bot.handlers.player.music_handler import update_number_of_listeners


async def setup_redis():
    redis = aioredis.from_url(os.getenv('REDIS_URL'), decode_responses=True)


async def main():
    await async_main()
    load_dotenv()
    redis = await setup_redis()
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_router(player)
    dp.include_router(admin)
    dp.include_router(menu)
    dp.include_router(payment)
    dp.include_router(casino)
    dp.include_router(inventory)
    dp.include_router(music)

    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(update_number_of_listeners, 'interval', seconds=10)
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
