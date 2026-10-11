from typing import Annotated

from fastapi import APIRouter, Body, Query

from .models.news_models import Article
from ..service.news_service import (
    related_news as _related_news,
    search_news_by_ticker as _search_news_by_ticker,
    search_news as _search_news,
    search_news_by_keywords as _search_news_by_keywords,
    stored_news as _stored_news,
)
from .validation import TickerSymbol, int_range, list_of, string
from .deps import StoreDep

router = APIRouter()


@router.get(
    "/news",
    summary="Search news articles by query",
    description="Searches news articles.",
)
def search_news_by_query(
    store: StoreDep,
    query: Annotated[string(max_length=500), Query(description="News search query")] = "business",
    limit: Annotated[int_range(), Query(description="Maximum number of articles")] = 25,
) -> list[Article]:
    return _search_news(query, limit=limit, store=store)


@router.get(
    "/news/keywords",
    summary="Search news articles by keywords",
    description="Searches news articles for each keyword.",
)
def search_news_by_keywords(
    store: StoreDep,
    keywords: Annotated[list_of(string(max_length=100), max_length=20), Query(description="News search keywords")],
    limit: Annotated[int_range(), Query(description="Maximum number of articles")] = 25,
) -> list[Article]:
    return _search_news_by_keywords(keywords, limit=limit, store=store)


@router.get(
    "/news/stored",
    summary="Get stored news articles",
    description="Returns persisted articles ordered by publishedAt descending.",
)
def get_stored_news(
    store: StoreDep,
    offset: Annotated[int_range(ge=0, le=None), Query(description="Result offset")] = 0,
    limit: Annotated[int_range(), Query(description="Maximum number of articles")] = 100,
) -> list[Article]:
    return _stored_news(store, offset=offset, limit=limit)


@router.post(
    "/news/related",
    summary="Get related news articles",
    description="Embeds the given text and returns stored articles ordered by semantic similarity. "
)
def get_related_news(
    store: StoreDep,
    text: Annotated[string(max_length=10_000), Body(embed=True, description="Text to find related articles")],
    limit: Annotated[int_range(), Query(description="Maximum number of articles")] = 10,
) -> list[Article]:
    return _related_news(text, store, limit=limit)


@router.get(
    "/tickers/{symbol}/news",
    summary="Get news articles for a ticker",
    description="Returns the latest news articles for a ticker symbol.",
)
def search_news_by_ticker(
    symbol: TickerSymbol,
    store: StoreDep,
    limit: Annotated[int_range(), Query(description="Maximum number of articles")] = 10,
) -> list[Article]:
    return _search_news_by_ticker(symbol.upper(), limit=limit, store=store)
