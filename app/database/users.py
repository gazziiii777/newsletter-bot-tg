from __future__ import annotations

from app.database.connection import _get_conn


def store_user(username: str) -> int:
    """Добавляет юзера по username. Возвращает новый id."""
    with _get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users (username) VALUES (?)",
            (username.strip(),),
        )
        conn.commit()
        return cur.lastrowid


def get_all_users() -> list[tuple[int, str | None]]:
    with _get_conn() as conn:
        cur = conn.execute("SELECT id, username FROM users ORDER BY id")
        return cur.fetchall()


def delete_user(user_id: int) -> bool:
    with _get_conn() as conn:
        cur = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return cur.rowcount > 0
