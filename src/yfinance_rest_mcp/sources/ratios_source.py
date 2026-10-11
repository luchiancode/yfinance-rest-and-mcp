import yfinance as yf

from ..api.models.fundamentals_models import Ratios
from .quote_source import TickerNotFoundError
from .source import Source


class RatiosSource(Source[Ratios]):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

    def get_from_yfinance(self) -> Ratios:
        info = yf.Ticker(self.symbol).info

        if not info or not info.get("symbol"):
            raise TickerNotFoundError(self.symbol)

        return Ratios.model_validate({**info, "symbol": self.symbol})

    def get_from_db(self) -> Ratios | None:
        return None
