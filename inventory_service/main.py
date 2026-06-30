from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import asyncpg
import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI(title="Inventory Service")
security = HTTPBearer()

DSN = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5433/inventory")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGO = "HS256"

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)
    description: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    quantity: int

class StockUpdate(BaseModel):
    quantity: int = Field(..., ge=0)

async def db():
    return await asyncpg.connect(DSN)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid token")

@app.on_event("startup")
async def startup():
    conn = await db()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id        SERIAL PRIMARY KEY,
            username  VARCHAR(50) UNIQUE NOT NULL,
            password  VARCHAR(200) NOT NULL,
            role      VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
            created_at TIMESTAMP DEFAULT NOW()
        );
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

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(username: str, password: str):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = await db()
    try:
        await conn.execute("INSERT INTO users (username, password) VALUES ($1, $2)", username, hashed)
        return {"username": username}
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="username already exists")
    finally:
        await conn.close()

@app.post("/login")
async def login(username: str, password: str):
    conn = await db()
    try:
        row = await conn.fetchrow("SELECT * FROM users WHERE username = $1", username)
        if not row or not bcrypt.checkpw(password.encode(), row["password"].encode()):
            raise HTTPException(status_code=401, detail="invalid credentials")
        token = jwt.encode(
            {"sub": username, "role": row["role"], "exp": datetime.utcnow() + timedelta(hours=1)},
            JWT_SECRET, algorithm=JWT_ALGO
        )
        return {"access_token": token, "token_type": "bearer"}
    finally:
        await conn.close()

@app.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(body: ProductCreate, user: str = Depends(get_current_user)):
    conn = await db()
    try:
        pid = await conn.fetchval(
            "INSERT INTO products (name, description, price) VALUES ($1, $2, $3) RETURNING id",
            body.name, body.description, body.price
        )
        await conn.execute("INSERT INTO stock (product_id, quantity) VALUES ($1, 0)", pid)
        return {"id": pid, "name": body.name, "price": body.price}
    finally:
        await conn.close()

@app.get("/products")
async def list_products(q: str = None):
    conn = await db()
    try:
        if q:
            rows = await conn.fetch("""
                SELECT p.id, p.name, p.price, s.quantity
                FROM products p
                LEFT JOIN stock s ON s.product_id = p.id
                WHERE p.name ILIKE $1
                ORDER BY p.id
            """, f"%{q}%")
        else:
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
async def update_stock(pid: int, quantity: int, user: str = Depends(get_current_user)):
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


