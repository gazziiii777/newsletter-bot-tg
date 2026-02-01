"""Создаёт Telethon-сессию my_session для рассылки."""
import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

API_ID = int(os.getenv("TELETHON_API_ID", ""))
API_HASH = os.getenv("TELETHON_API_HASH", "")
SESSION = os.getenv("TELETHON_SESSION", "my_session")


async def main() -> None:
    async with TelegramClient(SESSION, API_ID, API_HASH) as client:
        await client.get_me()
    print(f"Сессия {SESSION} создана.")


if __name__ == "__main__":
    asyncio.run(main())
