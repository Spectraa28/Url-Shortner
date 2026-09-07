from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from starlette.status import (
    HTTP_307_TEMPORARY_REDIRECT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_410_GONE,
)

from db import init_db
from exceptions import (
    AlreadyExistsError,
    InvalidAliasError,
    ShortUrlNotFoundError,
    UrlExpiredError,
)
from queries.models import AnalyticsResponse, ShortenRequest, ShortenResponse
from service import create_short_url, get_analytics, get_redirect_url


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/shorten")
def short_url(request: ShortenRequest) -> ShortenResponse:
    """Generates a short code for the original url and return a short url"""
    try:
        url = create_short_url(request)
    except InvalidAliasError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    except AlreadyExistsError as e:
        raise HTTPException(status_code=HTTP_409_CONFLICT, detail=str(e))
    return url


@app.get("/{short_code}")
def redirect(short_code: str):
    """Fetches the original url from the Db and redirects to that"""
    try:
        url = get_redirect_url(short_code)
    except ShortUrlNotFoundError as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))
    except UrlExpiredError as e:
        raise HTTPException(status_code=HTTP_410_GONE, detail=str(e))
    return RedirectResponse(url=url, status_code=HTTP_307_TEMPORARY_REDIRECT)


@app.get("/analytics/{short_code}")
def analytics(short_code: str) -> AnalyticsResponse:
    """Gives the no. of clicks on the url"""
    try:
        result = get_analytics(short_code)
    except ShortUrlNotFoundError as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))
    return result
