from functools import lru_cache
from pydantic import Field, AliasChoices, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Environment variables
    fast_api_key: str = Field(..., validation_alias=AliasChoices("FAST_API_KEY"))
    railway_db_url: str = Field(..., validation_alias=AliasChoices("RAILWAY_DB_URL"))
    local_test_db_url: str = Field(..., validation_alias=AliasChoices("LOCAL_TEST_DB_URL"))
    cors_allowed_origins: str | None = Field(
        default=None,
        validation_alias=AliasChoices("CORS_ALLOWED_ORIGINS")
    )

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