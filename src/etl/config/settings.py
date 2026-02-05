from pydantic import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    database_url: str

    temp_dir: Path = Path("/tmp/etl")
    chunk_size: int = 1000
    request_timeout: int = 60

    class Config:
        env_prefix = "ETL_"


settings = Settings()
