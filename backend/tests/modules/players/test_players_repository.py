import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from modules.players import repository as repo, models as player_models
from modules.users import models as user_models
from modules.teams import models as team_models
from helpers.factories import create_user, create_team
from modules.leagues import models as league_models
from modules.fantasy_teams import models as fantasy_team_models
from config.database import Base


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)

    # Import related models so metadata includes required tables
    _ = (
        user_models.User,
        team_models.Team,
        league_models.League,
        league_models.LeagueMember,
        fantasy_team_models.FantasyTeam,
        player_models.Player,
        player_models.PlayerNews,
    )

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    yield session
    session.close()


# Use centralized factories


def test_create_and_get_player(db_session):
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id)

    p = repo.create_player(
        db_session,
        name="John Doe",
        position="QB",
        image_url=None,
        thumbnail_url=None,
        created_by=user.id,
        team_id=team.id,
    )

    assert p.id is not None

    fetched = repo.get_by_id(db_session, p.id)
    assert fetched is not None
    assert fetched.name == "John Doe"


def test_get_by_name_ci_for_team_and_list(db_session):
    user = create_user(db_session, email="a@example.com")
    team = create_team(db_session, created_by=user.id)

    repo.create_player(db_session, name="Alice", position="WR", image_url=None, thumbnail_url=None, created_by=user.id, team_id=team.id)
    repo.create_player(db_session, name="bob", position="RB", image_url=None, thumbnail_url=None, created_by=user.id, team_id=team.id)
    repo.create_player(db_session, name="charlie", position="TE", image_url=None, thumbnail_url=None, created_by=user.id, team_id=team.id)

    found = repo.get_by_name_ci_for_team(db_session, team_id=team.id, name="  ALICE  ")
    assert found is not None
    assert found.name.lower() == "alice"

    players = repo.list_players_by_team(db_session, team_id=team.id)
    # Should be ordered by name (Alice, bob, charlie)
    assert [p.name.lower() for p in players] == ["alice", "bob", "charlie"]


def test_news_crud_and_latest(db_session):
    user = create_user(db_session, email="n@example.com")
    team = create_team(db_session, created_by=user.id)

    player = repo.create_player(db_session, name="NewsPlayer", position="RB", image_url=None, thumbnail_url=None, created_by=user.id, team_id=team.id)

    now = datetime.utcnow()
    older = now - timedelta(minutes=10)

    n1 = player_models.PlayerNews(player_id=player.id, author_id=user.id, summary="S1", text="T1", created_at=older)
    n2 = player_models.PlayerNews(player_id=player.id, author_id=user.id, summary="S2", text="T2", created_at=now)

    repo.create_news(db_session, news=n1)
    repo.create_news(db_session, news=n2)

    news_list = repo.list_news_for_player(db_session, player_id=player.id)
    assert len(news_list) == 2
    # list_news_for_player orders by created_at desc
    assert news_list[0].summary == "S2"

    latest = repo.get_latest_news_for_player(db_session, player_id=player.id)
    assert latest is not None
    assert latest.summary == "S2"
