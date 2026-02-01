from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from telethon import TelegramClient

from infrastructure.config import settings
from infrastructure.logger import get_logger
from app.database.messages import get_message_text, set_message_text
from app.database.users import delete_user, get_all_users, store_user
from app.keyboards.inline import (
    broadcast_start_kb,
    main_inline_kb,
    message_edit_kb,
    message_save_kb,
)
from app.keyboards.reply import main_reply_kb

router = Router()
log = get_logger(__name__)

# Состояние ожидания ввода: "add" | "delete" | None
_user_input_state: dict[int, str | None] = {}
# Состояние для текста сообщения: "create" | "edit" | None
_message_input_state: dict[int, str | None] = {}
_pending_message_text: dict[int, str] = {}
_message_prompt_id: dict[int, int] = {}


async def _send_broadcast(
    text: str,
    recipients: list[tuple[int, str]],
) -> tuple[int, int, list[str]]:
    api_id = settings.TELETHON_API_ID
    api_hash = settings.TELETHON_API_HASH
    session_name = settings.TELETHON_SESSION
    success = 0
    failed = 0
    failed_recipients: list[str] = []
    async with TelegramClient(session_name, api_id, api_hash) as client:
        for user_id, recipient in recipients:
            try:
                await client.send_message(recipient, text)
                success += 1
            except Exception as e:
                failed += 1
                failed_recipients.append(f"id={user_id}, {recipient}")
                log.exception("Ошибка отправки для id=%s, %s: %s",
                              user_id, recipient, e)
    return success, failed, failed_recipients


@router.message(F.text == "Показать юзеров")
async def show_users(message: Message) -> None:
    _user_input_state.pop(message.from_user.id, None)
    try:
        users = get_all_users()
    except Exception as e:
        log.exception("Ошибка получения списка юзеров: %s", e)
        await message.answer("Не удалось загрузить список. Попробуйте позже.")
        return
    if not users:
        await message.answer("В базе пока никого нет.")
        return
    lines = [f"• id: {uid}, username: {uname}" for uid, uname in users]
    await message.answer("Юзеры в базе:\n\n" + "\n".join(lines))


@router.message(F.text == "Добавить юзера")
async def add_user_prompt(message: Message) -> None:
    _user_input_state[message.from_user.id] = "add"
    _message_input_state.pop(message.from_user.id, None)
    await message.answer(
        "Напишите username или номер телефона через +7.\n"
        "Примеры:\n"
        "usermmame\n"
        "+71234567890"
    )


@router.message(F.text == "Удалить юзера")
async def delete_user_prompt(message: Message) -> None:
    _user_input_state[message.from_user.id] = "delete"
    _message_input_state.pop(message.from_user.id, None)
    await message.answer("Введите id пользователя (число) для удаления.\nПример: 123456789")


@router.message(F.text, lambda message: _user_input_state.get(message.from_user.id) == "add")
async def add_user_input(message: Message) -> None:
    username = (message.text or "").strip()
    if not username:
        await message.answer("Введите username (не пусто).")
        return
    _user_input_state.pop(message.from_user.id, None)
    try:
        new_id = store_user(username)
        log.info("Добавлен юзер: id=%s, username=%s", new_id, username)
        await message.answer(f"Добавлен: {username}")
    except Exception as e:
        log.exception("Ошибка добавления юзера username=%s: %s", username, e)
        await message.answer("Не удалось добавить. Попробуйте позже.")


@router.message(F.text, lambda message: _user_input_state.get(message.from_user.id) == "delete")
async def delete_user_input(message: Message) -> None:
    raw_text = (message.text or "").strip()
    if not raw_text.isdigit():
        await message.answer("Введите одно число — id пользователя.")
        return
    try:
        uid = int(raw_text)
        _user_input_state.pop(message.from_user.id, None)
        if delete_user(uid):
            log.info("Удалён юзер: id=%s", uid)
            await message.answer(f"Юзер с id {uid} удалён.")
        else:
            log.warning("Юзер с id=%s не найден в базе", uid)
            await message.answer(f"Юзера с id {uid} в базе нет.")
    except ValueError:
        await message.answer("Введите одно число — id пользователя.")
    except Exception as e:
        log.exception("Ошибка удаления юзера id=%s: %s",
                      message.text.strip(), e)
        await message.answer("Не удалось удалить. Попробуйте позже.")


@router.message(F.text == "Текст сообщения")
async def message_text_menu(message: Message) -> None:
    _user_input_state.pop(message.from_user.id, None)
    _message_input_state.pop(message.from_user.id, None)
    text = get_message_text()
    if text:
        await message.answer(
            "<b>Текст для рассылки</b>\n\n" + text,
            reply_markup=message_edit_kb(),
            parse_mode="HTML",
        )
        return
    _message_input_state[message.from_user.id] = "create"
    prompt = await message.answer(
        "<b>Текст для рассылки</b>\n\n"
        "Введите текст сообщения.",
        parse_mode="HTML",
    )
    _message_prompt_id[message.from_user.id] = prompt.message_id


