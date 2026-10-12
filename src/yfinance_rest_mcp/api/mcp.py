from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Annotated

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool
from yfinance.exceptions import YFRateLimitError

from .models.fundamentals_models import Quote
from .models.news_models import Article
from ..service.fundamentals_service import TickerNotFoundError, get_quotes as _get_quotes
from ..service.news_service import (
    search_news_by_ticker as _search_news_by_ticker,
    search_news as _search_news,
    search_news_by_keywords as _search_news_by_keywords,
)
from ..db.storage import PostgresStore, create_store
from .validation import TickerSymbol, int_range, list_of, string


@dataclass
class MCPState:
    store: PostgresStore | None


@asynccontextmanager
async def lifespan(_server: MCPServer) -> AsyncIterator[MCPState]:
    store = await run_in_threadpool(create_store)
    try:
        yield MCPState(store=store)
    finally:
        if store is not None:
            await run_in_threadpool(store.close)


server = MCPServer("yfinance-rest-mcp", lifespan=lifespan)


def handle_errors[**P, R](tool: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    @wraps(tool)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return await tool(*args, **kwargs)
        except ToolError:
            raise
        except YFRateLimitError as exc:
            raise ToolError("Upstream rate limit reached. Try again later.") from exc
        except SQLAlchemyError as exc:
            raise ToolError("Unable to persist data in PostgreSQL.") from exc
        except Exception as exc:
            raise ToolError("Unable to fetch data.") from exc

    return wrapper


@server.tool(
    description=(
        "Get the latest regular-market quotes for 1–20 ticker symbols. "
        "Returns a symbol-keyed object of quotes with fields: symbol, name, "
        "exchange, currency, marketCap, fiftyDayAverage, twoHundredDayAverage. "
        "day market: price, time, change, changePercent, volume, dayLow, "
        "dayHigh, open, previousClose. "
        "52 week: low, high."
    ),
    structured_output=True,
)
@handle_errors
async def get_quotes(
    symbols: Annotated[list_of(TickerSymbol, max_length=20), Field(description="Ticker symbols")],
    ctx: Context[MCPState, None],
) -> dict[str, Quote]:
    symbol_list = list(dict.fromkeys(symbol.upper() for symbol in symbols))
    store = ctx.request_context.lifespan_context.store
    try:
        return await run_in_threadpool(_get_quotes, symbol_list, store)
    except TickerNotFoundError as exc:
        raise ToolError(f"No data found for ticker {exc}.") from exc


@server.tool(
    description=(
        "Search news articles acrossy. "
        "Returns a list of articles with id, title, "
        "url, image, publishedAt, and source."
    ),
    structured_output=True,
)
@handle_errors
async def search_news(
    ctx: Context[MCPState, None],
    query: Annotated[string(max_length=1000), Field(description="News search query")] = "business",
    limit: Annotated[int_range(), Field(description="Maximum number of articles")] = 25,
) -> list[Article]:
    store = ctx.request_context.lifespan_context.store
    return await run_in_threadpool(_search_news, query, limit=limit, store=store)


@server.tool(
    description=(
        "Searches news articles for each keyword."
        "Returns a list of articles with id, title, "
        "url, image, publishedAt, and source."
    ),
    structured_output=True,
)
@handle_errors
async def search_news_by_keywords(
    ctx: Context[MCPState, None],
    keywords: Annotated[list_of(string(max_length=100), max_length=20), Field(description="News search keywords")],
    limit: Annotated[int_range(), Field(description="Maximum number of articles")] = 25,
) -> list[Article]:
    store = ctx.request_context.lifespan_context.store
    return await run_in_threadpool(_search_news_by_keywords, keywords, limit=limit, store=store)


@server.tool(
    description=(
        "Get the latest news articles for a ticker symbol. "
        "Returns a list of articles with id, title, "
        "url, image, publishedAt, and source."
    ),
    structured_output=True,
)
@handle_errors
async def search_news_by_ticker(
    symbol: TickerSymbol,
    ctx: Context[MCPState, None],
    limit: Annotated[int_range(), Field(description="Maximum number of articles")] = 10,
) -> list[Article]:
    store = ctx.request_context.lifespan_context.store
    return await run_in_threadpool(_search_news_by_ticker, symbol.upper(), limit=limit, store=store)


def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
