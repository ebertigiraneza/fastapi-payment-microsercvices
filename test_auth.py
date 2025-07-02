# test_auth.py
from fastapi.testclient import TestClient
from authentification.main import app
from shared.databases import database
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
async def setup_db():
    await database.connect()
    yield
    await database.disconnect()

def test_successful_login_sync():

    test_user = {
        "email": "test@example.com",
        "password": "securepassword",
        "username": "testuser"
    }
    client.post("/auth/register", json=test_user)

    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "securepassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()   
    
def test_invalid_credentials():
    client = TestClient(app)
    response = client.post(
        "/auth/login",
        data={"username": "fake@user.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

    