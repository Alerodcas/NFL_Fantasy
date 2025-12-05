import sys
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime

# Ensure `backend/src` is on sys.path before importing application packages
ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = str(ROOT / "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from fastapi import FastAPI
from fastapi.testclient import TestClient

import modules.leagues.router as router_mod


def make_app():
    app = FastAPI()
    app.include_router(router_mod.router)

    # Override dependencies with simple stubs
    app.dependency_overrides[router_mod.get_db] = lambda: None
    app.dependency_overrides[router_mod.get_current_user] = lambda: SimpleNamespace(id=1)
    return app


def test_search_leagues_validation_no_params():
    app = make_app()
    client = TestClient(app)

    r = client.get("/leagues/search")
    assert r.status_code == 400
    assert "Debe proporcionar al menos un criterio" in r.json().get("detail", "")


def test_search_leagues_name_too_short():
    app = make_app()
    client = TestClient(app)

    r = client.get("/leagues/search", params={"name": "ab"})
    assert r.status_code == 400
    assert "al menos 3 caracteres" in r.json().get("detail", "")


def test_search_leagues_success(monkeypatch):
    app = make_app()
    client = TestClient(app)

    # Prepare a fake service response
    fake_result = [
        {
            "id": 1,
            "uuid": "uuid-1",
            "name": "Liga 1",
            "description": "desc",
            "status": "pre_draft",
            "max_teams": 8,
            "season_id": 1,
            "season_name": "S2025",
            "slots_available": 3,
            "created_at": datetime.utcnow().isoformat(),
        }
    ]

    monkeypatch.setattr(router_mod, "svc_search_leagues", lambda db, filters: fake_result)

    r = client.get("/leagues/search", params={"name": "Liga"})
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert body[0]["name"] == "Liga 1"


def test_create_league_success(monkeypatch):
    app = make_app()
    client = TestClient(app)

    # Mock the service to return fake league and team
    fake_league = SimpleNamespace(
        id=10,
        uuid="uuid-10",
        name="LigaTest",
        status="pre_draft",
        max_teams=8,
        playoff_format=4,
        allow_decimal_scoring=True,
        season_id=1,
    )
    fake_team = SimpleNamespace(id=99)

    monkeypatch.setattr(router_mod, "create_league_with_commissioner_team", lambda **kwargs: (fake_league, fake_team))
    monkeypatch.setattr(router_mod.audit, "log_event", lambda *args, **kwargs: None)

    payload = {
        "name": "LigaTest",
        "description": "desc",
        "max_teams": 8,
        "password": "Abcdef12",
        "playoff_format": 4,
        "allow_decimal_scoring": True,
        "fantasy_team": {"name": "TeamOne"},
    }

    r = client.post("/leagues", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 10
    assert body["commissioner_team_id"] == 99


def test_join_league_success(monkeypatch):
    app = make_app()
    client = TestClient(app)

    # Fake member returned by the service
    fake_member = SimpleNamespace(league_id=5, fantasy_team_id=55, user_alias="mi_alias", joined_at=datetime.utcnow())
    monkeypatch.setattr(router_mod, "svc_join_league", lambda **kwargs: fake_member)
    monkeypatch.setattr(router_mod.audit, "log_event", lambda *args, **kwargs: None)

    payload = {
        "password": "Abcdef12",
        "user_alias": "mi_alias",
        "fantasy_team": {"name": "EquipoX"},
    }

    r = client.post("/leagues/5/join", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["league_id"] == 5
    assert body["team_id"] == 55


def test_upload_fantasy_team_image(monkeypatch):
    app = make_app()
    client = TestClient(app)

    # Mock media_repo.save_upload
    monkeypatch.setattr(router_mod.media_repo, "save_upload", lambda file, path: ("/media/img.png", "/media/thumb.png"))

    files = {"image": ("img.png", b"abc", "image/png")}
    r = client.post("/leagues/fantasy-team/upload", files=files)
    assert r.status_code == 201
    body = r.json()
    assert body["image_url"] == "/media/img.png"
