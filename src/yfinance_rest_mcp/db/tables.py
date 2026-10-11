from datetime import UTC, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

EMBEDDING_DIMENSIONS = 768


class Instrument(SQLModel, table=True):
    __tablename__ = "instruments"

    symbol: str = Field(primary_key=True)
    name: str | None = None
    asset_class: str
    aliases: list[str] = Field(default_factory=list, sa_type=JSONB)
    exchange: str | None = None
    currency: str | None = None
    size: float | None = None
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), sa_type=DateTime(timezone=True),
    )


class QuoteSnapshot(SQLModel, table=True):
    __tablename__ = "quote_snapshots"

    id: int | None = Field(default=None, primary_key=True)
    symbol: str = Field(index=True)
    name: str | None = None
    exchange: str | None = None
    currency: str | None = None
    regular_market_price: float | None = None
    regular_market_time: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    regular_market_change: float | None = None
    regular_market_change_percent: float | None = None
    regular_market_volume: int | None = None
    regular_market_day_low: float | None = None
    regular_market_day_high: float | None = None
    regular_market_open: float | None = None
    regular_market_previous_close: float | None = None
    fifty_two_week_low: float | None = None
    fifty_two_week_high: float | None = None
    fifty_day_average: float | None = None
    two_hundred_day_average: float | None = None
    market_cap: int | None = None
    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), sa_type=DateTime(timezone=True),
    )


class NewsArticle(SQLModel, table=True):
    __tablename__ = "news_articles"
    __table_args__ = (
        Index(
            "idx_news_articles_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    external_id: str = Field(primary_key=True)
    title: str | None = None
    description: str | None = None
    url: str | None = None
    image: str | None = None
    published_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    source: str | None = None
    embedding: list[float] | None = Field(default=None, sa_column=Column(Vector(EMBEDDING_DIMENSIONS)))
    embedding_model: str | None = None
    fetched_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), sa_type=DateTime(timezone=True),
    )
