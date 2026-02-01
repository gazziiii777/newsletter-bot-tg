from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_inline_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть меню",
                                  callback_data="open_menu")],
        ]
    )


def message_edit_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Редактировать",
                                  callback_data="message_edit")],
        ]
    )


def message_save_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Сохранить", callback_data="message_save")],
        ]
    )


def broadcast_start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Начать рассылку", callback_data="broadcast_start")],
        ]
    )
