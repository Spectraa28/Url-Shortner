from datetime import datetime

from pydantic import BaseModel, HttpUrl


class ShortenRequest(BaseModel):
    original_url: HttpUrl
    expires_in_hours: int | None = None
    custom_alias: str | None = None


class ShortenResponse(BaseModel):
    short_code: str
    short_url: HttpUrl


class AnalyticsResponse(BaseModel):
    original_url: HttpUrl
    created_at: datetime
    expires_at: datetime
    click_count: int
