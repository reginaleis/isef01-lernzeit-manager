import json
import logging
import logging.config
import os
import sys


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }

        # If 'extra' was passed to the logger, include it
        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)

        # Include traceback if an exception occurred
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


def configure_logging() -> None:
    # Allow toggling via Railway Variables (default to INFO)
    log_level = os.getenv("LOG_LEVEL", "INFO")

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {"()": JsonFormatter},
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                    "formatter": "json",
                },
            },
            "loggers": {
                # Keep framework logs quiet unless debugging
                "fastapi": {"level": "WARNING"},
                "uvicorn": {"level": "WARNING"},
                "sqlalchemy": {"level": "WARNING"},
                # Your app logs
                "isef01_lernzeit_manager": {"level": log_level},
            },
            "root": {"handlers": ["console"], "level": "WARNING"},
        }
    )
