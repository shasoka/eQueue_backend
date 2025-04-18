from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import router as api_router
from core.exceptions.exceptions_handlers import register_exceptions_handlers
from core.models import db_helper


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[Any, Any]:
    # На __aenter__ ничего не происходит
    # После __aenter__ yield
    yield
    # На __aexit__ dispose
    await db_helper.dispose()


def build_fastapi_app() -> FastAPI:
    app = FastAPI(
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    app.include_router(api_router)

    register_exceptions_handlers(app)

    return app
