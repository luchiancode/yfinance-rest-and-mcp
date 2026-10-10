from typing import Mapping, Protocol, Self

from typesafe_sdk import JSONContent, Question, SystemOneResponse


class DecisionModelAdapter(Protocol):
    model: str

    @classmethod
    def get(cls) -> Self: ...

    @property
    def enabled(self) -> bool: ...

    def decide(
        self, state: JSONContent, questions: Mapping[str, Question]
    ) -> SystemOneResponse | None: ...
