from __future__ import annotations

import sqlite3
from pathlib import Path

from infrastructure.logger import get_logger


# Корень проекта (где main.py), затем data в корне
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "users.db"

log = get_logger(__name__)


def _get_conn() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with _get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL
                )
                """
            )
        log.info("БД: %s", DB_PATH)
    except sqlite3.Error as e:
        log.exception("Ошибка инициализации БД: %s", e)
        raise
