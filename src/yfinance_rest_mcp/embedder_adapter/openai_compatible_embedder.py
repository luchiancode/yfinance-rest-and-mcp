import os
from pathlib import Path
from typing import Self

import httpx
from tokenizers import Tokenizer

from .protocol import EmbedderAdapter

MAX_EMBED_TOKENS = 7 * 1024


class OpenAICompatibleEmbedder(EmbedderAdapter):
    _instance: "OpenAICompatibleEmbedder | None" = None

    def __init__(self) -> None:
        self.model = os.getenv("EMBEDDING_MODEL") or ""
        self._base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1")

        tokenizer_path = Path(__file__).resolve().parent.parent / "tokenizers" / "embeddinggemma-2-tokenizer.json"
        
        self._tokenizer = Tokenizer.from_file(str(tokenizer_path))
        self._tokenizer.no_truncation()
        self._tokenizer.no_padding()

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
        if not self.enabled or not texts:
            return []

        chunks = [self.split_text(text) for text in texts]

        inputs = []
        for text_chunks in chunks:
            inputs.extend(text_chunks)

        response = httpx.post(
            f"{self._base_url}/embeddings",
            json={"model": self.model, "input": inputs, "encoding_format": "float"},
            headers=self._headers,
            timeout=60,
        )

        response.raise_for_status()

        embeddings = self.combine_embeddings(response.json()["data"], chunks)
        return embeddings


    def embed_rows(self, rows: dict[str, dict], *keys: str) -> list[list[float] | None]:
        texts = [
            "\n".join(str(row[key]) for key in keys if row.get(key))
            for row in rows.values()
        ]

        if not self.enabled or not keys:
            return [None] * len(texts)

        try:
            vectors = self.embed([text for text in texts if text])
        except Exception:
            return [None] * len(texts)

        vector_iter = iter(vectors)
        return [next(vector_iter) if text else None for text in texts]

    def split_text(self, text: str) -> list[str]:
        encoding = self._tokenizer.encode(text, add_special_tokens=False)
        token_limit = MAX_EMBED_TOKENS - self._tokenizer.num_special_tokens_to_add(False)

        if len(encoding.ids) <= token_limit:
            return [text]

        chunks = []
        start = 0
        for token_offset in range(token_limit, len(encoding.ids), token_limit):
            end = encoding.offsets[token_offset][0]
            if end > start:
                chunks.append(text[start:end])
                start = end
                
        chunks.append(text[start:])

        return chunks


    def combine_embeddings(self, data: list[dict], chunks: list[list[str]]) -> list[list[float]]:
        data = sorted(data, key=lambda item: item["index"])

        vectors = [item["embedding"] for item in data]
        result = []
        offset = 0
        
        for group in chunks:
            batch = vectors[offset:offset + len(group)]
            result.append(batch[0] if len(batch) == 1 else [
                sum(values) / len(batch) for values in zip(*batch, strict=True)
            ])
            offset += len(group)
            
        return result