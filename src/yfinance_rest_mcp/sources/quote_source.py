from datetime import UTC, datetime

import yfinance as yf

from ..api.models.fundamentals_models import Quote
from ..db.fundamentals_repository import get_quote
from ..db.storage import PostgresStore
from .source import Source


class TickerNotFoundError(LookupError):
    pass


class QuoteSource(Source[Quote]):
    def __init__(
        self,
        symbol: str, store: PostgresStore | None, *,
        since: datetime,
    ) -> None:
        self.symbol = symbol
        self.store = store
        self.since = since

    def get_from_db(self) -> Quote | None:
        if self.store is None:
            return None

        row = get_quote(self.store, self.symbol, since=self.since)

        if row is None:
            return None

        return Quote(**row.model_dump(exclude={"id", "recorded_at"}))

    def get_from_yfinance(self) -> Quote:
        info = yf.Ticker(self.symbol).info

        if not info or not info.get("symbol"):
            raise TickerNotFoundError(self.symbol)

        price = info.get("regularMarketPrice") or info.get("currentPrice")
        price_timestamp = info.get("regularMarketTime") if price is not None else None

        return Quote(
            symbol=self.symbol,
            name=info.get("longName") or info.get("shortName"),
            exchange=info.get("fullExchangeName") or info.get("exchange"),
            currency=info.get("currency"),
            regular_market_price=price,
            regular_market_time=datetime.fromtimestamp(price_timestamp, UTC) if price_timestamp is not None else None,
            regular_market_change=info.get("regularMarketChange"),
            regular_market_change_percent=info.get("regularMarketChangePercent"),
            regular_market_volume=info.get("regularMarketVolume"),
            regular_market_day_low=info.get("regularMarketDayLow"),
            regular_market_day_high=info.get("regularMarketDayHigh"),
            regular_market_open=info.get("regularMarketOpen"),
            regular_market_previous_close=info.get("regularMarketPreviousClose"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            fifty_day_average=info.get("fiftyDayAverage"),
            two_hundred_day_average=info.get("twoHundredDayAverage"),
            market_cap=info.get("marketCap"),
        )
