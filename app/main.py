import uvicorn
from fastapi import FastAPI

from build import build_fastapi_app
from core.config import settings

app: FastAPI = build_fastapi_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
