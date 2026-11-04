from typing import Annotated

from fastapi import APIRouter, Body, HTTPException

from .models.decisions_models import SentimentDecision
from ..service.decisions_service import get_sentiment as _get_sentiment
from .validation import TickerSymbol, string

router = APIRouter()


@router.post(
    "/decisions/sentiment",
    summary="Decide news sentiment for a ticker",
    description="Decides whether a news text is positive, neutral or negative for a ticker.",
)
def decide_sentiment(
    ticker: Annotated[TickerSymbol, Body(description="Ticker symbol")],
    text: Annotated[string(max_length=10_000), Body(description="News text to evaluate")],
) -> SentimentDecision:
    result = _get_sentiment(ticker.upper(), text)

    if result is None:
        raise HTTPException(status_code=503, detail="Decision model is not configured.")

    return result
