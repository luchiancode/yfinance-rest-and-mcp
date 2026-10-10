import os
from typing import Mapping, Self

from typesafe_sdk import JSONContent, Question, SystemOneResponse, TypeSafeClient

from .protocol import DecisionModelAdapter


class TypeSafeDecider(DecisionModelAdapter):
    _instance: "TypeSafeDecider | None" = None

    def __init__(self) -> None:
        self.model = os.getenv("DECISION_MODEL", "decision-model")

        self._client = (
            TypeSafeClient(
                model=self.model,
                base_url=os.getenv("TYPESAFE_BASE_URL", "http://127.0.0.1:8008"),
                api_key=os.getenv("TYPESAFE_API_KEY") or "local",
            )

            if self.enabled
            else None
        )

    @classmethod
    def get(cls) -> Self:
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    @property
    def enabled(self) -> bool:
        return bool(self.model)

    def decide(
        self, state: JSONContent, questions: Mapping[str, Question]
    ) -> SystemOneResponse | None:
        if self._client is None:
            return None
            
        return self._client.system_one(state, questions)
