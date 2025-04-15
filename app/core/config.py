from pydantic import BaseModel
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Run(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiPrefix(BaseModel):
    prefix: str = "/api"


class Database(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    max_overflow: int = 50
    pool_size: int = 10


class Settings(BaseSettings):
    run: Run = Run()
    api: ApiPrefix = ApiPrefix()
    db: Database


settings = Settings()

__all__ = [
    "settings",
]
