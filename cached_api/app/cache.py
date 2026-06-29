import redis
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)

def get_cached(key):
    return redis_client.get(key)

def set_cached(key, value, ttl=3600):
    redis_client.set(key, value, ex=ttl)

def delete_cached(key):
    redis_client.delete(key)
