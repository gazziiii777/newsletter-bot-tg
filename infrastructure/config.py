from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8")

    BOT_TOKEN: str
    TELETHON_API_ID: int
    TELETHON_API_HASH: str
    TELETHON_SESSION: str = "my_session"
    ALLOWED_USER_IDS: str  # "528798616,585296404"

    @property
    def allowed_user_ids(self) -> set[int]:
        parts = [p.strip()
                 for p in self.ALLOWED_USER_IDS.split(",") if p.strip()]
        return {int(p) for p in parts}


settings = Settings()
