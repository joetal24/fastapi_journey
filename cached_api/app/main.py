from fastapi import FastAPI, Request, HTTPException
from starlette.responses import JSONResponse
from app.cache import get_cached, set_cached, delete_cached, redis_client
from app.db import get_plot_from_db, update_plot_in_db
import json
import time
import asyncio
import secrets

app = FastAPI(title="Cached API", description="Redis caching patterns demo")

def _cache_key(plot_id: str, version: int = None) -> str:
    if version is None:
        v = redis_client.get(f"version:plot:{plot_id}")
        version = int(v) if v is not None else 0
    return f"plot:{plot_id}:v{version}"

def _bump_version(plot_id: str):
    redis_client.incr(f"version:plot:{plot_id}")

def check_rate_limit(key: str, max_requests: int = 10, window_secs: int = 60) -> bool:
    now = time.time()
    cutoff = now - window_secs
    redis_client.zremrangebyscore(key, 0, cutoff)
    if redis_client.zcard(key) >= max_requests:
        return False
    redis_client.zadd(key, {str(now): now})
    redis_client.expire(key, window_secs)
    return True

@app.get("/plot/{plot_id}")
async def get_plot(plot_id: str, request: Request = None, _retry: int = 0):
    if request and request.client:
        ip = request.client.host
        if not check_rate_limit(f"ratelimit:{ip}:plot", max_requests=5, window_secs=10):
            raise HTTPException(status_code=429, detail="rate limit exceeded")

    if _retry > 5:
        return JSONResponse(status_code=503, content={"error": "try again"})

    key = _cache_key(plot_id)
    cached = get_cached(key)
    if cached:
        return {"source": "cache", "data": json.loads(cached)}

    acquired = redis_client.set(f"lock:plot:{plot_id}", "refreshing", nx=True, ex=5)
    if not acquired:
        await asyncio.sleep(0.1)
        return await get_plot(plot_id, _retry=_retry + 1)

    start = time.time()
    plot_data = get_plot_from_db(plot_id)
    db_latency = time.time() - start

    if plot_data:
        key = _cache_key(plot_id)
        set_cached(key, json.dumps(plot_data), ttl=3600)
    redis_client.delete(f"lock:plot:{plot_id}")

    return {
        "source": "database",
        "db_latency_ms": round(db_latency * 1000, 1),
        "data": plot_data,
    }

@app.put("/plot/{plot_id}")
async def update_plot(plot_id: str, new_data: dict):
    updated = update_plot_in_db(plot_id, new_data)
    _bump_version(plot_id)
    return {"status": "updated", "data": updated, "version_bumped": True}

@app.post("/invalidate/{plot_id}")
async def manual_invalidate(plot_id: str):
    _bump_version(plot_id)
    return {"status": "version bumped", "plot_id": plot_id}

@app.post("/plot/{plot_id}/purchase")
async def purchase_plot(plot_id: str):
    acquired = redis_client.set(f"lock:plot:{plot_id}", "sold", nx=True, ex=30)
    if not acquired:
        return JSONResponse(status_code=409, content={"error": "already sold"})

    update_plot_in_db(plot_id, {"status": "sold"})
    _bump_version(plot_id)
    redis_client.delete(f"lock:plot:{plot_id}")
    return {"status": "sold", "plot_id": plot_id}

def _get_session(request: Request):
    sid = request.headers.get("x-session-id")
    if not sid:
        raise HTTPException(status_code=401, detail="missing session")
    data = redis_client.hgetall(f"session:{sid}")
    if not data:
        raise HTTPException(status_code=401, detail="invalid or expired session")
    redis_client.expire(f"session:{sid}", 1800)
    return data

@app.post("/login")
async def login(username: str):
    sid = secrets.token_hex(16)
    redis_client.hset(f"session:{sid}", mapping={
        "username": username,
        "role": "buyer",
        "login_time": str(time.time()),
    })
    redis_client.expire(f"session:{sid}", 1800)
    return {"session_id": sid, "expires_in": "30 minutes"}

@app.get("/me")
async def get_me(request: Request):
    session = _get_session(request)
    return {"user": session["username"], "role": session["role"]}

@app.get("/stats")
async def cache_stats():
    info = redis_client.info("stats")
    hits = info.get("keyspace_hits", 0)
    misses = info.get("keyspace_misses", 0)
    total = hits + misses
    hit_rate = hits / total if total > 0 else 0
    return {"hits": hits, "misses": misses, "hit_rate": round(hit_rate, 4)}
