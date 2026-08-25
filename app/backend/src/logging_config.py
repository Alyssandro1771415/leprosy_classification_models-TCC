import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

MAX_LOG_BYTES = 10 * 1024 * 1024
BACKUP_COUNT = 5


class _UtcFormatter(logging.Formatter):
    converter = time.gmtime


def _formatter() -> logging.Formatter:
    return _UtcFormatter(
        fmt="%(asctime)sZ level=%(levelname)s logger=%(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def _file_handler(path: Path, level: int) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        path,
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(_formatter())
    return handler


def _stream_handler(stream, level: int) -> logging.StreamHandler:
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    handler.setFormatter(_formatter())
    return handler


def _replace_handlers(logger: logging.Logger, handlers: list[logging.Handler]) -> None:
    for handler in logger.handlers:
        handler.close()
    logger.handlers.clear()
    for handler in handlers:
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def configure_logging() -> Path:
    """Configura logs rotativos sem registrar corpos, tokens ou imagens."""
    log_dir = Path(os.getenv("LOG_DIR", "logs")).resolve()
    log_dir.mkdir(parents=True, exist_ok=True)

    _replace_handlers(
        logging.getLogger("leprosy.application"),
        [
            _file_handler(log_dir / "application.log", logging.INFO),
            _stream_handler(sys.stdout, logging.INFO),
        ],
    )
    _replace_handlers(
        logging.getLogger("leprosy.exceptions"),
        [
            _file_handler(log_dir / "exceptions.log", logging.ERROR),
            _stream_handler(sys.stderr, logging.ERROR),
        ],
    )
    _replace_handlers(
        logging.getLogger("leprosy.access"),
        [_file_handler(log_dir / "access.log", logging.INFO)],
    )

    return log_dir
