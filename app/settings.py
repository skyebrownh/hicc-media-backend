from functools import lru_cache
from pydantic import Field, AliasChoices, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Environment variables
    fast_api_key: str = Field(..., validation_alias=AliasChoices("FAST_API_KEY"))
    database_url: str = Field(..., validation_alias=AliasChoices("DATABASE_URL"))
    local_test_db_url: str = Field(..., validation_alias=AliasChoices("LOCAL_TEST_DB_URL"))
    cors_allowed_origins: str | None = Field(
        default=None,
        validation_alias=AliasChoices("CORS_ALLOWED_ORIGINS")
    )
    env: str = Field(..., validation_alias=AliasChoices("ENV"))
    log_level: str = Field(..., validation_alias=AliasChoices("LOG_LEVEL"))
    clerk_jwks_url: str = Field(..., validation_alias=AliasChoices("CLERK_JWKS_URL"))
    clerk_issuer_url: str = Field(..., validation_alias=AliasChoices("CLERK_ISSUER_URL"))
    clerk_audience: str = Field(..., validation_alias=AliasChoices("CLERK_AUDIENCE"))

    @computed_field
    @property
    def cors_allowed_origins_list(self) -> list[str]:
        if self.cors_allowed_origins is None or not self.cors_allowed_origins.strip():
            return []
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

@lru_cache()
def get_settings() -> Settings:
    # Cache ensures settings are only loaded once and can be reused everywhere
    return Settings()

settings = get_settings()