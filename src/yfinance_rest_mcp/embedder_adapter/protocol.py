from typing import Protocol, Self


class EmbedderAdapter(Protocol):
    model: str

    @classmethod
    def get(cls) -> Self: ...

    @property
    def enabled(self) -> bool: ...

    def embed(self, texts: list[str]) -> list[list[float]]: ...

    def embed_rows(self, rows: dict[str, dict], *keys: str) -> None: ...
