import pytest
from pydantic import ValidationError

from modules.teams import service as svc, schemas
from helpers.factories import create_user, create_team


# ==============================
# Create Team Tests
# ==============================

def test_create_team_success(monkeypatch, db_session):
    """Test successful team creation."""
    user = create_user(db_session)

    # Mock try_download_and_thumb to return a thumbnail URL
    monkeypatch.setattr(svc, "try_download_and_thumb", lambda url, subdir=None: "/thumb.png")

    payload = schemas.TeamCreate(
        name="  Dallas Cowboys  ",
        city="  Dallas  ",
        image_url="http://example.com/cowboys.png"
    )

    team = svc.create_team(db_session, payload=payload, created_by=user.id)

    assert team.id is not None
    assert team.name == "Dallas Cowboys"  # Whitespace stripped
    assert team.city == "Dallas"
    assert team.image_url == "http://example.com/cowboys.png"
    assert team.thumbnail_url == "/thumb.png"
    assert team.is_active is True
    assert team.created_by == user.id


def test_create_team_without_image(db_session):
    """Test creating a team without an image."""
    user = create_user(db_session)

    payload = schemas.TeamCreate(
        name="New York Giants",
        city="New York",
        image_url=None
    )

    team = svc.create_team(db_session, payload=payload, created_by=user.id)

    assert team.id is not None
    assert team.name == "New York Giants"
    assert team.image_url is None
    assert team.thumbnail_url is None


def test_create_team_name_too_short(db_session):
    """Test that creating a team with name < 2 chars fails at Pydantic validation."""
    user = create_user(db_session)

    # Pydantic validation will raise ValidationError before the service is even called
    with pytest.raises(ValidationError):
        schemas.TeamCreate(name="X", city="City", image_url=None)


def test_create_team_city_too_short(db_session):
    """Test that creating a team with city < 2 chars fails at Pydantic validation."""
    user = create_user(db_session)

    # Pydantic validation will raise ValidationError before the service is even called
    with pytest.raises(ValidationError):
        schemas.TeamCreate(name="Team", city="X", image_url=None)


def test_create_team_duplicate_name_case_insensitive(db_session):
    """Test that duplicate team names are rejected (case-insensitive)."""
    user = create_user(db_session)

    # Create first team
    payload1 = schemas.TeamCreate(name="Dallas Cowboys", city="Dallas", image_url=None)
    svc.create_team(db_session, payload=payload1, created_by=user.id)

    # Try to create duplicate with different case
    payload2 = schemas.TeamCreate(name="DALLAS COWBOYS", city="Dallas", image_url=None)
    with pytest.raises(ValueError, match="already exists"):
        svc.create_team(db_session, payload=payload2, created_by=user.id)


# ==============================
# Update Team Tests
# ==============================

def test_update_team_name(db_session):
    """Test updating a team's name."""
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id, name="Original", city="City")

    payload = schemas.TeamUpdate(name="Updated Name", city=None, image_url=None, is_active=None)
    updated = svc.update_team(db_session, team, payload=payload)

    assert updated.name == "Updated Name"
    assert updated.city == "City"  # Unchanged


def test_update_team_city(db_session):
    """Test updating a team's city."""
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id, name="Team", city="Original City")

    payload = schemas.TeamUpdate(name=None, city="New City", image_url=None, is_active=None)
    updated = svc.update_team(db_session, team, payload=payload)

    assert updated.city == "New City"
    assert updated.name == "Team"  # Unchanged


def test_update_team_image_url(db_session):
    """Test updating a team's image URL."""
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id, name="Team", city="City")

    payload = schemas.TeamUpdate(name=None, city=None, image_url="/new-image.png", is_active=None)
    updated = svc.update_team(db_session, team, payload=payload)

    assert updated.image_url == "/new-image.png"


def test_update_team_is_active(db_session):
    """Test updating a team's active status."""
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id, name="Team", city="City")

    payload = schemas.TeamUpdate(name=None, city=None, image_url=None, is_active=False)
    updated = svc.update_team(db_session, team, payload=payload)

    assert updated.is_active is False


