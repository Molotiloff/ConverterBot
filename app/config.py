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
    image_api_base_url: str
    api_token: str


@dataclass(frozen=True)
class ApiSettings:
    xe_username: str
    xe_password: str
    xe_base_url: str

    api_host: str
    api_port: int
    api_token_hash: str
    public_base_url: str

    image_ttl_seconds: int
    image_max_items: int
    api_rate_limit_requests: int
    api_rate_limit_seconds: int


def _get_xe_settings() -> tuple[str, str, str]:
    xe_username = os.getenv("XE_USERNAME", "").strip()
    xe_password = os.getenv("XE_PASSWORD", "").strip()
    xe_base_url = os.getenv(
        "XE_BASE_URL",
        "https://www.xe.com/api/protected/live-currency-pairs-rates/",
    ).strip()

    if not xe_username:
        raise ValueError("XE_USERNAME не найден в .env")

    if not xe_password:
        raise ValueError("XE_PASSWORD не найден в .env")

    return xe_username, xe_password, xe_base_url


def _get_image_settings() -> tuple[int, int]:
    image_ttl_seconds = int(os.getenv("IMAGE_TTL_SECONDS", "1800"))
    image_max_items = int(os.getenv("IMAGE_MAX_ITEMS", "500"))
    return image_ttl_seconds, image_max_items


def _get_rate_limit_settings() -> tuple[int, int]:
    requests_count = int(os.getenv("API_RATE_LIMIT_REQUESTS", "60"))
    seconds = int(os.getenv("API_RATE_LIMIT_SECONDS", "60"))
    return requests_count, seconds


def _validate_public_base_url(public_base_url: str) -> None:
    if not public_base_url:
        raise ValueError("PUBLIC_BASE_URL не найден в .env (нужен для публичных ссылок на картинки)")

    if public_base_url.startswith("http://localhost") or public_base_url.startswith("http://127.0.0.1"):
        raise ValueError("PUBLIC_BASE_URL должен быть публичным (не localhost)")


def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    xe_username, xe_password, xe_base_url = _get_xe_settings()

    app_host = os.getenv("APP_HOST", "0.0.0.0").strip()
    app_port = int(os.getenv("APP_PORT", "8080"))

    public_base_url = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")

    image_ttl_seconds, image_max_items = _get_image_settings()
    image_api_base_url = (
        os.getenv("IMAGE_API_BASE_URL", "").strip().rstrip("/")
        or os.getenv("API_BASE_URL", "").strip().rstrip("/")
    )
    api_token = os.getenv("API_TOKEN", "").strip()

    # --- валидация ---
    if not bot_token:
        raise ValueError("BOT_TOKEN не найден в .env")

    if image_api_base_url and not api_token:
        raise ValueError("API_TOKEN не найден в .env (нужен для IMAGE_API_BASE_URL)")

    _validate_public_base_url(public_base_url)

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
        image_api_base_url=image_api_base_url,
        api_token=api_token,
    )


def get_api_settings() -> ApiSettings:
    xe_username, xe_password, xe_base_url = _get_xe_settings()

    api_host = os.getenv("API_HOST", "127.0.0.1").strip()
    api_port = int(os.getenv("API_PORT", "8090"))
    api_token_hash = os.getenv("API_TOKEN_HASH", "").strip()
    public_base_url = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")

    image_ttl_seconds, image_max_items = _get_image_settings()
    api_rate_limit_requests, api_rate_limit_seconds = _get_rate_limit_settings()

    if not api_token_hash:
        raise ValueError("API_TOKEN_HASH не найден в .env")

    _validate_public_base_url(public_base_url)

    return ApiSettings(
        xe_username=xe_username,
        xe_password=xe_password,
        xe_base_url=xe_base_url,
        api_host=api_host,
        api_port=api_port,
        api_token_hash=api_token_hash,
        public_base_url=public_base_url,
        image_ttl_seconds=image_ttl_seconds,
        image_max_items=image_max_items,
        api_rate_limit_requests=api_rate_limit_requests,
        api_rate_limit_seconds=api_rate_limit_seconds,
    )
