import asyncio

from aiogram import executor
from loader import dp
import middlewares, filters, handlers
import logging

logging.basicConfig(level=logging.INFO)
from server.server import run_fastapi


async def run_bot():
    await dp.start_polling()


async def main():
    await asyncio.gather(run_bot(), run_fastapi())


if __name__ == '__main__':
    asyncio.run(main())
