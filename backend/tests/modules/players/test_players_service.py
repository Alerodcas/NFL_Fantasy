import io
import json
from datetime import datetime

import pytest

from modules.players import service as svc
from modules.players import schemas as schemas
from helpers.factories import create_user, create_team


def test_create_player_assigns_thumbnail_when_image(monkeypatch, db_session):
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id)

    # Parchear try_download_and_thumb para devolver una URL de thumbnail
    # Parchear try_download_and_thumb para devolver una URL de thumbnail
    monkeypatch.setattr(svc, "try_download_and_thumb", lambda url, subdir=None: "/thumb.png")

    payload = schemas.PlayerCreate(name="  John  ", position="QB", team_id=team.id, image_url="http://img")
    player = svc.create_player(db_session, payload=payload, created_by=user.id)

    # flush para asignar PKs si es necesario (no requerido para aserciones de atributos)
    # flush para asignar PKs si es necesario (no requerido para aserciones de atributos)
    db_session.flush()

    assert player.name == "John"
    assert player.thumbnail_url == "/thumb.png"
    assert player.image_url == "http://img"
    assert player.team_id == team.id


def test_process_players_batch_success(monkeypatch, db_session):
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id)

    # Preparar entrada de ejemplo y validadores
    # Preparar entrada de ejemplo y validadores
    sample = [{"name": "P1", "position": "RB", "team_id": team.id, "image_url": None}]
    fileobj = io.BytesIO(json.dumps(sample).encode("utf-8"))

    # validators.validate_players_batch devuelve una lista de dicts (elementos validados)
    # validators.validate_players_batch devuelve una lista de dicts (elementos validados)
    monkeypatch.setattr(svc, "validators", type("V", (), {"validate_players_batch": staticmethod(lambda db, data: data)}))

    saved = {}
    def fake_save_processed_copy(content, path, prefix=""):
        saved["last"] = {"content": content, "prefix": prefix}

    monkeypatch.setattr(svc, "save_processed_copy", fake_save_processed_copy)

    res = svc.process_players_batch(db_session, file=fileobj, created_by=user.id)
    assert "created" in res
    assert res["created"] == ["P1"]
    assert saved.get("last", {}).get("prefix") == "approved"


def test_process_players_batch_malformed_json_calls_rejected_save(monkeypatch, db_session):
    fileobj = io.BytesIO(b"not-json")

    called = {}
    def fake_save_processed_copy(content, path, prefix=""):
        called["prefix"] = prefix

    monkeypatch.setattr(svc, "save_processed_copy", fake_save_processed_copy)

    with pytest.raises(ValueError):
        svc.process_players_batch(db_session, file=fileobj, created_by=1)

    assert called.get("prefix") == "rejected"


def test_create_player_news_updates_player_visible_designation(monkeypatch, db_session):
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id)
    player = player_models.Player(name="PN", position="RB", image_url=None, thumbnail_url=None, is_active=True, created_by=user.id, team_id=team.id)
    db_session.add(player)
    db_session.commit()
    db_session.refresh(player)

    # Preparar un dict validado que validators.validate_player_news devolvería
    # Preparar un dict validado que validators.validate_player_news devolvería
    validated = {
        "player_id": player.id,
        "summary": " s ",
        "text": " long text of news ",
        "is_injury": True,
        "injury_type": "D",
        "update_state": True,
    }

    monkeypatch.setattr(svc, "validators", type("V", (), {"validate_player_news": staticmethod(lambda db, payload: validated)}))
    # repository.get_by_id debe devolver la instancia del jugador
    # repository.get_by_id debe devolver la instancia del jugador
    monkeypatch.setattr(svc, "repository", type("R", (), {"get_by_id": staticmethod(lambda db, player_id: db.get(player_models.Player, player_id))}))

    payload = schemas.PlayerNewsCreate(**{
        "player_id": player.id,
        "summary": " s ",
        "text": " long text of news ",
        "is_injury": True,
        "injury_type": "D",
        "update_state": True,
    })

    news = svc.create_player_news(db_session, payload=payload, author_id=user.id)

    # la noticia fue añadida a la sesión
    # la noticia fue añadida a la sesión
    assert news.summary == "s"
    # designación visible del jugador actualizada
    # designación visible del jugador actualizada
    assert getattr(player, "visible_designation", None) == "D"
    assert getattr(player, "visible_designation_updated_at", None) is not None
