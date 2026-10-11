from collections.abc import Iterable
from datetime import UTC, datetime

from ...api.models.news_models import Article
from .mapper import Mapper


class ArticleMapper(Mapper[dict, Article]):
    def map(self, item: dict) -> Article | None:
        content = item.get("content") or item

        canonical_url = content.get("canonicalUrl") or {}
        url = canonical_url.get("url") or item.get("link")
        title = content.get("title")

        if title is None and url is None:
            return None

        thumbnail = content.get("thumbnail") or {}
        image = thumbnail.get("originalUrl")
        
        if image is None:
            resolutions = thumbnail.get("resolutions") or []
            if resolutions:
                image = resolutions[-1].get("url")

        timestamp = item.get("providerPublishTime")
        published_at = (
            datetime.fromtimestamp(timestamp, UTC)
            if isinstance(timestamp, int | float) else None
        )

        provider = content.get("provider") or {}

        return Article(
            external_id=content.get("id") or item.get("uuid"),
            title=title,
            description=content.get("summary"),
            url=url,
            image=image,
            published_at=published_at,
            source=provider.get("displayName") or item.get("publisher"),
        )

    def map_all(self, items: Iterable[dict]) -> list[Article]:
        return [article for item in items if (article := self.map(item)) is not None]
