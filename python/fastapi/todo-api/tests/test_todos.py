from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_todo():
    response = client.post("/todos/", json={"title": "Test Todo", "description": "Test description"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["completed"] == False
    assert "id" in data

def test_get_todos():
    response = client.get("/todos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)