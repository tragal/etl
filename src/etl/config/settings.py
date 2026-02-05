from typing import Optional
from pathlib import Path

# prefer pydantic-settings (pydantic v2); fall back to pydantic.BaseSettings for older installs,
# and finally to pydantic.BaseModel to avoid import errors in environments without settings package.
try:
    from pydantic_settings import BaseSettings
except Exception:
    try:
        from pydantic import BaseSettings  # type: ignore
    except Exception:
        from pydantic import BaseModel as BaseSettings  # type: ignore


class Settings(BaseSettings):
    database_url: Optional[str] = None
    temp_dir: Path = Path("/data")
    chunk_size: int = 1000
    request_timeout: int = 60

    class Config:
        env_prefix = "ETL_"

    def get_database_url(self) -> str:
        if not self.database_url:
            raise RuntimeError("ETL_DATABASE_URL is not set in the environment")
        return self.database_url


settings = Settings()
