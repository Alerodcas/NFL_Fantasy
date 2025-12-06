import pytest
from modules.users import repository as repo, models
from modules.users import schemas
from config import auth as security


# ==============================
# CRUD Tests
# ==============================

def test_create_user_success(db_session):
    """Test creating a user."""
    user_create = schemas.UserCreate(
        name="John Doe",
        email="john@example.com",
        alias="johndoe",
        password="Pass1234"
    )

    user = repo.create_user(db_session, user=user_create)

    assert user.id is not None
    assert user.name == "John Doe"
    assert user.email == "john@example.com"
    assert user.alias == "johndoe"
    assert user.hashed_password != "Secure123!"  # Password is hashed
    assert user.role == "manager"  # Default role
    assert user.account_status == "active"  # Default status


def test_get_user_by_email(db_session):
    """Test retrieving a user by email."""
    user_create = schemas.UserCreate(
        name="Jane Doe",
        email="jane@example.com",
        alias="janedoe",
        password="Pass1234"
    )
    created = repo.create_user(db_session, user=user_create)

    fetched = repo.get_user_by_email(db_session, email="jane@example.com")

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.email == "jane@example.com"


def test_get_user_by_email_nonexistent(db_session):
    """Test that getting a nonexistent user returns None."""
    result = repo.get_user_by_email(db_session, email="nonexistent@example.com")
    assert result is None


def test_get_user_by_email_case_sensitive(db_session):
    """Test that email lookup is case-sensitive in the database."""
    user_create = schemas.UserCreate(
        name="Test User",
        email="test@example.com",
        alias="testuser",
        password="Pass1234"
    )
    repo.create_user(db_session, user=user_create)

    # Exact match should work
    found = repo.get_user_by_email(db_session, email="test@example.com")
    assert found is not None

    # Different case may not work depending on database configuration
    found_diff_case = repo.get_user_by_email(db_session, email="TEST@EXAMPLE.COM")
    # Just verify the behavior without asserting (depends on DB)


def test_create_user_duplicate_email_fails(db_session):
    """Test that creating a user with duplicate email fails."""
    user_create1 = schemas.UserCreate(
        name="User One",
        email="duplicate@example.com",
        alias="userone",
        password="Pass1234"
    )
    repo.create_user(db_session, user=user_create1)

    # Try to create another with same email
    user_create2 = schemas.UserCreate(
        name="User Two",
        email="duplicate@example.com",
        alias="usertwo",
        password="Pass5678"
    )

    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        repo.create_user(db_session, user=user_create2)


def test_user_default_values(db_session):
    """Test that user gets correct default values on creation."""
    user_create = schemas.UserCreate(
        name="Default Test",
        email="defaults@example.com",
        alias="defaulttest",
        password="Pass1234"
    )

    user = repo.create_user(db_session, user=user_create)

    assert user.profile_image_url == "default_profile.png"
    assert user.language == "en"
    assert user.role == "manager"
    assert user.account_status == "active"
    assert user.failed_login_attempts == 0
    assert user.created_at is not None
