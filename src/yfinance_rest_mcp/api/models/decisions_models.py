from enum import StrEnum

from pydantic import BaseModel


class Sentiment(StrEnum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


class SentimentDecision(BaseModel):
    symbol: str
    sentiment: Sentiment
    score: float | None = None
    confidence: float
