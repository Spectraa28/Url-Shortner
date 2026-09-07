# URL Shortener

A URL shortener built with FastAPI, SQLite, and Redis. Supports custom aliases, click-count analytics, and configurable expiration.

## Features

- **Custom aliases** — pick your own short code, or let the system generate one
- **Click analytics** — track total clicks per short link
- **Expiration** — links expire after a user-defined duration (in hours), or fall back to a default

## Architecture

The project follows a layered design, similar to a Controller → Service → Repository pattern:

```
main.py         Controller layer — HTTP routes, request/response handling,
                exception → HTTPException translation

service.py      Service layer — business logic (validation, expiry
                calculation, orchestration)

db.py           Repository layer — raw SQL against SQLite, no business logic

models.py       Pydantic schemas — request/response shapes

shortcode.py    Short code generation (Redis counter + base62 encoding)
                and custom alias validation

exceptions.py   Domain-specific exceptions, framework-agnostic
```

### Short code generation

Short codes are generated using an atomic Redis counter (`INCR`) encoded into
base62 (`0-9`, `a-z`, `A-Z`). This guarantees collision-free, ever-increasing
codes without needing a check-then-insert step. Custom aliases bypass the
counter entirely and are validated against a reserved-word list and a
strict alphanumeric format before being inserted.

### Data store

SQLite is used for persistence. A single `urls` table stores everything
needed — no separate analytics table, since click tracking is a simple
counter rather than per-event logging.

```sql
CREATE TABLE urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_code TEXT UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    click_count INTEGER NOT NULL DEFAULT 0
);
```

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Redis server running locally

### Install dependencies

```bash
uv sync
```

### Configure environment

Create a `.env` file in the project root:

```
BASE_URL=http://localhost:8000/
```

### Start Redis

```bash
redis-server --daemonize yes --port 6379
```

### Run the app

```bash
uv run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`, with interactive docs
at `http://localhost:8000/docs`.

## API

### `POST /shorten`

Create a short URL.

**Request body:**

```json
{
    "original_url": "https://example.com/some/long/path",
    "custom_alias": "mycoolsite",
    "expires_in_hours": 24
}
```

`custom_alias` and `expires_in_hours` are optional. If `custom_alias` is
omitted, a code is generated. If `expires_in_hours` is omitted, a default
duration is applied.

**Response:**

```json
{
    "short_code": "mycoolsite",
    "short_url": "http://localhost:8000/mycoolsite"
}
```

**Errors:**

| Status | Cause                                                           |
| ------ | --------------------------------------------------------------- |
| 400    | Custom alias fails validation (bad characters or reserved word) |
| 409    | Custom alias already exists                                     |

### `GET /{short_code}`

Redirects to the original URL and increments the click count.

**Errors:**

| Status | Cause                             |
| ------ | --------------------------------- |
| 404    | Short code doesn't exist          |
| 410    | Short code exists but has expired |

### `GET /analytics/{short_code}`

Returns stats for a short URL. Works regardless of expiration status.

**Response:**

```json
{
    "original_url": "https://example.com/some/long/path",
    "created_at": "2026-09-06T10:00:00",
    "expires_at": "2026-09-07T10:00:00",
    "click_count": 12
}
```

**Errors:**

| Status | Cause                    |
| ------ | ------------------------ |
| 404    | Short code doesn't exist |

## Known limitations

This is a personal/learning project and intentionally leaves out things a
production system would need:

- No cleanup job for expired rows — they remain in the database
- Redis counter is in-memory only; a Redis restart without persistence
  configured resets the counter (SQLite's `UNIQUE` constraint prevents
  silent collisions, but inserts would start failing until the counter
  catches back up)
- Short codes are case-sensitive
