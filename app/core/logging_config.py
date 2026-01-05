import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, level=logging.INFO):
    """
    Configures a logger with both StreamHandler (Console) and RotatingFileHandler.
    """
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    log_dir = "logs"
    try:
        os.makedirs(log_dir, exist_ok=True)
    except OSError as e:
        print(f"Warning: Could not create log directory '{log_dir}'. File logging disabled. Error: {e}")
        file_handler = None
    else:
        file_handler = RotatingFileHandler(
            filename=f"{log_dir}/{name}.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,        
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        logger.addHandler(stream_handler)
        if file_handler:
            logger.addHandler(file_handler)

    return logger


app_logger = setup_logger("app_logger")
error_logger = setup_logger("error_logger", level=logging.ERROR)