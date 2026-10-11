from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool
from yfinance.exceptions import YFRateLimitError

from .api.fundamentals_api import router as fundamentals_router
from .api.handlers import persistence_error_handler, rate_limit_handler, upstream_error_handler
from .api.news_api import router as news_router
from .db.storage import create_store


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    store = await run_in_threadpool(create_store)
    app.state.store = store
    try:
        yield
    finally:
        if store is not None:
            await run_in_threadpool(store.close)


app = FastAPI(
    title="yfinance-rest-mcp",
    description="An HTTP API for accessing yfinance data.",
    lifespan=lifespan,
)

app.include_router(fundamentals_router)
app.include_router(news_router)

app.add_exception_handler(YFRateLimitError, rate_limit_handler)
app.add_exception_handler(SQLAlchemyError, persistence_error_handler)
app.add_exception_handler(Exception, upstream_error_handler)


def main() -> None:
    uvicorn.run("yfinance_rest_mcp.app:app", host="127.0.0.1", port=5001)
