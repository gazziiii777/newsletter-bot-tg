from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from infrastructure.config import settings
from app.keyboards.reply import main_reply_kb
from infrastructure.logger import get_logger

router = Router()
log = get_logger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    if message.from_user.id not in settings.allowed_user_ids:
        await message.answer("так нельзя, напиши создателю @gazziiii777")
        return
    await message.answer("Привет, я бот для рассылки.", reply_markup=main_reply_kb())
