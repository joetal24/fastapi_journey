import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.dependencies import get_db


# Test database — separate from real one
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

# Create tables before tests run
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)



# Override get_db to use test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

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