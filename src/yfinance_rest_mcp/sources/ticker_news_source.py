import yfinance as yf

from ..api.models.news import Article
from .mappers.article_mapper import ArticleMapper
from .source import Source


class TickerNewsSource(ArticleMapper, Source[list[Article]]):
    def __init__(self, symbol: str, limit: int = 10) -> None:
        self.symbol = symbol
        self.limit = limit

    def get_from_yfinance(self) -> list[Article]:
        return self.map_all(yf.Ticker(self.symbol).get_news(count=self.limit) or [])

    def get_from_db(self) -> list[Article] | None:
        return None
