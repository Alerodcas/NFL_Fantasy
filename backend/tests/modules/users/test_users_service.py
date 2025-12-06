import pytest
from datetime import datetime, timezone

from modules.users import service as svc, schemas, models
from config import auth as security


# ==============================
# Register User Tests
# ==============================

def test_register_user_success(db_session):
    """Test successful user registration."""
    user_create = schemas.UserCreate(
        name="New User",
        email="newuser@example.com",
        alias="newuser",
        password="Pass1234"
    )

    user = svc.register_user(db=db_session, user=user_create)

    assert user.id is not None
    assert user.name == "New User"
    assert user.email == "newuser@example.com"
    assert user.alias == "newuser"
    assert user.account_status == "active"


def test_register_user_duplicate_email_fails(db_session):
    """Test that registering with duplicate email fails."""
    user_create1 = schemas.UserCreate(
        name="First User",
        email="duplicate@example.com",
        alias="first",
        password="Pass1234"
    )
    svc.register_user(db=db_session, user=user_create1)

    user_create2 = schemas.UserCreate(
        name="Second User",
        email="duplicate@example.com",
        alias="second",
        password="Pass5678"
    )

    with pytest.raises(ValueError, match="already registered"):
        svc.register_user(db=db_session, user=user_create2)


# ==============================
# Authenticate User Tests
# ==============================

def test_authenticate_user_success(db_session):
    """Test successful user authentication."""
    # Create user
    user_create = schemas.UserCreate(
        name="Auth Test",
        email="authtest@example.com",
        alias="authtest",
        password="Test1234"
    )
    svc.register_user(db=db_session, user=user_create)

    # Authenticate with correct password
    user = svc.authenticate_user(db_session, "authtest@example.com", "Test1234")

    assert user is not None
    assert user.email == "authtest@example.com"
    assert user.failed_login_attempts == 0
    assert user.last_activity is not None


def test_authenticate_user_wrong_password_fails(db_session):
    """Test that authentication fails with wrong password."""
    user_create = schemas.UserCreate(
        name="Wrong Pass Test",
        email="wrongpass@example.com",
        alias="wrongpass",
        password="Test1234"
    )
    svc.register_user(db=db_session, user=user_create)

    with pytest.raises(PermissionError, match="Invalid credentials"):
        svc.authenticate_user(db_session, "wrongpass@example.com", "WrongPass456")


def test_authenticate_user_nonexistent_fails(db_session):
    """Test that authentication fails for nonexistent user."""
    with pytest.raises(PermissionError, match="Invalid credentials"):
        svc.authenticate_user(db_session, "nonexistent@example.com", "SomePass123")


def test_authenticate_user_increments_failed_attempts(db_session):
    """Test that failed login attempts are tracked."""
    user_create = schemas.UserCreate(
        name="Failed Attempts",
        email="failattempts@example.com",
        alias="failattempts",
        password="Test1234"
    )
    user = svc.register_user(db=db_session, user=user_create)

    # Try wrong password
    try:
        svc.authenticate_user(db_session, "failattempts@example.com", "WrongPass")
    except PermissionError:
        pass

    # Refresh user from DB
    db_session.refresh(user)
    assert user.failed_login_attempts == 1


def test_authenticate_user_blocks_after_max_attempts(db_session):
    """Test that account is blocked after max failed attempts."""
    user_create = schemas.UserCreate(
        name="Block Test",
        email="blocktest@example.com",
        alias="blocktest",
        password="Test1234"
    )
    user = svc.register_user(db=db_session, user=user_create)

    # Try 5 wrong passwords
    for i in range(5):
        try:
            svc.authenticate_user(db_session, "blocktest@example.com", f"WrongPass{i}")
        except PermissionError as e:
            if i == 4:  # 5th attempt should trigger lock
                assert "locked" in str(e).lower() or "blocked" in str(e).lower()

    # Verify account is blocked
    db_session.refresh(user)
    assert user.account_status == "blocked"


