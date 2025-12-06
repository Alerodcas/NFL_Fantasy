from types import SimpleNamespace
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.testclient import TestClient

import modules.teams.router as router_mod


def make_app():
    """Create a test FastAPI app with teams router and mocked dependencies."""
    app = FastAPI()
    app.include_router(router_mod.router, prefix="/teams")

    # Override dependencies
    app.dependency_overrides[router_mod.get_db] = lambda: None
    app.dependency_overrides[router_mod.get_current_user] = lambda: SimpleNamespace(id=1, role="admin")
    return app


# ==============================
# Create Team Tests
# ==============================

def test_create_team_json_success(monkeypatch):
    """Test creating a team via JSON payload."""
    app = make_app()
    client = TestClient(app)

    # Mock service to return a team
    fake_team = SimpleNamespace(
        id=10,
        name="Dallas Cowboys",
        city="Dallas",
        image_url="http://example.com/cowboys.png",
        thumbnail_url="/thumb.png",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        created_by=1
    )
    monkeypatch.setattr(router_mod, "service", SimpleNamespace(create_team=lambda db, payload, created_by: fake_team))

    payload = {
        "name": "Dallas Cowboys",
        "city": "Dallas",
        "image_url": "http://example.com/cowboys.png"
    }
    response = client.post("/teams", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 10
    assert data["name"] == "Dallas Cowboys"
    assert data["city"] == "Dallas"


def test_create_team_json_without_image(monkeypatch):
    """Test creating a team without an image."""
    app = make_app()
    client = TestClient(app)

    fake_team = SimpleNamespace(
        id=11,
        name="New York Giants",
        city="New York",
        image_url=None,
        thumbnail_url=None,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        created_by=1
    )
    monkeypatch.setattr(router_mod, "service", SimpleNamespace(create_team=lambda db, payload, created_by: fake_team))

    payload = {"name": "New York Giants", "city": "New York"}
    response = client.post("/teams", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New York Giants"
    assert data["image_url"] is None


def test_create_team_duplicate_name_fails(monkeypatch):
    """Test that creating a team with duplicate name returns 409."""
    app = make_app()
    client = TestClient(app)

    # Mock service to raise ValueError for duplicate
    def failing_create(db, payload, created_by):
        raise ValueError("A team with that name already exists.")

    monkeypatch.setattr(router_mod, "service", SimpleNamespace(create_team=failing_create))

    payload = {"name": "Dallas Cowboys", "city": "Dallas"}
    response = client.post("/teams", json=payload)

    assert response.status_code == 409


def test_create_team_invalid_data_returns_422(monkeypatch):
    """Test that invalid data returns 422."""
    app = make_app()
    client = TestClient(app)

    # Mock service to raise ValueError for validation
    def failing_create(db, payload, created_by):
        raise ValueError("Name and city must be at least 2 characters.")

    monkeypatch.setattr(router_mod, "service", SimpleNamespace(create_team=failing_create))

    payload = {"name": "X", "city": "X"}
    response = client.post("/teams", json=payload)

    assert response.status_code == 422


def test_create_team_upload_success(monkeypatch):
    """Test creating a team by uploading an image file."""
    app = make_app()
    client = TestClient(app)

    # Mock media_repo.save_upload
    monkeypatch.setattr(
        router_mod.media_repo,
        "save_upload",
        lambda file, path: ("/media/cowboys.png", "/media/cowboys_thumb.png")
    )

    # Mock service to return a team with uploaded image
    fake_team = SimpleNamespace(
        id=20,
        name="Philadelphia Eagles",
        city="Philadelphia",
        image_url="/media/eagles.png",
        thumbnail_url="/media/eagles_thumb.png",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        created_by=1
    )
    monkeypatch.setattr(router_mod, "service", SimpleNamespace(create_team=lambda db, payload, created_by: fake_team))

    files = {"image": ("eagles.png", b"fake_image_data", "image/png")}
    data = {"name": "Philadelphia Eagles", "city": "Philadelphia"}
    response = client.post("/teams/upload", files=files, data=data)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 20
    assert body["name"] == "Philadelphia Eagles"


def test_create_team_upload_invalid_image_fails(monkeypatch):
    """Test that uploading invalid image returns 400."""
    app = make_app()
    client = TestClient(app)

    # Mock media_repo.save_upload to raise exception
    monkeypatch.setattr(
        router_mod.media_repo,
        "save_upload",
        lambda file, path: (_ for _ in ()).throw(Exception("Invalid image format"))
    )

    files = {"image": ("invalid.txt", b"not_an_image", "text/plain")}
    data = {"name": "Test Team", "city": "Test City"}
    response = client.post("/teams/upload", files=files, data=data)

    assert response.status_code == 400


# ==============================
# List Teams Tests
# ==============================

def test_list_teams_empty(monkeypatch):
    """Test listing teams when none exist."""
    app = make_app()
    client = TestClient(app)

    monkeypatch.setattr(router_mod, "service", SimpleNamespace(list_teams=lambda db, query, active_only, user_id: []))

    response = client.get("/teams")

    assert response.status_code == 200
    assert response.json() == []


def test_list_teams_success(monkeypatch):
    """Test listing teams successfully."""
    app = make_app()
    client = TestClient(app)

    fake_teams = [
        SimpleNamespace(
            id=1, name="Dallas Cowboys", city="Dallas", image_url=None,
            thumbnail_url=None, is_active=True, created_at=datetime.now(timezone.utc), created_by=1
        ),
        SimpleNamespace(
            id=2, name="Philadelphia Eagles", city="Philadelphia", image_url=None,
            thumbnail_url=None, is_active=True, created_at=datetime.now(timezone.utc), created_by=1
        ),
    ]
    monkeypatch.setattr(router_mod, "service", SimpleNamespace(list_teams=lambda db, query, active_only, user_id: fake_teams))

    response = client.get("/teams")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Dallas Cowboys"


def test_list_teams_filter_by_query(monkeypatch):
    """Test listing teams with query filter."""
    app = make_app()
    client = TestClient(app)

    fake_teams = [
        SimpleNamespace(
            id=1, name="Dallas Cowboys", city="Dallas", image_url=None,
            thumbnail_url=None, is_active=True, created_at=datetime.now(timezone.utc), created_by=1
        )
    ]
    monkeypatch.setattr(router_mod, "service", SimpleNamespace(list_teams=lambda db, query, active_only, user_id: fake_teams))

    response = client.get("/teams?q=Dallas")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Dallas Cowboys"


def test_list_teams_filter_by_active(monkeypatch):
    """Test listing teams filtered by active status."""
    app = make_app()
    client = TestClient(app)

    fake_teams = [
        SimpleNamespace(
            id=1, name="Active Team", city="City", image_url=None,
            thumbnail_url=None, is_active=True, created_at=datetime.now(timezone.utc), created_by=1
        )
    ]
    monkeypatch.setattr(router_mod, "service", SimpleNamespace(list_teams=lambda db, query, active_only, user_id: fake_teams))

    response = client.get("/teams?active=true")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


# ==============================
# Get Team Tests
# ==============================

def test_get_team_success(monkeypatch):
    """Test retrieving a team by ID."""
    app = make_app()
    client = TestClient(app)

    fake_team = SimpleNamespace(
        id=5,
        name="San Francisco 49ers",
        city="San Francisco",
        image_url="/49ers.png",
        thumbnail_url="/49ers_thumb.png",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        created_by=1
    )
    monkeypatch.setattr(router_mod, "service", SimpleNamespace(get_team_by_id=lambda db, team_id: fake_team))

    response = client.get("/teams/5")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 5
    assert data["name"] == "San Francisco 49ers"


def test_get_team_not_found(monkeypatch):
    """Test that getting a nonexistent team returns 404."""
    app = make_app()
    client = TestClient(app)

    monkeypatch.setattr(router_mod, "service", SimpleNamespace(get_team_by_id=lambda db, team_id: None))

    response = client.get("/teams/9999")

    assert response.status_code == 404


# ==============================
# Update Team Tests
# ==============================

def test_update_team_success(monkeypatch):
    """Test updating a team successfully."""
    app = make_app()
    client = TestClient(app)

    fake_team = SimpleNamespace(
        id=3,
        name="Updated Team",
        city="Updated City",
        image_url="/updated.png",
        thumbnail_url=None,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        created_by=1
    )

    # Mock get_by_id
    monkeypatch.setattr(router_mod, "get_by_id", lambda db, team_id: fake_team)

    # Mock service.update_team
    monkeypatch.setattr(router_mod, "service", SimpleNamespace(update_team=lambda db, team, payload: fake_team))

    payload = {"name": "Updated Team", "city": "Updated City", "image_url": "/updated.png"}
    response = client.put("/teams/3", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Team"
    assert data["city"] == "Updated City"


def test_update_team_not_found(monkeypatch):
    """Test updating a nonexistent team returns 404."""
    app = make_app()
    client = TestClient(app)

    monkeypatch.setattr(router_mod, "get_by_id", lambda db, team_id: None)

    payload = {"name": "Updated Team"}
    response = client.put("/teams/9999", json=payload)

    assert response.status_code == 404


def test_update_team_duplicate_name_fails(monkeypatch):
    """Test that updating to a duplicate name returns 409."""
    app = make_app()
    client = TestClient(app)

    fake_team = SimpleNamespace(id=3, name="Team A")
    monkeypatch.setattr(router_mod, "get_by_id", lambda db, team_id: fake_team)

    # Mock service to raise duplicate error
    def failing_update(db, team, payload):
        raise ValueError("A team with that name already exists.")

    monkeypatch.setattr(router_mod, "service", SimpleNamespace(update_team=failing_update))

    payload = {"name": "Team B"}
    response = client.put("/teams/3", json=payload)

    assert response.status_code == 409


def test_update_team_unauthorized(monkeypatch):
    """Test that non-admin users cannot update teams."""
    app = FastAPI()
    app.include_router(router_mod.router, prefix="/teams")

    # Override with non-admin user
    app.dependency_overrides[router_mod.get_db] = lambda: None
    app.dependency_overrides[router_mod.get_current_user] = lambda: SimpleNamespace(id=1, role="user")

    client = TestClient(app)

    payload = {"name": "Updated Team"}
    response = client.put("/teams/3", json=payload)

    assert response.status_code == 403


# ==============================
# Permission Tests
# ==============================

def test_create_team_requires_admin_role(monkeypatch):
    """Test that only admin users can create teams."""
    app = FastAPI()
    app.include_router(router_mod.router, prefix="/teams")

    app.dependency_overrides[router_mod.get_db] = lambda: None
    app.dependency_overrides[router_mod.get_current_user] = lambda: SimpleNamespace(id=1, role="user")

    client = TestClient(app)

    payload = {"name": "Test Team", "city": "Test City"}
    response = client.post("/teams", json=payload)

    assert response.status_code == 403


def test_upload_requires_admin_role(monkeypatch):
    """Test that only admin users can upload team images."""
    app = FastAPI()
    app.include_router(router_mod.router, prefix="/teams")

    app.dependency_overrides[router_mod.get_db] = lambda: None
    app.dependency_overrides[router_mod.get_current_user] = lambda: SimpleNamespace(id=1, role="viewer")

    client = TestClient(app)

    files = {"image": ("test.png", b"data", "image/png")}
    data = {"name": "Test Team", "city": "Test City"}
    response = client.post("/teams/upload", files=files, data=data)

    assert response.status_code == 403
