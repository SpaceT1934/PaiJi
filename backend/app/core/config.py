import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


DEFAULT_VISION_MODEL = "doubao-seed-1-6-vision-250815"


def clean_env(value: str | None) -> str:
    return (value or "").strip().strip("`").strip('"').strip("'")


def clean_model(value: str | None) -> str:
    model = clean_env(value)
    if not model or model.startswith("ak-"):
        return DEFAULT_VISION_MODEL
    return model


@dataclass(frozen=True)
class Settings:
    app_name: str = "TripNote Backend"
    api_base_url: str = clean_env(
        os.getenv("ARK_BASE_URL")
        or os.getenv("DEEPSEEK_BASE_URL")
        or "https://ark.cn-beijing.volces.com/api/v3"
    )
    api_key: str = clean_env(os.getenv("ARK_API_KEY") or os.getenv("DEEPSEEK_API_KEY"))
    model: str = clean_model(
        os.getenv("ARK_MODEL") or os.getenv("DEEPSEEK_MODEL") or DEFAULT_VISION_MODEL
    )
    default_vision_model: str = DEFAULT_VISION_MODEL
    upstream_mode: str = clean_env(os.getenv("UPSTREAM_MODE") or "responses")
    mock_ai: bool = clean_env(os.getenv("MOCK_AI")) == "1"
    max_upload_bytes: int = 10 * 1024 * 1024


settings = Settings()
