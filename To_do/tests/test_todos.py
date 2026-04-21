from tests.conftest import client

def test_register():
    response = client.post("/auth/register", json={
        "email": "test@gmail.com",
        "password": "test123"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "test@gmail.com"

def test_login():
    response = client.post("/auth/login", json={
        "email": "test@gmail.com",
        "password": "test123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_todos(auth_token): 
    # use token in header
    response = client.get("/todos/", headers={
        "Authorization": f"Bearer {auth_token}"
    })
    assert response.status_code == 200
    assert response.json() == []


def test_create_todo(auth_token):
    response = client.post("/todos/", 
        json={"title": "Buy milk", "completed": False},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Buy milk"