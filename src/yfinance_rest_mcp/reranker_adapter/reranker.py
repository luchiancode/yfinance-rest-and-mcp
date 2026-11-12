import os

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .protocol import RerankerAdapter


class RerankResult(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)

    index: int = Field(ge=0, strict=True)
    relevance_score: float


class RerankResponse(BaseModel):
    results: list[RerankResult]


class Reranker(RerankerAdapter):
    """rank documents by relevance to a query"""

    def __init__(self) -> None:
        self.model = os.getenv("RERANKER_MODEL", "").strip()
        self.url = os.getenv("RERANKER_URL", "").strip()

        self._headers = {}
        if key := os.getenv("RERANKER_API_KEY"):
            self._headers["Authorization"] = f"Bearer {key}"

    @property
    def enabled(self) -> bool:
        return bool(self.model)

    def rerank(self, query: str, documents: list[str], limit: int) -> list[int]:
        if not documents:
            return []
        if not self.enabled:
            return list(range(min(limit, len(documents))))
        if not self.url:
            raise ValueError("RERANKER_URL is required when RERANKER_MODEL is set")
        
        response = httpx.post(
            self.url,
            json={"model": self.model, "query": query, "documents": documents,
                  "top_n": min(limit, len(documents))},
            headers=self._headers,
            timeout=60,
        )

        response.raise_for_status()
        results = RerankResponse.model_validate(response.json()).results
        indices = [result.index for result in results]

        if len(set(indices)) != len(indices) or any(i >= len(documents) for i in indices):
            raise ValueError("Reranker returned invalid document indices")
        
        return [result.index for result in sorted(
            results, key=lambda result: result.relevance_score, reverse=True
        )][:limit]
