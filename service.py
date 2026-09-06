import os
import sqlite3
from datetime import datetime, timedelta

from dotenv import load_dotenv
from pydantic import HttpUrl

from db import get_url_by_code, increment_click, insert_url
from exceptions import (
    AlreadyExistsError,
    InvalidAliasError,
    ShortUrlNotFoundError,
    UrlExpiredError,
)
from queries.models import AnalyticsResponse, ShortenRequest, ShortenResponse
from queries.shortcode import generate_short_code, is_valid_alias

load_dotenv()


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/")


def create_short_url(request: ShortenRequest) -> ShortenResponse:
    if request.custom_alias:
        if is_valid_alias(request.custom_alias):
            short_code = request.custom_alias
        else:
            raise InvalidAliasError()
    else:
        short_code = generate_short_code()

    if request.expires_in_hours:
        expire = request.expires_in_hours
    else:
        expire = 5
    now = datetime.now()
    created_at = now.isoformat()
    expires_at = now + timedelta(hours=expire)
    expires_at_str = expires_at.isoformat()

    try:
        insert_url(short_code, str(request.original_url), created_at, expires_at_str)
    except sqlite3.IntegrityError:
        raise AlreadyExistsError()
    short_url = BASE_URL + short_code
    return ShortenResponse(short_code=short_code, short_url=short_url)


def get_redirect_url(short_code: str) -> HttpUrl:
    row = get_url_by_code(short_code)
    if row is None:
        raise ShortUrlNotFoundError()
    expires_at = datetime.fromisoformat(row["expires_at"])
    if expires_at < datetime.now():
        raise UrlExpiredError()
    increment_click(short_code)
    return row["original_url"]


def get_analytics(short_code: str) -> AnalyticsResponse:
    row = get_url_by_code(short_code)
    if row is None:
        raise ShortUrlNotFoundError()
    return AnalyticsResponse(
        original_url=row["original_url"],
        created_at=row["created_at"],
        expires_at=row["expires_at"],
        click_count=row["click_count"],
    )
