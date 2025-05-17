import time
import orjson
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.types import ASGIApp, Receive, Scope, Send

from core.middlewares.logs import logger


__all__ = ("WebSocketMiddleware",)


class WebSocketMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "websocket":
            start_time = time.perf_counter()
            client = scope.get("client")
            path = scope.get("path")

            logger.info(f"WebSocket connection from {client} to {path}")

            try:
                await self.app(scope, receive, send)
            except WebSocketDisconnect:
                pass
            finally:
                proc_time = time.perf_counter() - start_time
                logger.info(
                    f"WebSocket disconnected from {client} after {proc_time:.5f} sec"
                )
        else:
            await self.app(scope, receive, send)
