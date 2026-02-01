from __future__ import annotations

from app.database.connection import _get_conn


def get_message_text() -> str | None:
    with _get_conn() as conn:
        cur = conn.execute("SELECT text FROM message WHERE id = 1")
        row = cur.fetchone()
        return row[0] if row else None


def set_message_text(text: str) -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO message (id, text)
            VALUES (1, ?)
            ON CONFLICT(id) DO UPDATE SET text = excluded.text
            """,
            (text,),
        )
        conn.commit()
