import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.dependencies import get_db
import asyncio

# Test database — separate from real one
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_db())




# Override get_db to use test database
async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def auth_token():
    client.post("/auth/register", json={
        "email": "fixture@gmail.com",
        "password": "test123"
    })
    response = client.post("/auth/login", json={
        "email": "fixture@gmail.com",
        "password": "test123"
    })
    return response.json()["access_token"]