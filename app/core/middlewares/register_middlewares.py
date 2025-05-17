import time
import uuid
from typing import Awaitable, Callable

import orjson
from fastapi import FastAPI, Request, Response
from starlette.responses import StreamingResponse

from .logs import logger


def register_middlewares(app: FastAPI) -> None:
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

    # noinspection PyUnusedLocal
    @app.middleware("http")
    async def log_incoming_request(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:

        # Генерация uid для различения запросов
        chain_uuid: uuid.UUID = uuid.uuid4()

        # Подменяем _receive, чтобы downstream (router) тоже получил тело
        async def receive() -> dict:
            return {"type": "http.request", "body": body}

        body = await request.body()
        request._receive = receive  # "Восстанавливаем" тело запроса

        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                parsed_body = orjson.loads(body)
            except Exception:
                parsed_body = "<invalid json>"
        elif "multipart/form-data" in content_type:
            parsed_body = "<multipart/form-data>"
        else:
            parsed_body = body.decode("utf-8", errors="replace")

        logger.info(
            "[%s] Request: %s %s, Headers: %s, Body: %s, Query: %s",
            str(chain_uuid),
            request.method,
            request.url.path,
            dict(request.headers),
            parsed_body,
            dict(request.query_params),
        )

        # Отправка запроса в downstream (router)
        response: Response | StreamingResponse = await call_next(request)

        # Подмена тела ответа
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        try:
            json_body = orjson.loads(response_body)
            compact_json = orjson.dumps(json_body).decode("utf-8")
            logger.info(
                "[%s] Response [%s in %s sec]: %s",
                str(chain_uuid),
                response.status_code,
                response.headers["X-Process-Time"],
                compact_json,
            )
        except Exception:
            logger.info(
                "Response [%s in %s sec]: <non-JSON body>",
                response.status_code,
                response.headers["X-Process-Time"],
            )
        delimiter: str = "-" * 50
        logger.info(
            "%s End of request chain %s",
            delimiter,
            delimiter,
        )

        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