@router.callback_query(F.data == "message_edit")
async def message_edit(callback: CallbackQuery) -> None:
    try:
        await callback.message.delete()
    except Exception:
        pass
    _message_input_state[callback.from_user.id] = "edit"
    prompt = await callback.message.answer("Отправьте новый текст сообщения.")
    _message_prompt_id[callback.from_user.id] = prompt.message_id
    await callback.answer()


@router.message(F.text, lambda message: _message_input_state.get(message.from_user.id) in {"create", "edit"})
async def message_text_input(message: Message) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Текст не должен быть пустым. Попробуйте ещё раз.")
        return
    try:
        await message.delete()
    except Exception:
        pass
    prompt_id = _message_prompt_id.pop(message.from_user.id, None)
    if prompt_id:
        try:
            await message.bot.delete_message(message.chat.id, prompt_id)
        except Exception:
            pass
    _pending_message_text[message.from_user.id] = text
    _message_input_state.pop(message.from_user.id, None)
    await message.answer(text, reply_markup=message_save_kb())


@router.callback_query(F.data == "message_save")
async def message_save(callback: CallbackQuery) -> None:
    text = _pending_message_text.pop(callback.from_user.id, None)
    if not text:
        await callback.message.answer("Нет текста для сохранения. Нажмите «Текст сообщения».")
        await callback.answer()
        return
    try:
        set_message_text(text)
    except Exception as e:
        log.exception("Ошибка сохранения текста сообщения: %s", e)
        await callback.message.answer("Не удалось сохранить текст. Попробуйте позже.")
        await callback.answer()
        return
    log.info("Текст сообщения сохранён. user_id=%s", callback.from_user.id)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        "<b>Текст для рассылки</b>\n\n" + text,
        reply_markup=message_edit_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(F.text == "Рассылка")
async def broadcast_menu(message: Message) -> None:
    _user_input_state.pop(message.from_user.id, None)
    _message_input_state.pop(message.from_user.id, None)
    text = get_message_text()
    if not text:
        await message.answer("Сначала задайте текст рассылки в «Текст сообщения».")
        return
    try:
        users = get_all_users()
    except Exception as e:
        log.exception("Ошибка получения списка юзеров: %s", e)
        await message.answer("Не удалось получить список юзеров. Попробуйте позже.")
        return
    count = len(users)
    await message.answer(
        "<b>Начать рассылку</b>\n\n"
        f"Юзеров в базе: {count}\n\n"
        f"{text}",
        reply_markup=broadcast_start_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "broadcast_start")
async def broadcast_start(callback: CallbackQuery) -> None:
    text = get_message_text()
    if not text:
        await callback.message.answer("Сначала задайте текст рассылки в «Текст сообщения».")
        await callback.answer()
        return
    try:
        await callback.message.edit_text(
            "<b>Рассылка началась</b>",
            parse_mode="HTML",
        )
    except Exception:
        pass
    try:
        users = get_all_users()
    except Exception as e:
        log.exception("Ошибка получения списка юзеров: %s", e)
        await callback.message.answer("Не удалось получить список юзеров. Попробуйте позже.")
        await callback.answer()
        return
    recipients = [(uid, uname) for uid, uname in users if uname]
    log.info("Рассылка началась. Всего юзеров: %s", len(recipients))
    try:
        success, failed, failed_recipients = await _send_broadcast(text, recipients)
        log.info("Рассылка завершена. Успешно: %s, Ошибок: %s", success, failed)
    except Exception as e:
        log.exception("Критическая ошибка рассылки: %s", e)
        await callback.message.edit_text(
            "<b>Ошибка рассылки</b>",
            parse_mode="HTML",
        )
        await callback.answer()
        return
    if failed_recipients:
        log.warning("Не удалось отправить: %s", ", ".join(failed_recipients))
        await callback.message.answer(
            "Не удалось отправить следующим пользователям:\n"
            + "\n".join(failed_recipients)
        )
    try:
        await callback.message.edit_text(
            "<b>Рассылка закончилась</b>",
            parse_mode="HTML",
        )
    except Exception:
        pass
    log.info("Рассылка закончилась. Всего юзеров: %s", len(users))
    await callback.answer()


@router.message(F.text == "Профиль")
async def profile(message: Message) -> None:
    _user_input_state.pop(message.from_user.id, None)
    await message.answer("Раздел профиля. Тут будет ваша логика.")


@router.message(F.text == "Помощь")
async def help_message(message: Message) -> None:
    _user_input_state.pop(message.from_user.id, None)
    await message.answer("Напишите, что нужно сделать, и бот ответит.")


@router.callback_query(F.data == "open_menu")
async def open_menu(callback: CallbackQuery) -> None:
    await callback.message.answer("Открываю меню:", reply_markup=main_inline_kb())
    await callback.answer()
