NEW_USER = {
    "email": "new@example.com",
    "username": "newuser",
    "name": "New User",
    "password": "correct-horse",
}


def test_health_check(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "CogniCortex"}


def test_signup_returns_user_without_password(client):
    response = client.post("/api/v1/users", json=NEW_USER)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == NEW_USER["email"]
    assert "password" not in body
    assert "hashed_password" not in body


def test_login_returns_bearer_token(register_and_login):
    headers = register_and_login()

    assert headers["Authorization"].startswith("Bearer ")


def test_login_rejects_wrong_password(client, register_and_login):
    register_and_login(email="owner@example.com", password="correct-horse")

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "owner@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_protected_route_requires_token(client):
    response = client.get("/api/v1/workflows")

    assert response.status_code == 401


def test_duplicate_signup_returns_conflict(client):
    client.post("/api/v1/users", json=NEW_USER)

    response = client.post("/api/v1/users", json=NEW_USER)

    assert response.status_code == 409
