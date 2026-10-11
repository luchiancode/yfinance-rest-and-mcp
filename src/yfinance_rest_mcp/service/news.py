from ..api.models.news import Article
from ..db.news_repository import related_articles, save_articles, stored_articles
from ..db.storage import PostgresStore
from ..embedder_adapter.openai_compatible_embedder import OpenAICompatibleEmbedder
from ..sources.search_news_source import SearchNewsSource
from ..sources.ticker_news_source import TickerNewsSource

__all__ = [
    "related_news",
    "search_news_by_ticker",
    "search_news",
    "search_news_by_keywords",
    "stored_news",
]

def search_news(
    query: str, limit: int = 8,
    store: PostgresStore | None = None,
) -> list[Article]:
    articles = SearchNewsSource(query, limit).get_from_yfinance()

    if store is not None:
        save_articles(store, articles)

    return articles


def search_news_by_ticker(
    symbol: str, limit: int = 10,
    store: PostgresStore | None = None,
) -> list[Article]:
    articles = TickerNewsSource(symbol, limit).get_from_yfinance()

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


def related_news(
    text: str, store: PostgresStore | None, limit: int = 10,
) -> list[Article]:
    embedder = OpenAICompatibleEmbedder.get()
    if store is None or not embedder.enabled:
        return []

    [embedding] = embedder.embed([text])
    return [
        Article(**row.model_dump())
        for row in related_articles(store, embedding, embedder.model, limit)
    ]
