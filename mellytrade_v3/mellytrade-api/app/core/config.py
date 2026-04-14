from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    database_url: str = 'sqlite:///./signals.db'
    fastapi_key: str = 'change-me-fastapi-key'
    cf_hub_url: str = 'http://127.0.0.1:8787'
    cf_api_secret: str = 'change-me-cloudflare-secret'
    cooldown_seconds: int = 120
    min_confidence: float = 70.0
    max_risk_percent: float = 1.0

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
