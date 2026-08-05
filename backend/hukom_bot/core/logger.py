import logging

from datetime import date
from logging.handlers import RotatingFileHandler

from backend.hukom_bot.util.utility import get_project_root


def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = get_project_root() / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"{date.today()}.log"

    file_handler = RotatingFileHandler(
        filename=log_file, maxBytes=10_000_000, backupCount=5, encoding="utf-8"  # 10 MB
    )

    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    file_handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[file_handler])
