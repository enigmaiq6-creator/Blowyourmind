import os
import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

env_dir = None
if getattr(sys, "frozen", False):
    env_dir = os.path.dirname(sys.executable)
else:
    env_dir = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{env_dir}/.env", env_file_encoding="utf-8", extra="ignore"
    )
    # Google
    GEMINI_API_KEY: str = ""

    # Discord
    DISCORD_EMAIL: str = ""
    DISCORD_PASSWORD: str = ""
    DISCORD_TOKEN: str = ""
    DISCORD_CHAT_URL: str = ""
    DISCORD_MESSAGES_ENDPOINT: str = ""


ENV_SETTINGS = Settings()
