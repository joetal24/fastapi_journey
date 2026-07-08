# Brain Dump — Backend Engineering

## Kafka

### Producer

**Common (every producer):**
```
1. AIOKafkaProducer(bootstrap_servers="host:port")
2. await producer.start()
3. await producer.send("topic", key=b"...", value=b"...")
4. await producer.stop()
```

**Unique (your data):**
- Key → partition routing (same key = same partition = ordered)
- Value → serialized to bytes (JSON/Protobuf/String), contains your business event
- Topic → the channel, named by your domain (`stock-updates`, `orders`, `user-events`)

**Rule:** Always encode key/value to bytes. Always `try/finally` for stop.

---

### Consumer

**Common (every consumer):**
```
1. AIOKafkaConsumer("topic", bootstrap_servers="host:port")
2. await consumer.start()
3. async for msg in consumer:     # infinite loop
       msg.key, msg.value         # your data
4. await consumer.stop()
```

**Unique (your processing logic):**
- What you do with `msg.value` — send email, run fraud check, update dashboard
- Whether you use `group_id` — same group = workload sharing, different group = independent readers

**Rule:** Consumer stays running. Never stops after one message.

---

### Key vs Value

| | Key | Value |
|---|---|---|
| Purpose | Partition routing + identity | The actual data |
| Example | `"product:5"` | `{"product_id":5, "quantity":80}` |
| Required? | Optional but recommended | Yes |
| Same key → | Same partition, ordered delivery | — |

---

### Important gotchas

- **Duplicate messages** — Kafka guarantees at-least-once delivery, not exactly-once. Your consumer must handle duplicates (idempotency).
- **Order** — Only guaranteed within a partition, not across partitions.
- **Consumer groups** — Multiple consumers with same `group_id` split partitions between them. Add more consumers = more parallelism.
- **No group_id** — Consumer starts from latest offset, only sees new messages.

---

## PostgreSQL

### Tables & Constraints

```sql
CREATE TABLE products (
    id    SERIAL PRIMARY KEY,         -- auto-increment, unique
    name  VARCHAR(200) NOT NULL,       -- required
    price NUMERIC(12,2) CHECK (price > 0)  -- must be positive
);
```

| Constraint | What it prevents |
|---|---|
| `PRIMARY KEY` | Duplicate IDs (auto-indexed) |
| `UNIQUE` | Duplicate values |
| `NOT NULL` | Missing required field |
| `CHECK` | Invalid values (negative price) |
| `FOREIGN KEY` | Orphan references |

**Key insight:** DB constraints are the last line of defense. Your app code should catch bad data first, but never trust app code to be perfect.

### Joins

| Type | Result |
|---|---|
| `INNER JOIN` | Only rows matching both tables |
| `LEFT JOIN` | All rows from left, NULLs where right missing |
| `RIGHT JOIN` | All rows from right, NULLs where left missing |

### Transactions (ACID)

```sql
BEGIN;
UPDATE products SET status='sold' WHERE id=1;
INSERT INTO transactions (...) VALUES (...);
COMMIT;  -- or ROLLBACK
```

Either both succeed or both fail. Critical when two writes must happen together. PostgreSQL auto-rolls back on error.

### Indexes

- `PRIMARY KEY` and `UNIQUE` auto-create indexes
- Add indexes on columns you `WHERE`, `JOIN`, or `ORDER BY` often
- Each index slows down writes (INSERT/UPDATE must update it)
- Use `EXPLAIN ANALYZE` to check if an index is actually used

### Query optimization

Read `EXPLAIN ANALYZE` output:
- `Seq Scan` = reading every row (bad for big tables)
- `Index Scan` = using index (good)
- `Rows Removed by Filter` = waste (rows read then discarded)

---

## Redis

### Why it's fast

- In-memory (no disk reads)
- Single-threaded event loop (no locks, no context switches)
- ~100K ops/sec per node

### Data Structures

