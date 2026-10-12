from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Query

from .models.fundamentals_models import InstrumentClass, InstrumentPage, Quote, Ratios
from ..service.fundamentals_service import (
    TickerNotFoundError,
    get_instruments as _get_instruments,
    get_quotes as _get_quotes,
    get_ratios as _get_ratios,
)
from .validation import TickerSymbol, int_range, list_of
from .deps import StoreDep

router = APIRouter()


@router.post(
    "/quotes",
    summary="Get quotes for multiple tickers",
    description=(
        "Accepts a JSON array of ticker symbols. Returns the latest available regular-market "
    ),
)
def get_quotes(
    symbols: Annotated[
        list_of(TickerSymbol, max_length=20),
        Body(description="Ticker symbols", examples=[["MSFT", "AAPL", "GOOG"]]),
    ],
    store: StoreDep,
) -> dict[str, Quote]:
    symbol_list = list(dict.fromkeys(symbol.upper() for symbol in symbols))
    try:
        return _get_quotes(symbol_list, store)
    except TickerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"No data found for ticker {exc}.") from exc


@router.get(
    "/ratios/{symbol}",
    summary="Get financial ratios for a ticker",
    description="Returns valuation, liquidity, leverage and profitability ratios for a ticker symbol.",
)
def get_ratios(symbol: TickerSymbol, store: StoreDep) -> Ratios:
    try:
        return _get_ratios(symbol.upper(), store)
    except TickerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"No data found for ticker {exc}.") from exc


@router.get(
    "/instruments",
    summary="List instruments for database seeding",
    description=(
        "Paginate stocks, ETFs and mutual funds across yfinance-supported exchanges. "
        "Ordered by size descending: market cap for stocks, net assets for funds. "
    ),
)
def get_instruments(
    store: StoreDep,
    asset_class: Annotated[
        InstrumentClass, Query(alias="assetClass", description="Instrument type"),
    ] = InstrumentClass.EQUITY,
    offset: Annotated[int_range(ge=0, le=None), Query(description="Result offset; follow nextOffset")] = 0,
    limit: Annotated[int_range(le=250), Query(description="Maximum number of results")] = 250,
) -> InstrumentPage:
    return _get_instruments(asset_class, offset=offset, limit=limit, store=store)
