from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Article(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    external_id: str | None = Field(default=None, alias="externalId")
    title: str | None = None
    description: str | None = None
    content: str | None = None
    url: str | None = None
    image: str | None = None
    published_at: datetime | None = Field(default=None, alias="publishedAt")
    source: str | None = None
