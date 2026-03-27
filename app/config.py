import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    xe_username: str
    xe_password: str
    xe_base_url: str

    app_host: str
    app_port: int
    public_base_url: str

    image_ttl_seconds: int
    image_max_items: int


def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    xe_username = os.getenv("XE_USERNAME", "").strip()
    xe_password = os.getenv("XE_PASSWORD", "").strip()

    xe_base_url = os.getenv(
        "XE_BASE_URL",
        "https://www.xe.com/api/protected/live-currency-pairs-rates/",
    ).strip()

    app_host = os.getenv("APP_HOST", "0.0.0.0").strip()
    app_port = int(os.getenv("APP_PORT", "8080"))

    public_base_url = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")

    image_ttl_seconds = int(os.getenv("IMAGE_TTL_SECONDS", "1800"))
    image_max_items = int(os.getenv("IMAGE_MAX_ITEMS", "500"))

    # --- валидация ---
    if not bot_token:
        raise ValueError("BOT_TOKEN не найден в .env")

    if not xe_username:
        raise ValueError("XE_USERNAME не найден в .env")

    if not xe_password:
        raise ValueError("XE_PASSWORD не найден в .env")

    if not public_base_url:
        raise ValueError("PUBLIC_BASE_URL не найден в .env (нужен для inline картинок)")

    if public_base_url.startswith("http://localhost") or public_base_url.startswith("http://127.0.0.1"):
        raise ValueError("PUBLIC_BASE_URL должен быть публичным (не localhost)")

    return Settings(
        bot_token=bot_token,
        xe_username=xe_username,
        xe_password=xe_password,
        xe_base_url=xe_base_url,

        app_host=app_host,
        app_port=app_port,
        public_base_url=public_base_url,

        image_ttl_seconds=image_ttl_seconds,
        image_max_items=image_max_items,
    )