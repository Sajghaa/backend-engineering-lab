import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import Base, engine, SessionLocal

# Create a fresh database for testing
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def clean_db():
    # Truncate tables between tests (simple for SQLite)
    db = SessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    db.close()

def test_register_and_login(client):
    # Register
    resp = client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "secret"
    })
    assert resp.status_code == 201
    user = resp.json()
    assert user["username"] == "testuser"

    # Login
    resp = client.post("/auth/login", json={
        "username": "testuser",
        "password": "secret"
    })
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token is not None

def test_invalid_login(client):
    resp = client.post("/auth/login", json={
        "username": "nobody",
        "password": "wrong"
    })
    assert resp.status_code == 401