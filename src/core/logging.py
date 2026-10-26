import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.core.config import settings


def configure_logging() -> None:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    file_handler = RotatingFileHandler(log_dir / "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return
    root_logger.setLevel(settings.log_level.upper())
    root_logger.addHandler(console)
    root_logger.addHandler(file_handler)
