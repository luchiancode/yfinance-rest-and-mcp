from typing import Protocol


class RerankerAdapter(Protocol):
    @property
    def enabled(self) -> bool: ...

    def rerank(self, query: str, documents: list[str], limit: int) -> list[int]: ...
