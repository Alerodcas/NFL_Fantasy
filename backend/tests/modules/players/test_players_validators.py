import pytest
import io
import json
from datetime import datetime, date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from modules.players import validators as val
from modules.players import models as player_models
from modules.teams import models as team_models
from modules.users import models as user_models
from modules.leagues import models as league_models
from modules.fantasy_teams import models as fantasy_team_models
from config.database import Base
from helpers.factories import create_user, create_team, create_player, create_season, create_league, create_fantasy_team


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)

    # Registrar modelos involucrados en las comprobaciones de los validadores
    _ = (
        user_models.User,
        team_models.Team,
        league_models.Season,
        league_models.League,
        fantasy_team_models.FantasyTeam,
        player_models.Player,
        player_models.PlayerNews,
    )
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


def test_validate_single_player_success(db_session):
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id)

    payload = {"name": "  Alice ", "position": "wr", "team_id": team.id, "image_url": "/img.png"}
    out = val.validate_single_player(db_session, payload=payload)

    assert out["name"] == "Alice"
    assert out["position"] == "WR"
    assert out["team_id"] == team.id


def test_validate_single_player_errors(db_session):
    # campos faltantes
    with pytest.raises(ValueError) as exc:
        val.validate_single_player(db_session, payload={})
    assert "Name is required" in str(exc.value)

    # nombre corto y posición inválida
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id)
    payload = {"name": "A", "position": "XX", "team_id": team.id, "image_url": "/img.png"}
    with pytest.raises(ValueError) as exc2:
        val.validate_single_player(db_session, payload=payload)
    assert "Name must be at least 2 characters" in str(exc2.value)
    assert "Invalid position" in str(exc2.value)


def test_validate_players_batch_success_and_duplicate(db_session):
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id, name="Team A")

    data = [
        {"name": "Bob", "position": "RB", "team": "Team A", "image": "/img1.png"},
    ]
    out = val.validate_players_batch(db_session, data=data)
    assert isinstance(out, list)
    assert out[0]["name"] == "Bob"

    # Duplicado dentro del archivo
    data_dup = [
        {"name": "Bob", "position": "RB", "team": "Team A", "image": "/img1.png"},
        {"name": " Bob ", "position": "rb", "team": "Team A", "image": "/img2.png"},
    ]
    with pytest.raises(ValueError) as exc:
        val.validate_players_batch(db_session, data=data_dup)
    assert "duplicated inside the file" in str(exc.value)


def test_validate_players_batch_missing_and_invalid(db_session):
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id, name="Team B")

    data = [
        {"name": "", "position": "RB", "team": "Team B", "image": "/img.png"},
        {"name": "Cathy", "position": "XX", "team": "Team B", "image": "/img.png"},
    ]
    with pytest.raises(ValueError) as exc:
        val.validate_players_batch(db_session, data=data)
    msg = str(exc.value)
    assert "missing field 'name'" in msg
    assert "invalid position" in msg.lower()


def test_validate_player_news_success_and_errors(db_session):
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id)
    player = create_player(db_session, name="P1", position="QB", created_by=user.id, team_id=team.id)

    good = {
        "player_id": player.id,
        "summary": "Hello",
        "text": "This is more than ten chars",
        "is_injury": True,
        "injury_type": "D",
    }
    out = val.validate_player_news(db_session, good)
    assert out["player_id"] == player.id
    assert out["is_injury"] is True

    # jugador faltante
    bad = {"player_id": 9999, "summary": "s", "text": "too short"}
    with pytest.raises(ValueError) as exc:
        val.validate_player_news(db_session, bad)
    assert "Player not found" in str(exc.value) or "player_id is required" in str(exc.value)

    # jugador inactivo
    player2 = create_player(db_session, name="P2", position="RB", created_by=user.id, team_id=team.id)
    player2.is_active = False
    db_session.commit()
    bad2 = {"player_id": player2.id, "summary": "s", "text": "This is more than ten", "is_injury": False}
    with pytest.raises(ValueError) as exc2:
        val.validate_player_news(db_session, bad2)
    assert "Player is not active" in str(exc2.value)

    # lesión sin tipo
    bad3 = {"player_id": player.id, "summary": "ok", "text": "This is more than ten", "is_injury": True}
    with pytest.raises(ValueError) as exc3:
        val.validate_player_news(db_session, bad3)
    assert "injury_type is required" in str(exc3.value)
