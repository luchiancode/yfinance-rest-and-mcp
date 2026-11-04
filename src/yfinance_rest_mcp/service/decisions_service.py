from typesafe_sdk import Choice, Score

from ..api.models.decisions_models import Sentiment, SentimentDecision
from ..decision_model_adapter.typesafe_decider import TypeSafeDecider


def get_sentiment(symbol: str, text: str) -> SentimentDecision | None:
    decider = TypeSafeDecider.get()
    response = decider.decide(
        {"ticker": symbol, "information": text},
        {
            "sentiment": Choice(
                instructions=f"Is this information positive, negative, or neutral for {symbol}?",
                criteria={
                    "POSITIVE": "The information is likely to benefit the ticker's price or business.",
                    "NEUTRAL": "The information is mixed, minor, or has no clear impact on the ticker.",
                    "NEGATIVE": "The information is likely to hurt the ticker's price or business.",
                },
            ),
            "impact": Score(
                instructions=f"Rate the item expected impact on {symbol}, from -10 (very negative) to 10 (very positive).",
                criteria=["-10", "-5", "0", "5", "10"]
            ),
        },
    )

    if response is None:
        return None

    sentiment = response.choices["sentiment"]
    impact = response.scores.get("impact")

    return SentimentDecision(
        symbol=symbol,
        sentiment=Sentiment(sentiment.choice.upper()),
        score=impact.score if impact is not None else None,
        confidence=sentiment.confidence,
    )
