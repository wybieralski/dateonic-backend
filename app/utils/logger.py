# backend/app/utils/logger.py
import logging
import sys
from pathlib import Path
from datetime import datetime
from functools import wraps
import traceback
from fastapi import HTTPException
import json


class CustomFormatter(logging.Formatter):
    """Custom formatter adding colors to log levels"""

    FORMATS = {
        logging.DEBUG: "\033[0;36m{}\033[0m",  # Cyan
        logging.INFO: "\033[0;32m{}\033[0m",  # Green
        logging.WARNING: "\033[0;33m{}\033[0m",  # Yellow
        logging.ERROR: "\033[0;31m{}\033[0m",  # Red
        logging.CRITICAL: "\033[0;35m{}\033[0m",  # Magenta
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        if log_fmt:
            record.msg = log_fmt.format(record.msg)
        return formatter.format(record)


def setup_logger():
    """Configure and return logger instance"""

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger("dateonic")
    logger.setLevel(logging.DEBUG)

    # Console handler with custom formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)

    # File handlers
    current_date = datetime.now().strftime("%Y-%m-%d")

    # General logs
    file_handler = logging.FileHandler(
        f"logs/dateonic_{current_date}.log",
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    ))
    logger.addHandler(file_handler)

    # Error logs
    error_handler = logging.FileHandler(
        f"logs/errors_{current_date}.log",
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s:\n%(message)s\n"
    ))
    logger.addHandler(error_handler)

    return logger


# Create logger instance
logger = setup_logger()


def log_error(error):
    """Format error details for logging"""
    error_details = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc()
    }
    return json.dumps(error_details, indent=2)


def handle_errors(func):
    """Decorator for handling and logging errors in routes"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as he:
            # Log HTTP exceptions (client errors)
            logger.warning(f"HTTP {he.status_code}: {he.detail}")
            raise he
        except Exception as e:
            # Log unexpected errors
            error_details = log_error(e)
            logger.error(f"Unexpected error:\n{error_details}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error. Check logs for details."
            )

    return wrapper