import os
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
    database_url: str
    temp_dir: Path
    chunk_size: int
    request_timeout: Optional[int] = None

    class Config:
        env_prefix = "ETL_"

    @classmethod
    def from_env(cls) -> "Settings":
        prefix = cls.Config.env_prefix if hasattr(cls.Config, "env_prefix") else ""

        def key(name: str) -> str:
            return f"{prefix}{name}"

        db = os.environ.get(key("DATABASE_URL"))
        if not db:
            raise RuntimeError("ETL_DATABASE_URL is not set in the environment")

        temp = os.environ.get(key("TEMP_DIR"))
        temp_dir = Path(temp) if temp else cls.temp_dir

        chunk = os.environ.get(key("CHUNK_SIZE"))
        chunk_size = int(chunk) if chunk is not None else cls.chunk_size

        timeout = os.environ.get(key("REQUEST_TIMEOUT")) or 30
        request_timeout = int(timeout) if timeout is not None else cls.request_timeout

        return cls(
            database_url=db,
            temp_dir=temp_dir,
            chunk_size=chunk_size,
            request_timeout=request_timeout,
        )


settings = Settings.from_env()
