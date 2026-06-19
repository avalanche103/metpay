from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MetPay"
    database_url: str = "sqlite:///./metpay.db"

    artpay_api_mode: Literal["stub", "v2_store", "v3_epos"] = "stub"
    artpay_store_id: str = ""
    artpay_secret: str = "dev-secret"
    artpay_signature_key_index: str = "1"
    artpay_test: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
