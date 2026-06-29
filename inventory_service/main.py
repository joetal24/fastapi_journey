from fastapi import FastAPI, HTTPException
import asyncpg
import os

app = FastAPI(title="Inventory Service")

DSN = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5433/inventory")

async def db():
    return await asyncpg.connect(DSN)

@app.on_event("startup")
async def startup():
    conn = await db()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          SERIAL PRIMARY KEY,
            name        VARCHAR(200) NOT NULL,
            description TEXT,
            price       NUMERIC(12,2) NOT NULL CHECK (price >= 0),
            created_at  TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS stock (
            product_id  INTEGER PRIMARY KEY REFERENCES products(id),
            quantity    INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
            warehouse   VARCHAR(100) DEFAULT 'main'
        );
    """)
    await conn.close()

@app.post("/products")
async def create_product(name: str, price: float, description: str = None):
    conn = await db() #Open
    try:
        pid = await conn.fetchval(
            "INSERT INTO products (name, description, price) VALUES ($1, $2, $3) RETURNING id",
            name, description, price
        )
        await conn.execute("INSERT INTO stock (product_id, quantity) VALUES ($1, 0)", pid)
        return {"id": pid, "name": name, "price": price}
    finally:
        await conn.close() # close

@app.get("/products")
async def list_products():
    conn = await db()
    try:
        rows = await conn.fetch("""
            SELECT p.id, p.name, p.price, s.quantity
            FROM products p
            LEFT JOIN stock s ON s.product_id = p.id
            ORDER BY p.id
        """)
        return [dict(r) for r in rows]
    finally:
        await conn.close()

@app.get("/products/{pid}")
async def get_product(pid: int):
    conn = await db()
    try:
        row = await conn.fetchrow("""
            SELECT p.*, s.quantity
            FROM products p
            LEFT JOIN stock s ON s.product_id = p.id
            WHERE p.id = $1
        """, pid)
        if not row:
            raise HTTPException(status_code=404, detail="product not found")
        return dict(row)
    finally:
        await conn.close()

@app.put("/products/{pid}/stock")
async def update_stock(pid: int, quantity: int):
    if quantity < 0:
        raise HTTPException(status_code=400, detail="quantity cannot be negative")
    conn = await db()
    try:
        row = await conn.fetchrow("SELECT id FROM products WHERE id = $1", pid)
        if not row:
            raise HTTPException(status_code=404, detail="product not found")
        await conn.execute(
            "INSERT INTO stock (product_id, quantity) VALUES ($1, $2) "
            "ON CONFLICT (product_id) DO UPDATE SET quantity = $2",
            pid, quantity
        )
        return {"product_id": pid, "quantity": quantity}
    finally:
        await conn.close()


