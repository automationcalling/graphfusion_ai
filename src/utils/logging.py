from __future__ import annotations

import logging
import os

_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
_FORMATTER = logging.Formatter(
    "%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def _configure_root() -> None:
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(_FORMATTER)
        root.addHandler(handler)
    root.setLevel(getattr(logging, _LOG_LEVEL, logging.INFO))

    # Ensure uvicorn loggers use the same formatter so all output is consistent
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers = []
        uv_logger.propagate = True

    # Reduce log noise from very chatty dependencies unless explicitly debugging.
    # This keeps demo output readable during ingestion (PDFs with many images).
    if root.level > logging.DEBUG:
        for name in (
            "httpx",
            "httpcore",
            "openai",
            "urllib3",
        ):
            logging.getLogger(name).setLevel(logging.WARNING)

        # Healthchecks hit /health frequently under Docker; keep access logs quiet.
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


_configure_root()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
