from datetime import UTC, datetime, timedelta

from ..api.models.fundamentals import InstrumentClass, InstrumentPage, Quote, Ratios
from ..db.fundamentals_repository import save_instruments, save_quote
from ..db.storage import PostgresStore
from ..sources.instrument_source import InstrumentSource
from ..sources.quote_source import QuoteSource, TickerNotFoundError
from ..sources.ratios_source import RatiosSource
from ..sources.source import Source

__all__ = [
    "QUOTE_TTL",
    "TickerNotFoundError",
    "get_instruments",
    "get_quote",
    "get_quotes",
    "get_ratios",
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


def get_ratios(symbol: str) -> Ratios:
    return RatiosSource(symbol).get_from_yfinance()
