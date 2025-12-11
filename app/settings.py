from pydantic import BaseSettings, Field
from functools import lru_cache

class Settings(BaseSettings):
    # Environment variables
    fast_api_key: str = Field(..., env="FAST_API_KEY")
    railway_database_url: str = Field(..., env="RAILWAY_DATABASE_URL")
    local_test_db_url: str = Field(..., env="LOCAL_TEST_DB_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    # Cache ensures settings are only loaded once and can be reused everywhere
    return Settings()

settings = get_settings()