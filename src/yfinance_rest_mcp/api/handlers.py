import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from yfinance.exceptions import YFRateLimitError

logger = logging.getLogger(__name__)


def rate_limit_handler(_request: Request, _exc: YFRateLimitError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": "Upstream rate limit reached. Try again later."})


def persistence_error_handler(_request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("Persistence failed: %s", exc)
    return JSONResponse(status_code=503, content={"detail": "Unable to persist data in PostgreSQL."})


def upstream_error_handler(_request: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": "Unable to fetch data."})
