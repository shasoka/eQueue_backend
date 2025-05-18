"""Модуль, реализующий создание логгера."""

import logging
from pathlib import Path

# Лог-файл в корне проекта
log_file: Path = Path(__file__).parent.parent.parent.parent.parent / "app.log"
log_file.parent.mkdir(parents=True, exist_ok=True)

logger: logging.Logger = logging.getLogger("my_logger")
logger.setLevel(logging.INFO)

formatter: logging.Formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler: logging.FileHandler = logging.FileHandler(
    log_file,
    encoding="utf-8",
)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
