from collections.abc import Iterable
from datetime import UTC, datetime

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, select

from ..api.models.fundamentals_models import Instrument, Quote
from .storage import PostgresStore
from .tables import Instrument as InstrumentTable, QuoteSnapshot


def save_instruments(store: PostgresStore, items: Iterable[Instrument]) -> None:
    updated_at = datetime.now(UTC)

    rows = {
        item.symbol: {**item.model_dump(), "size": item.size, "updated_at": updated_at}
        for item in items
    }
    
    if not rows:
        return

    statement = insert(InstrumentTable).values(list(rows.values()))
    statement = statement.on_conflict_do_update(
        index_elements=[InstrumentTable.symbol],
        set_={key: statement.excluded[key] for key in next(iter(rows.values())) if key != "symbol"},
    )

    with Session(store.engine) as session:
        session.execute(statement)
        session.commit()


def instruments_page(
    store: PostgresStore, asset_class: str, offset: int, limit: int,
) -> tuple[list[InstrumentTable], int]:
    with Session(store.engine) as session:
        rows = session.exec(
            select(InstrumentTable)
            .where(InstrumentTable.asset_class == asset_class)
            .order_by(InstrumentTable.size.desc().nullslast(), InstrumentTable.symbol)
            .offset(offset)
            .limit(limit)
        ).all()

        total = session.exec(
            select(func.count()).select_from(InstrumentTable)
            .where(InstrumentTable.asset_class == asset_class)
        ).one()

    return list(rows), total


def latest_quote(store: PostgresStore, symbol: str, since: datetime) -> QuoteSnapshot | None:
    with Session(store.engine) as session:
        return session.exec(
            select(QuoteSnapshot)
            .where(QuoteSnapshot.symbol == symbol, QuoteSnapshot.recorded_at >= since)
            .order_by(QuoteSnapshot.id.desc())
            .limit(1)
        ).first()


def save_quote(store: PostgresStore, record: Quote) -> None:
    with Session(store.engine) as session:
        session.add(QuoteSnapshot(**record.model_dump()))
        session.commit()
