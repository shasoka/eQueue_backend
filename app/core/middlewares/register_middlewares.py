import time
from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response

from .logs import logger


def register_middlewares(app: FastAPI) -> None:

    # noinspection PyUnusedLocal
    @app.middleware("http")
    async def log_incoming_request(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        logger.info(
            "Incoming request: %s %s",
            request.method,
            request.url.path,
        )
        return await call_next(request)

    # noinspection PyUnusedLocal
    @app.middleware("http")
    async def add_proc_time_header(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start_time: float = time.perf_counter()
        response: Response = await call_next(request)
        proc_time: float = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{proc_time:.5f}"
        return response
