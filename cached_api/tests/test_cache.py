import pytest
from app.main import app
from app.cache import redis_client
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_cache():
    redis_client.flushdb()
    yield

def test_cache_miss_hits_db():
    response = client.get("/plot/VOL001")
    assert response.status_code == 200
    assert response.json()["source"] == "database"

def test_cache_hit():
    client.get("/plot/VOL001")
    response = client.get("/plot/VOL001")
    assert response.json()["source"] == "cache"

def test_cache_invalidation():
    client.get("/plot/VOL001")
    version = redis_client.get("version:plot:VOL001")
    assert version is None

    client.put("/plot/VOL001", json={"owner": "New Owner"})
    version = redis_client.get("version:plot:VOL001")
    assert version == "1"

def test_unknown_plot():
    response = client.get("/plot/UNKNOWN")
    assert response.status_code == 200
    assert response.json()["data"] is None

def test_manual_invalidate():
    client.get("/plot/VOL001")

    client.post("/invalidate/VOL001")
    version = redis_client.get("version:plot:VOL001")
    assert version == "1"

def test_update_then_read():
    client.get("/plot/VOL001")
    client.put("/plot/VOL001", json={"owner": "New Owner"})
    response = client.get("/plot/VOL001")
    assert response.json()["source"] == "database"
    assert response.json()["data"]["owner"] == "New Owner"

def test_stats_endpoint():
    response = client.get("/stats")
    assert response.status_code == 200
    assert "hit_rate" in response.json()

def test_version_bump_on_update():
    client.get("/plot/VOL001")

    client.put("/plot/VOL001", json={"owner": "X"})
    v = int(redis_client.get("version:plot:VOL001"))
    assert v == 1

    client.put("/plot/VOL001", json={"owner": "Y"})
    v = int(redis_client.get("version:plot:VOL001"))
    assert v == 2
