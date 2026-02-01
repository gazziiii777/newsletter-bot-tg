from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_reply_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Показать юзеров"),
                KeyboardButton(text="Добавить юзера"),
                KeyboardButton(text="Удалить юзера"),
            ],
            [
                KeyboardButton(text="Текст сообщения"),
                KeyboardButton(text="Рассылка"),
            ],
        ],
        resize_keyboard=True
    )
