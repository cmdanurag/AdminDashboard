def test_signup(client):
    response = client.post(
        "/auth/signup",
        json={"name": "Test User", "email": "test@example.com", "password": "password123", "is_admin": False}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_signup_duplicate_email(client):
    response = client.post(
        "/auth/signup",
        json={"name": "Test User 2", "email": "test@example.com", "password": "password123", "is_admin": False}
    )
    assert response.status_code == 400

def test_login(client):
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
