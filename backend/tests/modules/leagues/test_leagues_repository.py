import pytest
from sqlalchemy import create_engine
from datetime import date
from sqlalchemy.orm import sessionmaker

from modules.leagues import repository as repo, models as league_models
from modules.users import models as user_models
from modules.teams import models as team_models
from modules.fantasy_teams import models as fantasy_team_models
from config.database import Base


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)

    # importar modelos relacionados para que las tablas se registren (teams, fantasy_teams, users)
    _ = (
        user_models.User,
        team_models.Team,
        fantasy_team_models.FantasyTeam,
        league_models.Season,
    )
    # crear las tablas en la base de datos de prueba
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    yield session
    session.close()


def test_get_current_season(db_session):
    # crear un usuario para satisfacer las claves foráneas
    user = user_models.User(
        name="Admin",
        email="admin@example.com",
        alias="admin",
        hashed_password="x",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # crear dos seasons y marcar una como actual (usar objetos date de Python)
    s1 = league_models.Season(
        name="Season 2025",
        year=2025,
        week_count=10,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 3, 1),
        is_current=False,
        created_by=user.id,
        cached_weeks=[],
    )
    s2 = league_models.Season(
        name="Season 2026",
        year=2026,
        week_count=12,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 3, 1),
        is_current=True,
        created_by=user.id,
        cached_weeks=[],
    )
    db_session.add_all([s1, s2])
    db_session.commit()

    current = repo.get_current_season(db_session)
    assert current is not None
    assert current.name == "Season 2026"


def test_name_exists(db_session):
    # crear un usuario y una season para asociar la liga
    user = user_models.User(
        name="Admin2",
        email="admin2@example.com",
        alias="admin2",
        hashed_password="x",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    season = league_models.Season(
        name="Season X",
        year=2030,
        week_count=8,
        start_date=date(2030, 1, 1),
        end_date=date(2030, 2, 1),
        is_current=False,
        created_by=user.id,
        cached_weeks=[],
    )
    db_session.add(season)
    db_session.commit()
    db_session.refresh(season)

    # crear una liga
    league = league_models.League(
        name="Alpha League",
        description="test",
        max_teams=8,
        password_hash="hash",
        playoff_format=4,
        created_by=user.id,
        season_id=season.id,
        roster_schema={},
        scoring_schema={},
    )
    db_session.add(league)
    db_session.commit()

    assert repo.name_exists(db_session, "Alpha League") is True
    assert repo.name_exists(db_session, "NonExistent") is False

