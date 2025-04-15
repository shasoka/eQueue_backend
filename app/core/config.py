from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Run(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiPrefix(BaseModel):
    prefix: str = "/api"


class Settings(BaseSettings):
    run: Run = Run()
    api: ApiPrefix = ApiPrefix()


settings = Settings()

__all__ = [
    "settings",
]
