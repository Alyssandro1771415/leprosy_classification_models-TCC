import logging
import time
import uuid
from contextvars import ContextVar

from robyn import Request, Response

_request_start: ContextVar[float | None] = ContextVar("request_start", default=None)
_request_context: ContextVar[dict[str, str]] = ContextVar("request_context", default={})

access_logger = logging.getLogger("leprosy.access")
exception_logger = logging.getLogger("leprosy.exceptions")


def _safe(value: object, max_length: int = 200) -> str:
    return str(value).replace("\n", " ").replace("\r", " ").replace("\t", " ")[:max_length]


def _path(request: Request) -> str:
    return _safe(getattr(request.url, "path", str(request.url).split("?", 1)[0]))


def start_request_log(request: Request) -> Request:
    _request_start.set(time.perf_counter())
    _request_context.set(
        {
            "request_id": uuid.uuid4().hex,
            "method": _safe(request.method, 16),
            "path": _path(request),
            "ip": _safe(request.ip_addr, 64),
        }
    )
    return request


def finish_request_log(request: Request, response: Response) -> Response:
    start = _request_start.get()
    duration_ms = (time.perf_counter() - start) * 1000 if start is not None else 0.0
    context = _request_context.get()

    access_logger.info(
        "request_id=%s method=%s path=%s status=%s duration_ms=%.2f ip=%s",
        context.get("request_id", "-"),
        context.get("method", _safe(request.method, 16)),
        context.get("path", _path(request)),
        response.status_code,
        duration_ms,
        context.get("ip", _safe(request.ip_addr, 64)),
    )
    return response


def log_exception(error: BaseException, message: str, status_code: int = 500) -> None:
    context = _request_context.get()
    exception_logger.error(
        "%s request_id=%s method=%s path=%s status=%s ip=%s error_type=%s",
        message,
        context.get("request_id", "-"),
        context.get("method", "-"),
        context.get("path", "-"),
        status_code,
        context.get("ip", "-"),
        type(error).__name__,
        exc_info=(type(error), error, error.__traceback__),
    )
