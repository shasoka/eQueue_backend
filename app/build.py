"""Модуль, содержащий функцию для создания FastAPI-приложения."""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from fastapi.templating import Jinja2Templates

from api import router as api_router
from core.exceptions import register_exceptions_handlers
from core.middlewares import register_middlewares
from core.models import db_helper


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[Any, Any]:
    """
    Функция, которая закрывает сессию подключения к БД при завершении работы.
    """

    # На __aenter__ ничего не происходит
    # После __aenter__ yield
    yield
    # На __aexit__ dispose
    await db_helper.dispose()


def build_fastapi_app() -> FastAPI:
    """
    Функция, собирающая приложение.

    Здесь к объекту FastAPI подключаются роутеры, обработчики исключений,
    миддлвары и биндятся шаблоны.

    :return: собранное FastAPI-приложение
    """

    app = FastAPI(
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        title="eQueue API",
        summary="Шенберг Аркадий Алексеевич пытается в backend...",
        description="Серверная часть **eQueue**. Добро пожаловать 🤝"
        "\n\n[GitHub➚](https://github.com/shasoka/eQueue_backend)",
        version="1.0.0",
        swagger_ui_parameters={
            "syntaxHighlight": {
                "theme": "obsidian",
            }
        },
        redoc_url=None,
    )

    app.include_router(api_router)

    register_exceptions_handlers(app)

    register_middlewares(app)

    # Подключение шаблона для тестирования websocket
    templates = Jinja2Templates(directory="templates")

    @app.get("/", include_in_schema=False)
    def get(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="ws_test_client.html",
        )

    return app
