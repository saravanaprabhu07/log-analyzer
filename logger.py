"""
Logging Configuration
Provides centralized logging setup with both file and console handlers
"""

import logging
import logging.handlers
import os
from pathlib import Path
from config import settings


def setup_logging():
    """Configure logging for the application"""

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.log_level))
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)

    # File Handler (General Log)
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)

    # Error File Handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)

    # Access File Handler (for API access logs)
    access_handler = logging.handlers.RotatingFileHandler(
        log_dir / "access.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(simple_formatter)
    access_logger = logging.getLogger("access")
    access_logger.addHandler(access_handler)
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False

    return root_logger


# Initialize logging on module import
logger = setup_logging()


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module"""
    return logging.getLogger(name)
