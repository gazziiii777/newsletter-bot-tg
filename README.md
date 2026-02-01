# Newsletter Robot TG

Простой Telegram-бот для рассылки сообщений. Поддерживает:
- хранение списка получателей (username/телефоны);
- редактирование текста рассылки;
- запуск рассылки через Telethon от аккаунта;
- логирование ошибок доставки.

## Быстрый старт

1. Скопируйте `.env.example` в `.env` и заполните значения.
2. Создайте Telethon-сессию:
   ```bash
   python srcitp/create_session.py
   ```
3. Запустите бота:
   ```bash
   docker compose up --build
   ```

## Переменные окружения

- `BOT_TOKEN` — токен бота.
- `TELETHON_API_ID` — API ID для Telethon.
- `TELETHON_API_HASH` — API Hash для Telethon.
- `TELETHON_SESSION` — имя файла сессии (по умолчанию `my_session`).
- `ALLOWED_USER_IDS` — список разрешённых user_id через запятую.

## Описание репозитория

Этот репозиторий содержит Telegram-бота для подготовки и запуска рассылок. Внутри есть хранилище пользователей и текста рассылки на SQLite, а также инструменты для авторизации Telethon.
# newsletter-bot-tg
