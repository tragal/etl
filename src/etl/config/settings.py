# etl/config/settings.py
import yaml
import os
from typing import Optional, Dict, Any
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


class Settings2:
    """Load configuration from multiple sources"""

    def __init__(self):
        self.config_path = Path(__file__).parent / "databases.yaml"
        self._load_yaml()
        self._load_secrets()

    def _load_yaml(self):
        """Load non-secret config from YAML"""
        with open(self.config_path) as f:
            content = f.read()

            # Replace ${VAR} with environment variables
            for key, value in os.environ.items():
                content = content.replace(f"${{{key}}}", value)

            self.config = yaml.safe_load(content)

    def _load_secrets(self):
        """Load secrets from CyberArk/Vault or environment"""

        # Option 1: CyberArk
        if os.getenv("USE_CYBERARK") == "true":
            self.secrets = self._load_from_cyberark()

        # Option 2: HashiCorp Vault
        elif os.getenv("USE_VAULT") == "true":
            self.secrets = self._load_from_vault()

        # Option 3: Environment variables (dev/testing)
        else:
            self.secrets = self._load_from_env()

    def _load_from_cyberark(self) -> Dict[str, str]:
        """Load secrets from CyberArk"""
        try:
            from cyberark import CyberArkPasswordVault

            vault = CyberArkPasswordVault(
                api_url=os.getenv("CYBERARK_URL"), app_id=os.getenv("CYBERARK_APP_ID")
            )

            return {
                "DB_PRIMARY_PASSWORD": vault.get_password("db_primary"),
                "DB_SALES_PASSWORD": vault.get_password("db_sales"),
                "DB_ANALYTICS_PASSWORD": vault.get_password("db_analytics"),
                "DB_LEGACY_PASSWORD": vault.get_password("db_legacy"),
            }
        except Exception as e:
            raise Exception(f"Failed to load from CyberArk: {e}")

    def _load_from_vault(self) -> Dict[str, str]:
        """Load secrets from HashiCorp Vault"""
        try:
            import hvac

            client = hvac.Client(
                url=os.getenv("VAULT_ADDR"), token=os.getenv("VAULT_TOKEN")
            )

            secret = client.secrets.kv.v2.read_secret_version(
                path="database/credentials"
            )

            return secret["data"]["data"]
        except Exception as e:
            raise Exception(f"Failed to load from Vault: {e}")

    def _load_from_env(self) -> Dict[str, str]:
        """Load secrets from environment (fallback for dev)"""
        return {
            "DB_PRIMARY_PASSWORD": os.getenv("DB_PRIMARY_PASSWORD"),
            "DB_SALES_PASSWORD": os.getenv("DB_SALES_PASSWORD"),
            "DB_ANALYTICS_PASSWORD": os.getenv("DB_ANALYTICS_PASSWORD"),
            "DB_LEGACY_PASSWORD": os.getenv("DB_LEGACY_PASSWORD"),
        }

    def get_database_url(self, db_name: str) -> str:
        """Build database URL with secrets"""
        db_config = self.config["databases"][db_name]
        password = self.secrets.get(f"DB_{db_name.upper()}_PASSWORD")

        if not password:
            raise ValueError(f"Password for {db_name} not found!")

        # Build connection string
        if "mysql" in db_name.lower():
            driver = "mysql+pymysql"
        else:
            driver = "postgresql+psycopg2"

        return (
            f"{driver}://{db_config['username']}:{password}"
            f"@{db_config['host']}:{db_config['port']}"
            f"/{db_config['database']}"
        )


# Singleton instance
settings = Settings.from_env()
settings2 = Settings2()
