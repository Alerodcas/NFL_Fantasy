from types import SimpleNamespace
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.testclient import TestClient

import modules.players.router as router_mod


def make_app():
    app = FastAPI()
    # Montar el router de players bajo el prefijo /players como lo hace la app real
    app.include_router(router_mod.router, prefix="/players")

    # Sobrescribir dependencias
    app.dependency_overrides[router_mod.get_db] = lambda: None
    # El usuario actual debe ser admin para estos endpoints
    app.dependency_overrides[router_mod.get_current_user] = lambda: SimpleNamespace(id=1, role="admin")
    return app


def test_create_player_json_success(monkeypatch):
    app = make_app()
    client = TestClient(app)

    # validators.validate_single_player debe devolver un dict validado
    monkeypatch.setattr(router_mod, "validators", SimpleNamespace(validate_single_player=lambda db, payload: payload))

    fake_player = SimpleNamespace(
        id=11,
        name="John",
        position="QB",
        team_id=2,
        image_url="/img.png",
        thumbnail_url=None,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        created_by=1,
    )
    monkeypatch.setattr(router_mod, "service", SimpleNamespace(create_player=lambda db, payload, created_by: fake_player))

    # stub de commit_and_refresh que no hace nada
    monkeypatch.setattr(router_mod, "commit_and_refresh", lambda db, obj: None)

    payload = {"name": "John", "position": "QB", "team_id": 2, "image_url": "/img.png"}
    r = client.post("/players", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 11
    assert body["name"] == "John"


def test_create_player_upload_success(monkeypatch):
    app = make_app()
    client = TestClient(app)

    # validators debe aceptar archivo subido
    monkeypatch.setattr(router_mod, "validators", SimpleNamespace(validate_single_player=lambda db, payload, uploaded_file=None: payload))

    # media_repo debe guardar el archivo y devolver URLs
    monkeypatch.setattr(router_mod.media_repo, "save_player_upload", lambda file: ("/media/img.png", "/media/thumb.png"))

    fake_player = SimpleNamespace(
        id=20,
        name="Uploaded",
        position="WR",
        team_id=3,
        image_url="/media/img.png",
        thumbnail_url="/media/thumb.png",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        created_by=1,
    )
    monkeypatch.setattr(router_mod, "service", SimpleNamespace(create_player=lambda db, payload, created_by, thumbnail_url=None: fake_player))
    monkeypatch.setattr(router_mod, "commit_and_refresh", lambda db, obj: None)

    files = {
        "image": ("img.png", b"abc", "image/png"),
    }
    data = {"name": "Uploaded", "position": "WR", "team_id": "3"}
    r = client.post("/players/upload", data=data, files=files)
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 20
    assert body["image_url"] == "/media/img.png"


def test_batch_upload_validation_and_success(monkeypatch):
    app = make_app()
    client = TestClient(app)

    # Un nombre de archivo no-json debe devolver 400
    files = {"file": ("players.txt", b"[]", "application/json")}
    r = client.post("/players/batch-upload", files=files)
    assert r.status_code == 400

    # Ahora archivo json válido y el servicio devuelve la lista creada
    monkeypatch.setattr(router_mod, "service", SimpleNamespace(process_players_batch=lambda db, file, created_by: {"created": [1,2,3]}))
    monkeypatch.setattr(router_mod, "commit", lambda db: None)

    files = {"file": ("players.json", b"[]", "application/json")}
    r = client.post("/players/batch-upload", files=files)
    assert r.status_code == 200
    body = r.json()
    assert "creados" in body["message"] or "jugadores" in body["message"]
