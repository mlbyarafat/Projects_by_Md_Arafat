from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_root():
    res = client.get("/")
    assert res.status_code in (200, 307, 404)

def test_docs():
    res = client.get("/docs")
    assert res.status_code == 200

# Simple register + token flow (integration)
def test_register_and_token():
    email = "testuser@example.com"
    name = "Test User"
    pwd = "strongpassword123"
    # register
    r = client.post("/register", json={"name": name, "email": email, "password": pwd})
    assert r.status_code == 200
    # token (use form data)
    r2 = client.post("/token", data={"username": email, "password": pwd})
    assert r2.status_code == 200
    data = r2.json()
    assert "access_token" in data
