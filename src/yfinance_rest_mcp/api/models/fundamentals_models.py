from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

class InstrumentClass(StrEnum):
    EQUITY = "EQUITY"
    ETF = "ETF"
    MUTUALFUND = "MUTUALFUND"

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

class Ratios(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    symbol: str
    current_price: float | None = Field(default=None, alias="currentPrice")
    market_cap: int | None = Field(default=None, alias="marketCap")
    enterprise_value: int | None = Field(default=None, alias="enterpriseValue")
    average_volume: int | None = Field(default=None, alias="averageVolume")
    current_ratio: float | None = Field(default=None, alias="currentRatio")
    quick_ratio: float | None = Field(default=None, alias="quickRatio")
    debt_to_equity: float | None = Field(default=None, alias="debtToEquity")
    dividend_yield: float | None = Field(default=None, alias="dividendYield")
    trailing_eps: float | None = Field(default=None, alias="trailingEps")
    enterprise_to_ebitda: float | None = Field(default=None, alias="enterpriseToEbitda")
    enterprise_to_revenue: float | None = Field(default=None, alias="enterpriseToRevenue")
    free_cashflow: int | None = Field(default=None, alias="freeCashflow")
    price_to_book: float | None = Field(default=None, alias="priceToBook")
    trailing_pe: float | None = Field(default=None, alias="trailingPE")
    price_to_sales_trailing_12_months: float | None = Field(default=None, alias="priceToSalesTrailing12Months")
    return_on_assets: float | None = Field(default=None, alias="returnOnAssets")
    return_on_equity: float | None = Field(default=None, alias="returnOnEquity")