def test_authenticate_blocked_user_fails(db_session):
    """Test that blocked user cannot authenticate even with correct password."""
    user_create = schemas.UserCreate(
        name="Blocked User",
        email="blocked@example.com",
        alias="blocked",
        password="Test1234"
    )
    user = svc.register_user(db=db_session, user=user_create)

    # Manually block the account
    user.account_status = "blocked"
    db_session.commit()

    with pytest.raises(PermissionError, match="blocked"):
        svc.authenticate_user(db_session, "blocked@example.com", "Test1234")


def test_authenticate_resets_failed_attempts_on_success(db_session):
    """Test that successful login resets failed attempt counter."""
    user_create = schemas.UserCreate(
        name="Reset Attempts",
        email="resetattempts@example.com",
        alias="resetattempts",
        password="Test1234"
    )
    user = svc.register_user(db=db_session, user=user_create)

    # Simulate failed attempts
    user.failed_login_attempts = 3
    db_session.commit()

    # Now authenticate with correct password
    authenticated = svc.authenticate_user(db_session, "resetattempts@example.com", "Test1234")

    assert authenticated.failed_login_attempts == 0


# ==============================
# Token Tests
# ==============================

def test_create_access_token_for_user(db_session):
    """Test JWT token creation."""
    user_create = schemas.UserCreate(
        name="Token Test",
        email="token@example.com",
        alias="token",
        password="Pass1234"
    )
    user = svc.register_user(db=db_session, user=user_create)

    token = svc.create_access_token_for_user(user)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_includes_user_email(monkeypatch, db_session):
    """Test that token includes user email."""
    from jose import jwt

    user_create = schemas.UserCreate(
        name="Token Email Test",
        email="tokenemail@example.com",
        alias="tokenemail",
        password="Pass1234"
    )
    user = svc.register_user(db=db_session, user=user_create)

    token = svc.create_access_token_for_user(user)

    # Decode token (without verification for testing)
    decoded = jwt.decode(token, "", options={"verify_signature": False})

    assert decoded.get("sub") == "tokenemail@example.com"
    assert decoded.get("user_id") == user.id


# ==============================
# Update Profile Tests
# ==============================

def test_update_user_profile_name(db_session):
    """Test updating user name."""
    user_create = schemas.UserCreate(
        name="Original Name",
        email="update@example.com",
        alias="update",
        password="Pass1234"
    )
    user = svc.register_user(db=db_session, user=user_create)

    updated = svc.update_user_profile(db_session, user, name="Updated Name")

    assert updated.name == "Updated Name"
    assert updated.email == "update@example.com"  # Unchanged


def test_update_user_profile_alias(db_session):
    """Test updating user alias."""
    user_create = schemas.UserCreate(
        name="Alias Test",
        email="alias@example.com",
        alias="oldalias",
        password="Pass1234"
    )
    user = svc.register_user(db=db_session, user=user_create)

    updated = svc.update_user_profile(db_session, user, alias="newalias")

    assert updated.alias == "newalias"
    assert updated.name == "Alias Test"  # Unchanged


def test_update_user_profile_password(db_session):
    """Test updating user password."""
    user_create = schemas.UserCreate(
        name="Password Test",
        email="password@example.com",
        alias="password",
        password="Test1234"
    )
    user = svc.register_user(db=db_session, user=user_create)

    old_hash = user.hashed_password
    updated = svc.update_user_profile(db_session, user, password="New5678")

    assert updated.hashed_password != old_hash
    assert updated.hashed_password != "NewPass456"  # Still hashed


def test_update_user_profile_multiple_fields(db_session):
    """Test updating multiple fields at once."""
    user_create = schemas.UserCreate(
        name="Original Name",
        email="multiupdate@example.com",
        alias="oldname",
        password="Test1234"
    )
    user = svc.register_user(db=db_session, user=user_create)

    updated = svc.update_user_profile(
        db_session,
        user,
        name="New Name",
        alias="newname",
        password="New5678"
    )

    assert updated.name == "New Name"
    assert updated.alias == "newname"
    # Verify password was changed by trying to authenticate
    auth_user = svc.authenticate_user(db_session, "multiupdate@example.com", "New5678")
    assert auth_user is not None
