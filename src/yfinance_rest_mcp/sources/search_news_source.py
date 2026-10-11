import yfinance as yf

from ..api.models.news_models import Article
from .mappers.article_mapper import ArticleMapper
from .source import Source


class SearchNewsSource(ArticleMapper, Source[list[Article]]):
    def __init__(self, query: str, limit: int = 8) -> None:
        self.query = query
        self.limit = limit

    def get_from_yfinance(self) -> list[Article]:
        return self.map_all(yf.Search(self.query, news_count=self.limit).news or [])

    def get_from_db(self) -> list[Article] | None:
        return None
