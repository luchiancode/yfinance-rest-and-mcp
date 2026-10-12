from datetime import datetime

import yfinance as yf

from ..api.models.fundamentals_models import Ratios
from ..db.fundamentals_repository import get_ratio
from ..db.storage import PostgresStore
from .quote_source import TickerNotFoundError
from .source import Source


class RatiosSource(Source[Ratios]):
    def __init__(
        self,
        symbol: str, store: PostgresStore | None, *,
        since: datetime,
    ) -> None:
        self.symbol = symbol
        self.store = store
        self.since = since


    def get_from_yfinance(self) -> Ratios:
        info = yf.Ticker(self.symbol).info

        if not info or not info.get("symbol"):
            raise TickerNotFoundError(self.symbol)

        return Ratios.model_validate({**info, "symbol": self.symbol})

    def get_from_db(self) -> Ratios | None:
        if self.store is None:
            return None

        row = get_ratio(self.store, self.symbol, since=self.since)

        if row is None:
            return None

        return Ratios(**row.model_dump(exclude={"id", "recorded_at"}))
