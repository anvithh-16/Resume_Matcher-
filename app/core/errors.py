import logging
import time
import uuid
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app")

class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(message)
        self.status_code, self.code, self.message = status_code, code, message

def error_body(request: Request, code: str, message: str) -> dict:
    rid = getattr(request.state, "request_id", "-")
    return {"error": {"code": code, "message": message, "request_id": rid}}

def register_error_handlers(app):
    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request.state.request_id = uuid.uuid4().hex[:12]
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:  # last line of defence: no stack trace to client or log
            logger.error("unhandled_error request_id=%s path=%s type=%s",
                         request.state.request_id, request.url.path, type(exc).__name__)
            response = JSONResponse(status_code=500, content=error_body(
                request, "internal_error", "Something went wrong. Quote the request ID if you report this."))
        response.headers["X-Request-ID"] = request.state.request_id
        logger.info("request method=%s path=%s status=%s ms=%.0f request_id=%s", request.method,
                    request.url.path, response.status_code, (time.perf_counter() - start) * 1000,
                    request.state.request_id)
        return response

    @app.exception_handler(AppError)
    async def app_error(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content=error_body(request, exc.code, exc.message))

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        return JSONResponse(status_code=exc.status_code, content=error_body(request, "http_error", str(exc.detail)))

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        fields = sorted({".".join(str(p) for p in e["loc"][1:]) or "body" for e in exc.errors()})
        return JSONResponse(status_code=422, content=error_body(
            request, "validation_error", "Please check these fields: " + ", ".join(fields)))
