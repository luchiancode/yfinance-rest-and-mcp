from datetime import UTC, datetime, timedelta

from .models import Article, InstrumentClass, InstrumentPage, Quote
from .db.repository import save_articles, save_instruments, save_quote, stored_articles
from .sources.instrument_source import InstrumentSource
from .sources.quote_source import QuoteSource, TickerNotFoundError
from .sources.search_news_source import SearchNewsSource
from .sources.source import Source
from .sources.ticker_news_source import TickerNewsSource
from .db.storage import PostgresStore

__all__ = [
    "QUOTE_TTL",
    "TickerNotFoundError",
    "get_instruments",
    "get_quote",
    "get_quotes",
    "get_ticker_news",
    "search_news",
    "search_news_by_keywords",
    "stored_news",
]

QUOTE_TTL = timedelta(minutes=2)


def get_instruments(
    asset_class: InstrumentClass, offset: int = 0, limit: int = 250,
    store: PostgresStore | None = None,
) -> InstrumentPage:
    source: Source[InstrumentPage] = InstrumentSource(asset_class, offset, limit, store)
    page = source.get_from_db()
    
    if page is not None:
        return page
        
    page = source.get_from_yfinance()
    if store is not None:
        save_instruments(store, page.items)
    return page


def get_quote(
    symbol: str, store: PostgresStore | None = None,
) -> Quote:
    now = datetime.now(UTC)
    source: Source[Quote] = QuoteSource(symbol, store, since=now - QUOTE_TTL)
    result = source.get_from_db()

    if result is not None:
        return result

    result = source.get_from_yfinance()

    if store is not None:
        save_quote(store, result)

    return result


def get_quotes(
    symbols: list[str], store: PostgresStore | None = None,
) -> dict[str, Quote]:
    return {symbol: get_quote(symbol, store) for symbol in symbols}


def get_ticker_news(
    symbol: str, limit: int = 10,
    store: PostgresStore | None = None,
) -> list[Article]:
    articles = TickerNewsSource(symbol, limit).get_from_yfinance()

    if store is not None:
        save_articles(store, articles)
    return articles


def search_news(
    query: str, limit: int = 8,
    store: PostgresStore | None = None,
) -> list[Article]:
    articles = SearchNewsSource(query, limit).get_from_yfinance()

    if store is not None:
        save_articles(store, articles)

    return articles


def search_news_by_keywords(
    keywords: list[str], limit: int = 25,
    store: PostgresStore | None = None,
) -> list[Article]:
    articles: list[Article] = []
    seen: set[str] = set()

    for keyword in keywords:
        for article in search_news(keyword, limit=limit, store=store):
            key = article.external_id or article.url or article.title
            if key is not None and key not in seen:
                seen.add(key)
                articles.append(article)
                
    return articles[:limit]


def stored_news(
    store: PostgresStore | None, offset: int = 0, limit: int = 100,
) -> list[Article]:
    if store is None:
        return []
    return [
        Article(**row.model_dump()) for row in stored_articles(store, offset, limit)
    ]
