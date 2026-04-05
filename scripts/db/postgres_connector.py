import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import psycopg


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


load_dotenv(ENV_FILE)


@dataclass(frozen=True)
class PostgresConfig:
    host: str
    port: int
    dbname: str
    user: str
    password: str
    sslmode: str = "prefer"

    @classmethod
    def from_env(cls, prefix: str = "POSTGRES_") -> "PostgresConfig":
        return cls(
            host=_get_required_env(f"{prefix}HOST"),
            port=int(os.getenv(f"{prefix}PORT", "5432")),
            dbname=_get_required_env(f"{prefix}DB"),
            user=_get_required_env(f"{prefix}USER"),
            password=_get_required_env(f"{prefix}PASSWORD"),
            sslmode=os.getenv(f"{prefix}SSLMODE", "prefer"),
        )

    def to_connection_kwargs(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "dbname": self.dbname,
            "user": self.user,
            "password": self.password,
            "sslmode": self.sslmode,
        }

    def to_dsn(self, mask_password: bool = True) -> str:
        password = "****" if mask_password else self.password
        return (
            f"host={self.host} "
            f"port={self.port} "
            f"dbname={self.dbname} "
            f"user={self.user} "
            f"password={password} "
            f"sslmode={self.sslmode}"
        )


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(
        f"Environment variable '{name}' is not set. "
        f"Copy '.env.example' to '.env' and fill in your PostgreSQL settings."
    )


def get_postgres_config(prefix: str = "POSTGRES_") -> PostgresConfig:
    return PostgresConfig.from_env(prefix=prefix)


def connect_postgres(prefix: str = "POSTGRES_", **overrides):
    config = get_postgres_config(prefix=prefix)
    kwargs = config.to_connection_kwargs()
    kwargs.update(overrides)
    return psycopg.connect(**kwargs)
