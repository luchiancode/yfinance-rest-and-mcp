import os
from typing import Self

import httpx

from .protocol import EmbedderAdapter


class OpenAICompatibleEmbedder(EmbedderAdapter):
    _instance: "OpenAICompatibleEmbedder | None" = None

    def __init__(self) -> None:
        self.model = os.getenv("EMBEDDING_MODEL") or ""
        self._base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1").rstrip("/")

        self._headers = {}

        #Optional
        if api_key := os.getenv("OPENAI_API_KEY"):
            self._headers["Authorization"] = f"Bearer {api_key}"

        #Optional
        if site_url := os.getenv("YOUR_SITE_URL"):
            self._headers["HTTP-Referer"] = site_url

        #Optional
        if site_name := os.getenv("YOUR_SITE_NAME"):
            self._headers["X-OpenRouter-Title"] = site_name


    @classmethod
    def get(cls) -> Self:
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    @property
    def enabled(self) -> bool:
        return bool(self.model)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not self.enabled:
            return []

        response = httpx.post(
            f"{self._base_url}/embeddings",
            json={"model": self.model, "input": texts, "encoding_format": "float"},
            headers=self._headers,
            timeout=60,
        )

        response.raise_for_status()
        data = response.json()["data"]

        return [item["embedding"] for item in sorted(data, key=lambda item: item["index"])]

    def embed_rows(self, rows: dict[str, dict], *keys: str) -> None:
        if not self.enabled or not keys:
            return

        texts = [
            "\n".join(str(row[key]) for key in keys if row.get(key))
            for row in rows.values()
        ]
        try:
            vectors = self.embed([text for text in texts if text])
        except Exception:
            return

        vector_iter = iter(vectors)
        for row, text in zip(rows.values(), texts, strict=True):
            if not text:
                continue
            row["embedding"] = next(vector_iter)
            row["embedding_model"] = self.model
