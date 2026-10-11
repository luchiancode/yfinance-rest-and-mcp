from collections.abc import Iterable
from datetime import UTC, datetime

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, select

from ..embedder_adapter.openai_compatible_embedder import OpenAICompatibleEmbedder
from ..api.models.news_models import Article
from .storage import PostgresStore
from .tables import NewsArticle


def save_articles(store: PostgresStore, articles: Iterable[Article]) -> None:
    fetched_at = datetime.now(UTC)

    rows = {
        article.external_id: {
            **article.model_dump(exclude={"content"}),
            "fetched_at": fetched_at,
        }
        for article in articles
        if article.external_id is not None
    }

    if not rows:
        return

    with Session(store.engine) as session:
        existing = set(session.exec(
            select(NewsArticle.external_id).where(NewsArticle.external_id.in_(rows))
        ).all())

    #check existing
    rows = {key: row for key, row in rows.items() if key not in existing}
    if not rows:
        return

    embedder = OpenAICompatibleEmbedder.get()
    vectors = embedder.embed_rows(rows, "title", "description")
    for row, vector in zip(rows.values(), vectors, strict=True):
        if vector is not None:
            row["embedding"] = vector
            row["embedding_model"] = embedder.model

    statement = insert(NewsArticle).values(list(rows.values()))
    statement = statement.on_conflict_do_nothing(index_elements=[NewsArticle.external_id])

    with Session(store.engine) as session:
        session.execute(statement)
        session.commit()


def related_articles(
    store: PostgresStore, embedding: list[float], embedding_model: str, limit: int,
) -> list[NewsArticle]:
    with Session(store.engine) as session:
        session.execute(select(func.set_config("hnsw.ef_search", str(max(limit, 40)), True)))
        distance = NewsArticle.embedding.cosine_distance(embedding)
        return list(session.exec(
            select(NewsArticle)
            .where(
                NewsArticle.embedding.is_not(None),
                NewsArticle.embedding_model == embedding_model,
                distance <= 0.2,
            )
            .order_by(distance)
            .limit(limit)
        ).all())


def stored_articles(store: PostgresStore, offset: int, limit: int) -> list[NewsArticle]:
    with Session(store.engine) as session:
        return list(session.exec(
            select(NewsArticle)
            .order_by(NewsArticle.published_at.desc().nullslast(), NewsArticle.external_id)
            .offset(offset)
            .limit(limit)
        ).all())
