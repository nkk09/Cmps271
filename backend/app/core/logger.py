import logging
import sys
from pathlib import Path

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"


def setup_logger(level: str = "INFO") -> None:
    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = logging.Formatter(LOG_FORMAT)

    # --- Console handler ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # --- File handler ---
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Avoid duplicate logs on reload
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
