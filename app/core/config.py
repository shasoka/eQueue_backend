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
    alive: str = "/am_i_alive"
    avatar: str = "/upload_avatar"


class ApiGroups(BaseModel):
    prefix: str = "/groups"
    tags: list[str] = ["Groups"]


class ApiWorkspaces(BaseModel):
    prefix: str = "/workspaces"
    tags: list[str] = ["Workspaces"]

    # --- Endpoints ---

    subscribed: str = "/subscribed"


class ApiWorkspaceMembers(BaseModel):
    prefix: str = "/workspace_members"
    tags: list[str] = ["Workspace Members"]

    # --- Endpoints ---

    all: str = "/all"
    leaderboard: str = "/leaderboard"


class ApiSubjects(BaseModel):
    prefix: str = "/subjects"
    tags: list[str] = ["Subjects"]

    # --- Endpoints ---

    from_ecourses: str = "/from_ecourses"
    from_worksapce: str = "/from_workspace"


class ApiTasks(BaseModel):
    prefix: str = "/tasks"
    tags: list[str] = ["Tasks"]

    # --- Endpoints ---

    from_ecourses: str = "/from_ecourses"
    from_subject: str = "/from_subject"
    from_subject_with_submissions: str = "/from_subject_with_submissions"


class ApiSubmissions(BaseModel):
    prefix: str = "/submissions"
    tags: list[str] = ["Submissions"]

    # --- Endpoints ---

    from_task: str = "/from_task"


class ApiQueues(BaseModel):
    prefix: str = "/queues"
    tags: list[str] = ["Queues"]


class ApiQueueMembers(BaseModel):
    prefix: str = "/queue_members"
    tags: list[str] = ["Queue Members"]


class ApiBase(BaseModel):
    prefix: str = "/api"
    tags: list[str] = ["eQueue Api"]

    # --- OAuth2 Login endpoint

    access_token_url: str = "/api/users/moodle_auth"

    # --- Sub-routers ---

    users: ApiUsers = ApiUsers()
    groups: ApiGroups = ApiGroups()
    workspaces: ApiWorkspaces = ApiWorkspaces()
    workspace_members: ApiWorkspaceMembers = ApiWorkspaceMembers()
    subjects: ApiSubjects = ApiSubjects()
    tasks: ApiTasks = ApiTasks()
    submissions: ApiSubmissions = ApiSubmissions()
    queues: ApiQueues = ApiQueues()
    queue_members: ApiQueueMembers = ApiQueueMembers()


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

    upload_file_url: str = (
        "https://e.sfu-kras.ru/webservice/upload.php"
        "?token=%s"
        "&filearea=draft"
    )

    timetable_url: str = "https://edu.sfu-kras.ru/api/timetable/get_insts"

    enrolled_courses_url: str = (
        "https://e.sfu-kras.ru/webservice/rest/server.php"
        "?wstoken=%s"
        "&wsfunction=core_enrol_get_users_courses"
        "&moodlewsrestformat=json"
        "&userid=%s"
    )

    course_url: str = "https://e.sfu-kras.ru/course/view.php?id=%s"

    course_structure_url: str = (
        "https://e.sfu-kras.ru/webservice/rest/server.php"
        "?wstoken=%s"
        "&wsfunction=core_course_get_contents"
        "&moodlewsrestformat=json"
        "&courseid=%s"
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


# noinspection PyArgumentList
settings: Settings = Settings()