| Type | Best for | Gotcha |
|---|---|---|
| String | Cache, counters, session tokens | `SET` without `EX` = no expiry |
| Hash | Objects read/updated field-by-field | Each field name stored as string |
| List | Job queues (FIFO/LIFO) | Unbounded `LRANGE` = OOM |
| Set | Unique membership, intersections | `SINTER` on big sets blocks Redis |
| Sorted Set | Leaderboards, time-series, rate limiting | `ZADD` overwrites score if key exists |

### Key patterns

**Cache-aside:** Read cache → miss → load DB → populate cache. Most common.

**Write-through:** Write cache + DB together. Strong consistency, slower writes.

**Stampede protection:**
```python
SET lock:key "worker" NX EX 5   # only one worker acquires
```

**Rate limiting (sliding window):**
```python
ZREMRANGEBYSCORE key 0 <cutoff>   # remove old
ZCARD key                          # count recent
ZADD key <now> <now>               # log this request
```

### Common bugs

| Bug | Cause | Fix |
|---|---|---|
| Memory leak | `SET` without `EX` | Always `SET k v EX <ttl>` |
| Lost lock | Worker crashes before `DEL` | `SET NX EX <ttl>` — auto-expire |
| Stale data after write | Writer forgets to invalidate cache | Event-based invalidation or versioning |
| Fixed window burst | Rate limit resets at boundary | Sliding window with sorted sets |

### Session management

```python
HSET session:{sid} username "joel" role "buyer"
EXPIRE session:{sid} 1800        # auto-expire after 30 min
HGETALL session:{sid}            # read on each request
EXPIRE session:{sid} 1800        # extend on activity (sliding expiry)
```

---

## Cache Invalidation

| Strategy | How | When to use |
|---|---|---|
| TTL | Auto-expire time | Data changes predictably (listings, profiles) |
| Event-based | Delete cache on write | Known write paths, you control the code |
| Versioning | Increment version on write, key includes version | Race conditions between reads and writes |

---

## REST API

### Status codes

| Code | Meaning | When |
|---|---|---|
| 200 | OK | `GET`, `PUT` success |
| 201 | Created | `POST` success |
| 401 | Unauthorized | Missing/invalid auth |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate or double-sell |
| 429 | Rate limited | Too many requests |
| 503 | Service unavailable | Temporary failure (stampede) |

### Pagination

```python
GET /products?limit=20&offset=0
```
- `limit`: items per page (max 100, default 10)
- `offset`: how many to skip (page 2 = offset=20)
- DB only reads `limit` rows instead of everything

### Validation (Pydantic)

```python
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)
```

Validates before endpoint runs. Catches: empty strings, negative numbers, missing fields. Returns clear error messages.

---

## JWT Auth

```python
# Login
row = db.fetch("SELECT * FROM users WHERE username = $1", username)
bcrypt.checkpw(password, row["password"])  # verify hash
token = jwt.encode({"sub": username, "exp": now + 1h}, SECRET, algorithm="HS256")

# Protect endpoint
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = jwt.decode(credentials.credentials, SECRET, algorithms=["HS256"])
    return payload["sub"]  # username
```

| Piece | Job |
|---|---|
| `bcrypt` | Hash passwords (one-way, never store plaintext) |
| `jwt.encode` | Sign token with expiry |
| `Depends()` | FastAPI runs this before every protected endpoint |
| `HTTPBearer` | Reads `Authorization: Bearer <token>` header |

---

## Middleware

```python
@app.middleware("http")
async def log_requests(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    logger.info(f"{request.method} {request.url.path} {response.status_code} {duration}ms")
    return response
```

Runs on every request. Common uses: logging, auth, CORS, rate limiting, request ID.

**Gotchas:** Order matters (auth before logging), blocking calls block all requests, reading response body consumes it.

---

## FastAPI patterns

**Connection management:**
```python
async def db():
    return await asyncpg.connect(DSN)

# In endpoint:
conn = await db()
try:
    # queries
finally:
    await conn.close()    # ALWAYS close, even on error
```

**Parameterized queries (prevent SQL injection):**
```python
# Safe:
conn.fetch("SELECT * FROM products WHERE id = $1", pid)
# Unsafe:
conn.fetch(f"SELECT * FROM products WHERE id = {pid}")
```
