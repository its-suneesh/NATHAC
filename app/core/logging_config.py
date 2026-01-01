import logging
import os
from logging.handlers import RotatingFileHandler

os.makedirs("logs", exist_ok=True)


def setup_logger(name: str, log_file: str, level=logging.INFO):
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    handler = RotatingFileHandler(
        f"logs/{log_file}",
        maxBytes=5 * 1024 * 1024,
        backupCount=2
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


app_logger = setup_logger("app_logger", "app.log")
error_logger = setup_logger("error_logger", "error.log")