def test_update_team_duplicate_name_fails(db_session):
    """Test that updating to a duplicate name (case-insensitive) fails."""
    user = create_user(db_session)
    team1 = create_team(db_session, created_by=user.id, name="Team A", city="City A")
    team2 = create_team(db_session, created_by=user.id, name="Team B", city="City B")

    # Try to rename Team B to Team A
    payload = schemas.TeamUpdate(name="TEAM A", city=None, image_url=None, is_active=None)
    with pytest.raises(ValueError, match="already exists"):
        svc.update_team(db_session, team2, payload=payload)


def test_update_team_duplicate_name_same_team_allowed(db_session):
    """Test that updating a team to the same name is allowed."""
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id, name="Dallas Cowboys", city="Dallas")

    # Update to same name (different case) should work
    payload = schemas.TeamUpdate(name="DALLAS COWBOYS", city=None, image_url=None, is_active=None)
    updated = svc.update_team(db_session, team, payload=payload)

    assert updated.name == "DALLAS COWBOYS"


def test_update_team_multiple_fields(db_session):
    """Test updating multiple fields at once."""
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id, name="Original", city="Original City")

    payload = schemas.TeamUpdate(
        name="New Name",
        city="New City",
        image_url="/new.png",
        is_active=False
    )
    updated = svc.update_team(db_session, team, payload=payload)

    assert updated.name == "New Name"
    assert updated.city == "New City"
    assert updated.image_url == "/new.png"
    assert updated.is_active is False


# ==============================
# List Teams Tests
# ==============================

def test_list_teams_empty(db_session):
    """Test listing teams when none exist."""
    teams = svc.list_teams(db_session)
    assert teams == []


def test_list_teams_all(db_session):
    """Test listing all teams."""
    user = create_user(db_session)
    create_team(db_session, created_by=user.id, name="Team A", city="City A")
    create_team(db_session, created_by=user.id, name="Team B", city="City B")
    create_team(db_session, created_by=user.id, name="Team C", city="City C")

    teams = svc.list_teams(db_session)
    assert len(teams) == 3


def test_list_teams_filter_by_query(db_session):
    """Test listing teams with query filter."""
    user = create_user(db_session)
    create_team(db_session, created_by=user.id, name="Dallas Cowboys", city="Dallas")
    create_team(db_session, created_by=user.id, name="Philadelphia Eagles", city="Philadelphia")

    teams = svc.list_teams(db_session, query="Dallas")
    assert len(teams) == 1
    assert teams[0].name == "Dallas Cowboys"


def test_list_teams_filter_by_active_only(db_session):
    """Test listing only active teams."""
    user = create_user(db_session)
    team1 = create_team(db_session, created_by=user.id, name="Active Team", city="City")
    team2 = create_team(db_session, created_by=user.id, name="Inactive Team", city="City")

    # Deactivate second team
    from modules.teams import repository
    repository.update_team(db_session, team2, is_active=False)

    teams = svc.list_teams(db_session, active_only=True)
    assert len(teams) == 1
    assert teams[0].name == "Active Team"


def test_list_teams_filter_by_user_id(db_session):
    """Test listing teams created by specific user."""
    user1 = create_user(db_session, email="user1@example.com")
    user2 = create_user(db_session, email="user2@example.com")

    create_team(db_session, created_by=user1.id, name="User1 Team", city="City")
    create_team(db_session, created_by=user2.id, name="User2 Team", city="City")

    user1_teams = svc.list_teams(db_session, user_id=user1.id)
    assert len(user1_teams) == 1
    assert user1_teams[0].created_by == user1.id


def test_get_team_by_id_success(db_session):
    """Test retrieving a team by ID."""
    user = create_user(db_session)
    team = create_team(db_session, created_by=user.id, name="Team", city="City")

    fetched = svc.get_team_by_id(db_session, team.id)
    assert fetched is not None
    assert fetched.id == team.id


def test_get_team_by_id_nonexistent(db_session):
    """Test retrieving a nonexistent team returns None."""
    fetched = svc.get_team_by_id(db_session, 9999)
    assert fetched is None
