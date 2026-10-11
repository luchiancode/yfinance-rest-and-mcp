from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

class InstrumentClass(StrEnum):
    EQUITY = "EQUITY"
    ETF = "ETF"
    MUTUALFUND = "MUTUALFUND"

class Quote(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    symbol: str
    name: str | None = None
    exchange: str | None = None
    currency: str | None = None
    regular_market_price: float | None = Field(default=None, alias="regularMarketPrice")
    regular_market_time: datetime | None = Field(
        default=None,
        alias="regularMarketTime",
        description="UTC source timestamp for the regular-market price; null if unavailable.",
    )
    regular_market_change: float | None = Field(default=None, alias="regularMarketChange")
    regular_market_change_percent: float | None = Field(default=None, alias="regularMarketChangePercent")
    regular_market_volume: int | None = Field(default=None, alias="regularMarketVolume")
    regular_market_day_low: float | None = Field(default=None, alias="regularMarketDayLow")
    regular_market_day_high: float | None = Field(default=None, alias="regularMarketDayHigh")
    regular_market_open: float | None = Field(default=None, alias="regularMarketOpen")
    regular_market_previous_close: float | None = Field(default=None, alias="regularMarketPreviousClose")
    fifty_two_week_low: float | None = Field(default=None, alias="fiftyTwoWeekLow")
    fifty_two_week_high: float | None = Field(default=None, alias="fiftyTwoWeekHigh")
    fifty_day_average: float | None = Field(default=None, alias="fiftyDayAverage")
    two_hundred_day_average: float | None = Field(default=None, alias="twoHundredDayAverage")
    market_cap: int | None = Field(default=None, alias="marketCap")

class Instrument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    symbol: str
    name: str | None = None
    asset_class: str = Field(alias="assetClass")
    aliases: list[str] = Field(default_factory=list)
    exchange: str | None = Field(default=None, description="Exchange identifier, not a MIC code.")
    currency: str | None = Field(default=None, description="Currency or price-unit code.")
    size: float | None = Field(default=None, exclude=True)


class InstrumentPage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[Instrument]
    total: int
    offset: int
    next_offset: int | None = Field(alias="nextOffset")


class Article(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    external_id: str | None = Field(default=None, alias="externalId")
    title: str | None = None
    description: str | None = None
    content: str | None = None
    url: str | None = None
    image: str | None = None
    published_at: datetime | None = Field(default=None, alias="publishedAt")
    source: str | None = None
