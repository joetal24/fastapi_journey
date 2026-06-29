# 🚀 FastAPI Journey

Welcome to my FastAPI learning journey! This repository captures my progress as I explore building robust, scalable, and observable APIs using FastAPI and modern architecture patterns.

## 📂 Project Structure

This repository is organized into different modules, each focusing on a specific aspect of the FastAPI ecosystem:

*   **[prometheus_fastapi/](./prometheus_fastapi/)**: Implementation of observability using Prometheus and FastAPI.
*   **[clean-architecture/](./clean-architecture/)**: A deep dive into structuring FastAPI applications using Clean Architecture principles.
*   **[supabase1/](./supabase1/)**: Integration examples with Supabase for authentication and database management.
*   **[To_do/](./To_do/)**: A practical TODO application to test core FastAPI features.
*   **[cached_api/](./cached_api/)**: Redis caching layer with 4 patterns (cache-aside, write-through, write-behind, refresh-ahead), benchmarked at 220-365x speedup.

## 🛠️ Tech Stack

*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
*   **Observability**: Prometheus & Grafana
*   **Database**: Supabase (PostgreSQL)
*   **Caching**: Redis
*   **Architecture**: Clean Architecture / Hexagonal Architecture

## 🚦 Getting Started

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/joetal24/fastapi_journey.git
    cd fastapi_journey
    ```

2.  **Explore individual modules**:
    Each folder contains its own setup instructions and dependencies.

---

## 🎙️ Interview Prep — Caching & Redis

### Fundamentals
- **Why cache?** Reduce latency (300x+ faster), reduce DB load, lower cost.
- **Cache-aside**: App checks cache → miss → loads DB → populates cache. Most common, good for read-heavy.
- **Write-through**: Write to cache + DB synchronously. Strong consistency, slower writes.
- **Write-behind**: Write to cache, async job persists to DB. Fast writes, eventual consistency, risk of loss.
- **Refresh-ahead**: Refresh cache in background before TTL expires. Prevents misses on hot keys.

### Eviction Policies
| Policy | Behavior | Use Case |
|--------|----------|----------|
| LRU | Evicts least recently used | General-purpose, most common |
| LFU | Evicts least frequently used | Content delivery, popularity-based |
| FIFO | Evicts oldest first | Simple, predictable |
| TTL | Expire after fixed time | Session data, temp results |

### Redis Architecture
- **Single-threaded event loop** → atomic operations, no race conditions, ~100K ops/sec
- **Persistence**: RDB (point-in-time snapshot) vs AOF (append-only log, every write)
- **vs Memcached**: Redis has richer data structures, persistence, replication. Memcached is simpler, multi-threaded.
- **Cluster**: Hash slots (16384), automatic sharding, no cross-slot multi-key ops

### Common Interview Questions
1. *"How would you design a cache for a high-traffic API?"* → Cache-aside + Redis + TTL + invalidation on write
2. *"How do you handle cache stampede?"* → Locking (SETNX), stale-while-revalidate, refresh-ahead
3. *"What happens if Redis goes down?"* → Circuit breaker to DB, preload on startup, Redis Sentinel for HA
4. *"How do you invalidate nested caches?"* → Dependency tracking, cache versioning, event-driven invalidation
5. *"Redis vs Memcached vs local cache?"* → Redis for features/durability, Memcached for simplicity, local for single-instance speed

---
*Follow my journey as I build and learn!*
