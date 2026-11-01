"""Application logging configuration."""

import logging
import logging.config
from pathlib import Path

LOG_FILE = Path("logs") / "backend.log"


def configure_logging() -> None:
    """Configure application and framework logs in the backend log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "backend": {
                    "format": "%(asctime)s %(levelname)s %(name)s: %(message)s",
                },
            },
            "handlers": {
                "backend_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(LOG_FILE.resolve()),
                    "maxBytes": 1_000_000,
                    "backupCount": 5,
                    "encoding": "utf-8",
                    "formatter": "backend",
                },
            },
            "loggers": {
                "fastapi": {"handlers": ["backend_file"], "level": "INFO", "propagate": False},
                "starlette": {"handlers": ["backend_file"], "level": "INFO", "propagate": False},
                "uvicorn": {"handlers": ["backend_file"], "level": "INFO", "propagate": False},
                "sqlalchemy": {"handlers": ["backend_file"], "level": "INFO", "propagate": False},
                "isef01_lernzeit_manager": {
                    "handlers": ["backend_file"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
            "root": {"handlers": ["backend_file"], "level": "WARNING"},
        }
    )
