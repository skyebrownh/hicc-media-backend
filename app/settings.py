from functools import lru_cache
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Environment variables
    fast_api_key: str = Field(..., validation_alias=AliasChoices("FAST_API_KEY"))
    railway_database_url: str = Field(..., validation_alias=AliasChoices("RAILWAY_DATABASE_URL"))
    local_test_db_url: str = Field(..., validation_alias=AliasChoices("LOCAL_TEST_DB_URL"))


@lru_cache()
def get_settings() -> Settings:
    # Cache ensures settings are only loaded once and can be reused everywhere
    return Settings()


settings = get_settings()
