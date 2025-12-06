from types import SimpleNamespace
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.testclient import TestClient

import modules.users.router as router_mod


def make_app():
    """Create a test FastAPI app with users router and mocked dependencies."""
    app = FastAPI()
    app.include_router(router_mod.router, prefix="/users")

    # Override dependencies
    app.dependency_overrides[router_mod.get_db] = lambda: None
    return app


# ==============================
# Register Tests
# ==============================

def test_register_user_success(monkeypatch):
    """Test successful user registration."""
    app = make_app()
    client = TestClient(app)

    # Mock service to return a user
    fake_user = SimpleNamespace(
        id=10,
        name="John Doe",
        email="john@example.com",
        alias="johndoe",
        role="manager",
        account_status="active"
    )
    monkeypatch.setattr(router_mod, "service", SimpleNamespace(register_user=lambda db, user: fake_user))

    # Mock audit logging
    monkeypatch.setattr(router_mod, "audit", SimpleNamespace(log_event=lambda **kwargs: None))

    payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "alias": "johndoe",
        "password": "Pass1234"
    }
    response = client.post("/users/register/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"


def test_register_user_duplicate_email_fails(monkeypatch):
    """Test that duplicate email registration fails."""
    app = make_app()
    client = TestClient(app)

    def failing_register(db, user):
        raise ValueError("Email already registered")

    monkeypatch.setattr(router_mod, "service", SimpleNamespace(register_user=failing_register))
    monkeypatch.setattr(router_mod, "audit", SimpleNamespace(log_event=lambda **kwargs: None))

    payload = {
        "name": "John Doe",
        "email": "duplicate@example.com",
        "alias": "johndoe",
        "password": "Pass1234"
    }
    response = client.post("/users/register/", json=payload)

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_register_user_invalid_password_too_short(monkeypatch):
    """Test that invalid password is rejected."""
    app = make_app()
    client = TestClient(app)

    payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "alias": "johndoe",
        "password": "Short1"  # Less than 8 characters
    }
    response = client.post("/users/register/", json=payload)

    assert response.status_code == 422  # Validation error


def test_register_user_invalid_email_format(monkeypatch):
    """Test that invalid email format is rejected."""
    app = make_app()
    client = TestClient(app)

    payload = {
        "name": "John Doe",
        "email": "invalid-email",  # Not a valid email
        "alias": "johndoe",
        "password": "Pass1234"
    }
    response = client.post("/users/register/", json=payload)

    assert response.status_code == 422


# ==============================
# Login Tests
# ==============================

def test_login_success(monkeypatch):
    """Test successful user login."""
    app = make_app()
    client = TestClient(app)

    fake_user = SimpleNamespace(
        id=5,
        email="user@example.com",
        name="Test User"
    )

    monkeypatch.setattr(
        router_mod, "service",
        SimpleNamespace(
            authenticate_user=lambda db, email, password: fake_user,
            create_access_token_for_user=lambda user: "fake_token_jwt"
        )
    )
    monkeypatch.setattr(router_mod, "audit", SimpleNamespace(log_event=lambda **kwargs: None))

    response = client.post(
        "/users/token",
        data={"username": "user@example.com", "password": "Pass1234"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "fake_token_jwt"
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials_fails(monkeypatch):
    """Test that login fails with invalid credentials."""
    app = make_app()
    client = TestClient(app)

    def failing_auth(db, email, password):
        raise PermissionError("Invalid credentials")

    monkeypatch.setattr(
        router_mod, "service",
        SimpleNamespace(authenticate_user=failing_auth)
    )
    monkeypatch.setattr(router_mod.crud, "get_user_by_email", lambda db, email: None)
    monkeypatch.setattr(router_mod, "audit", SimpleNamespace(log_event=lambda **kwargs: None))

    response = client.post(
        "/users/token",
        data={"username": "user@example.com", "password": "WrongPass"}
    )

    assert response.status_code == 401


def test_login_account_blocked_fails(monkeypatch):
    """Test that login fails for blocked account."""
    app = make_app()
    client = TestClient(app)

    fake_user = SimpleNamespace(id=5, email="blocked@example.com")

    def failing_auth(db, email, password):
        raise PermissionError("Account locked due to too many failed attempts")

    monkeypatch.setattr(
        router_mod, "service",
        SimpleNamespace(authenticate_user=failing_auth)
    )
    monkeypatch.setattr(
        router_mod.crud,
        "get_user_by_email",
        lambda db, email: fake_user
    )
    monkeypatch.setattr(router_mod, "audit", SimpleNamespace(log_event=lambda **kwargs: None))

    response = client.post(
        "/users/token",
        data={"username": "blocked@example.com", "password": "Test1234"}
    )

    assert response.status_code == 400  # Bad request or account locked


# ==============================
# Current User Tests
# ==============================

def test_get_current_user_success(monkeypatch):
    """Test getting current user from token."""
    app = make_app()
    client = TestClient(app)

    fake_user = SimpleNamespace(
        id=10,
        name="John Doe",
        email="john@example.com",
        alias="johndoe",
        role="manager",
        account_status="active"
    )

    # Mock get_current_user dependency
    app.dependency_overrides[router_mod.get_current_user] = lambda: fake_user

    # Create a simple endpoint that uses get_current_user
    @app.get("/test-auth")
    def test_endpoint(current_user = router_mod.Depends(router_mod.get_current_user)):
        return {"user_id": current_user.id, "email": current_user.email}

    response = client.get("/test-auth")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 10
    assert data["email"] == "john@example.com"


# ==============================
# Input Validation Tests
# ==============================

def test_register_missing_required_field(monkeypatch):
    """Test that missing required fields are rejected."""
    app = make_app()
    client = TestClient(app)

    payload = {
        "name": "John Doe",
        # Missing email
        "alias": "johndoe",
        "password": "SecurePass123"
    }
    response = client.post("/users/register/", json=payload)

    assert response.status_code == 422


def test_register_empty_name_rejected(monkeypatch):
    """Test that empty name is rejected."""
    app = make_app()
    client = TestClient(app)

    payload = {
        "name": "",  # Empty string
        "email": "john@example.com",
        "alias": "johndoe",
        "password": "SecurePass123"
    }
    response = client.post("/users/register/", json=payload)

    assert response.status_code == 422


def test_register_password_too_long_rejected(monkeypatch):
    """Test that password longer than 12 chars is rejected."""
    app = make_app()
    client = TestClient(app)

    payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "alias": "johndoe",
        "password": "ThisPasswordIsTooLong123"  # More than 12 chars
    }
    response = client.post("/users/register/", json=payload)

    assert response.status_code == 422
