"""Simple sliding-window rate limiter (Redis preferred, in-memory fallback)."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

import redis.asyncio as aioredis
from fastapi import HTTPException, Request, status

from app.core.config import get_settings

_memory: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()


def client_key(request: Request, bucket: str) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    ip = (forwarded.split(",")[0].strip() if forwarded else None) or (
        request.client.host if request.client else "unknown"
    )
    return f"rl:{bucket}:{ip}"


async def enforce_rate_limit(request: Request, *, bucket: str, limit: int, window_seconds: int) -> None:
    key = client_key(request, bucket)
    settings = get_settings()
    allowed = await _redis_allow(settings.redis_url, key, limit, window_seconds)
    if allowed is None:
        allowed = _memory_allow(key, limit, window_seconds)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Try again later.",
        )


async def _redis_allow(redis_url: str, key: str, limit: int, window_seconds: int) -> bool | None:
    client = aioredis.from_url(redis_url, decode_responses=True)
    try:
        pipe = client.pipeline()
        now = time.time()
        pipe.zremrangebyscore(key, 0, now - window_seconds)
        pipe.zadd(key, {f"{now}": now})
        pipe.zcard(key)
        pipe.expire(key, window_seconds + 1)
        results = await pipe.execute()
        count = int(results[2])
        return count <= limit
    except Exception:
        return None
    finally:
        await client.aclose()


def _memory_allow(key: str, limit: int, window_seconds: int) -> bool:
    now = time.time()
    with _lock:
        q = _memory[key]
        while q and q[0] < now - window_seconds:
            q.popleft()
        q.append(now)
        return len(q) <= limit
