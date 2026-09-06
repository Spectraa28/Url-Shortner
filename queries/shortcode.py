import base62
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def generate_short_code() -> str:
    count = r.incr("url_counter")
    short_code = base62.encode(count)
    return short_code


RESERVED_ALIASES = {"analytics", "admin", "redoc", "docs"}


def is_valid_alias(alias: str) -> bool:
    if len(alias) <= 0:
        return False
    low_alias = alias.lower()
    if low_alias in RESERVED_ALIASES:
        return False
    return low_alias.isalnum()
