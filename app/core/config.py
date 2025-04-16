from pydantic import BaseModel
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ("settings",)


class Run(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiUsers(BaseModel):
    prefix: str = "/users"
    tags: list[str] = ["Users"]

    # --- Endpoints ---

    login: str = "/moodle_auth"


class ApiBase(BaseModel):
    prefix: str = "/api"
    tags: list[str] = ["eQueue Api"]

    # --- Sub-routers ---

    users: ApiUsers = ApiUsers()


class MoodleAPI(BaseModel):
    ecourses_base_url: str = "https://e.sfu-kras.ru/webservice/rest/server.php"

    auth_url: str = (
        "https://e.sfu-kras.ru/login/token.php"
        "?service=moodle_mobile_app"
        "&username=%s"
        "&password=%s"
    )

    get_user_info_url: str = (
        f"{ecourses_base_url}"
        f"?wstoken=%s"
        f"&wsfunction=core_webservice_get_site_info"
        f"&moodlewsrestformat=json"
    )


class Database(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    max_overflow: int = 50
    pool_size: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        env_file=".env",
    )

    run: Run = Run()
    api: ApiBase = ApiBase()
    moodle: MoodleAPI = MoodleAPI()
    db: Database


settings: Settings = Settings()
