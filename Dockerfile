FROM python:3.12.4

WORKDIR /backend

COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade pip && \
    pip install poetry==2.1.3

RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

COPY . .

WORKDIR /backend/appwork

CMD ["gunicorn", "main:app", "--workers", "3", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000", "--access-logfile", "-"]
