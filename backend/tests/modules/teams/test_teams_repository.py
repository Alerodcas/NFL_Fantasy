import pytest
from modules.teams import repository as repo
from modules.users import models as user_models


# ==============================
# CRUD Tests
# ==============================

def test_create_team(db_session, test_user):
    """Test creating a team."""
    team = repo.create_team(
        db_session,
        name="Dallas Cowboys",
        city="Dallas",
        image_url="/media/cowboys.png",
        thumbnail_url="/media/cowboys_thumb.png",
        created_by=test_user.id
    )

    assert team.id is not None
    assert team.name == "Dallas Cowboys"
    assert team.city == "Dallas"
    assert team.image_url == "/media/cowboys.png"
    assert team.thumbnail_url == "/media/cowboys_thumb.png"
    assert team.is_active is True
    assert team.created_by == test_user.id


def test_get_by_id(db_session, test_user):
    """Test retrieving a team by ID."""
    created = repo.create_team(
        db_session,
        name="New York Giants",
        city="New York",
        image_url=None,
        thumbnail_url=None,
        created_by=test_user.id
    )

    fetched = repo.get_by_id(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "New York Giants"
    assert fetched.city == "New York"


def test_get_by_id_nonexistent(db_session):
    """Test getting a team that doesn't exist returns None."""
    result = repo.get_by_id(db_session, 9999)
    assert result is None


def test_get_by_name_ci(db_session, test_user):
    """Test case-insensitive name search."""
    repo.create_team(
        db_session,
        name="San Francisco 49ers",
        city="San Francisco",
        image_url=None,
        thumbnail_url=None,
        created_by=test_user.id
    )

    # Test various case combinations
    found_lower = repo.get_by_name_ci(db_session, "san francisco 49ers")
    assert found_lower is not None
    assert found_lower.name == "San Francisco 49ers"

    found_upper = repo.get_by_name_ci(db_session, "SAN FRANCISCO 49ERS")
    assert found_upper is not None
    assert found_upper.name == "San Francisco 49ers"

    # Note: get_by_name_ci does case-insensitive comparison but doesn't strip whitespace
    found_mixed = repo.get_by_name_ci(db_session, "SaN FrAnCiScO 49eRs")
    assert found_mixed is not None
    assert found_mixed.name == "San Francisco 49ers"


def test_get_by_name_ci_nonexistent(db_session):
    """Test case-insensitive search returns None for nonexistent team."""
    result = repo.get_by_name_ci(db_session, "Nonexistent Team")
    assert result is None


def test_update_team_all_fields(db_session, test_user):
    """Test updating all fields of a team."""
    team = repo.create_team(
        db_session,
        name="Original Name",
        city="Original City",
        image_url="/original.png",
        thumbnail_url=None,
        created_by=test_user.id
    )

    updated = repo.update_team(
        db_session,
        team,
        name="Updated Name",
        city="Updated City",
        image_url="/updated.png",
        is_active=False
    )

    assert updated.id == team.id
    assert updated.name == "Updated Name"
    assert updated.city == "Updated City"
    assert updated.image_url == "/updated.png"
    assert updated.is_active is False


def test_update_team_partial_fields(db_session, test_user):
    """Test updating only some fields of a team."""
    team = repo.create_team(
        db_session,
        name="Kansas City Chiefs",
        city="Kansas City",
        image_url="/chiefs.png",
        thumbnail_url=None,
        created_by=test_user.id
    )

    # Update only name
    updated = repo.update_team(
        db_session,
        team,
        name="KC Chiefs"
    )

    assert updated.name == "KC Chiefs"
    assert updated.city == "Kansas City"  # Unchanged
    assert updated.image_url == "/chiefs.png"  # Unchanged


def test_update_team_none_values_ignored(db_session, test_user):
    """Test that None values don't overwrite existing fields."""
    team = repo.create_team(
        db_session,
        name="Original",
        city="Original City",
        image_url="/original.png",
        thumbnail_url=None,
        created_by=test_user.id
    )

    # Pass None for all fields - should keep originals
    updated = repo.update_team(
        db_session,
        team,
        name=None,
        city=None,
        image_url=None,
        is_active=None
    )

    assert updated.name == "Original"
    assert updated.city == "Original City"
    assert updated.image_url == "/original.png"


def test_list_teams_empty(db_session):
    """Test listing teams when none exist."""
    teams = repo.list_teams(db_session, q=None, active=None)
    assert teams == []


def test_list_teams_all(db_session, test_user):
    """Test listing all teams without filters."""
    repo.create_team(db_session, name="Team A", city="City A", image_url=None, thumbnail_url=None, created_by=test_user.id)
    repo.create_team(db_session, name="Team B", city="City B", image_url=None, thumbnail_url=None, created_by=test_user.id)
    repo.create_team(db_session, name="Team C", city="City C", image_url=None, thumbnail_url=None, created_by=test_user.id)

    teams = repo.list_teams(db_session, q=None, active=None)
    assert len(teams) == 3
    # Verify sorted by name
    assert [t.name for t in teams] == ["Team A", "Team B", "Team C"]


def test_list_teams_filter_by_query_name(db_session, test_user):
    """Test filtering teams by name query."""
    repo.create_team(db_session, name="Dallas Cowboys", city="Dallas", image_url=None, thumbnail_url=None, created_by=test_user.id)
    repo.create_team(db_session, name="Philadelphia Eagles", city="Philadelphia", image_url=None, thumbnail_url=None, created_by=test_user.id)
    repo.create_team(db_session, name="New York Giants", city="New York", image_url=None, thumbnail_url=None, created_by=test_user.id)

    # Search by name substring
    results = repo.list_teams(db_session, q="Dallas", active=None)
    assert len(results) == 1
    assert results[0].name == "Dallas Cowboys"


def test_list_teams_filter_by_query_city(db_session, test_user):
    """Test filtering teams by city query."""
    repo.create_team(db_session, name="Dallas Cowboys", city="Dallas", image_url=None, thumbnail_url=None, created_by=test_user.id)
    repo.create_team(db_session, name="Philadelphia Eagles", city="Philadelphia", image_url=None, thumbnail_url=None, created_by=test_user.id)
    repo.create_team(db_session, name="New York Giants", city="New York", image_url=None, thumbnail_url=None, created_by=test_user.id)

    # Search by city substring
    results = repo.list_teams(db_session, q="Phila", active=None)
    assert len(results) == 1
    assert results[0].name == "Philadelphia Eagles"


def test_list_teams_filter_by_active(db_session, test_user):
    """Test filtering teams by active status."""
    team1 = repo.create_team(db_session, name="Active Team", city="City", image_url=None, thumbnail_url=None, created_by=test_user.id)
    team2 = repo.create_team(db_session, name="Inactive Team", city="City", image_url=None, thumbnail_url=None, created_by=test_user.id)

    # Deactivate second team
    repo.update_team(db_session, team2, is_active=False)

    active_only = repo.list_teams(db_session, q=None, active=True)
    assert len(active_only) == 1
    assert active_only[0].name == "Active Team"

    inactive_only = repo.list_teams(db_session, q=None, active=False)
    assert len(inactive_only) == 1
    assert inactive_only[0].name == "Inactive Team"


def test_list_teams_filter_by_user_id(db_session, test_user):
    """Test filtering teams by creator."""
    # Create another user
    user2 = user_models.User(
        name="User 2",
        email="user2@example.com",
        alias="user2",
        hashed_password="hashedpwd"
    )
    db_session.add(user2)
    db_session.commit()
    db_session.refresh(user2)

    repo.create_team(db_session, name="Team by User1", city="City", image_url=None, thumbnail_url=None, created_by=test_user.id)
    repo.create_team(db_session, name="Team by User2", city="City", image_url=None, thumbnail_url=None, created_by=user2.id)

    user1_teams = repo.list_teams(db_session, q=None, active=None, user_id=test_user.id)
    assert len(user1_teams) == 1
    assert user1_teams[0].created_by == test_user.id

    user2_teams = repo.list_teams(db_session, q=None, active=None, user_id=user2.id)
    assert len(user2_teams) == 1
    assert user2_teams[0].created_by == user2.id


def test_list_teams_combined_filters(db_session, test_user):
    """Test listing with multiple filters combined."""
    repo.create_team(db_session, name="Dallas Cowboys", city="Dallas", image_url=None, thumbnail_url=None, created_by=test_user.id)
    team2 = repo.create_team(db_session, name="Dallas Stars", city="Dallas", image_url=None, thumbnail_url=None, created_by=test_user.id)
    repo.create_team(db_session, name="Philadelphia Eagles", city="Philadelphia", image_url=None, thumbnail_url=None, created_by=test_user.id)

    # Deactivate second Dallas team
    repo.update_team(db_session, team2, is_active=False)

    # Search for "Dallas" teams that are active
    results = repo.list_teams(db_session, q="Dallas", active=True)
    assert len(results) == 1
    assert results[0].name == "Dallas Cowboys"
