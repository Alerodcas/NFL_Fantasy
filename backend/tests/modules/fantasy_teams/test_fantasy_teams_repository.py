import pytest

from modules.fantasy_teams import repository, models


@pytest.fixture
def sample_team(db_session):
    """Inserta un equipo de prueba."""
    team = models.FantasyTeam(
        name="Los Tigres",
        image_url=None,
        thumbnail_url=None,
        is_active=True,
        user_id=1,
        league_id=7,
    )
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)
    return team


# -----------------------
# TESTS
# -----------------------

def test_get_by_id(db_session, sample_team):
    result = repository.get_by_id(db_session, sample_team.id)
    assert result is not None
    assert result.id == sample_team.id


def test_get_by_name_in_league_ci(db_session, sample_team):
    result = repository.get_by_name_in_league_ci(
        db_session, league_id=7, name="   LOS TIGRES   "
    )
    assert result is not None
    assert result.id == sample_team.id


def test_list_by_league(db_session, sample_team):
    results = repository.list_by_league(db_session, league_id=7)
    assert len(results) == 1
    assert results[0].id == sample_team.id


def test_create_fantasy_team(db_session):
    team = repository.create_fantasy_team(
        db_session,
        name="Sharks",
        image_url="img.png",
        thumbnail_url="thumb.png",
        user_id=2,
        league_id=7,
    )

    assert team.id is not None
    assert team.name == "Sharks"
    assert team.league_id == 7

    # Verificar que sí quedó en la DB
    saved = db_session.get(models.FantasyTeam, team.id)
    assert saved is not None


