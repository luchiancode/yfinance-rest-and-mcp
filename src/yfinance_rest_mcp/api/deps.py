from typing import Annotated

from fastapi import Depends, Request

from ..db.storage import PostgresStore


def get_store(request: Request) -> PostgresStore | None:
    return request.app.state.store


StoreDep = Annotated[PostgresStore | None, Depends(get_store)]
