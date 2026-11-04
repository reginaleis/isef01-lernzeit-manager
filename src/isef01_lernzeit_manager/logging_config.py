"""Application logging configuration."""

import logging
import logging.config
import sys


def configure_logging() -> None:
    """Configure application and framework logs on standard output."""
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
                "backend_stream": {
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                    "formatter": "backend",
                },
            },
            "loggers": {
                "fastapi": {"handlers": ["backend_stream"], "level": "INFO", "propagate": False},
                "starlette": {"handlers": ["backend_stream"], "level": "INFO", "propagate": False},
                "uvicorn": {"handlers": ["backend_stream"], "level": "INFO", "propagate": False},
                "sqlalchemy": {"handlers": ["backend_stream"], "level": "INFO", "propagate": False},
                "isef01_lernzeit_manager": {
                    "handlers": ["backend_stream"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
            "root": {"handlers": ["backend_stream"], "level": "WARNING"},
        }
    )
