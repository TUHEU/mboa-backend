from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_SECRET_KEY = "replace-this-development-secret-with-32-plus-bytes"


class Settings(BaseSettings):
    app_name: str = "Nyetam Tourism API"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    secret_key: str = DEFAULT_SECRET_KEY
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    google_client_id: str = ""
    google_routes_api_key: str = ""
    database_url: str = "sqlite:///./nyetam.db"
    cors_origins: list[str] = [
        "http://localhost:8123",
        "http://127.0.0.1:8123",
    ]
    # Lets `flutter run -d chrome` work on any random localhost port during
    # development. It is ignored when ENVIRONMENT=production.
    cors_origin_regex: str = r"https?://(localhost|127\.0\.0\.1)(:\d+)?"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_production(self) -> bool:
        return self.environment.strip().lower() == "production"

    @model_validator(mode="after")
    def require_real_secret_in_production(self) -> "Settings":
        if self.is_production and (
            self.secret_key == DEFAULT_SECRET_KEY or len(self.secret_key) < 32
        ):
            raise ValueError(
                "SECRET_KEY must be a unique value of at least 32 characters "
                "when ENVIRONMENT=production."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
