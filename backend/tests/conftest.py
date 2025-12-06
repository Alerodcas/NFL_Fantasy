from pathlib import Path
import sys

# Se asegura de que `backend/src` este en sys.path antes de importar paquetes de la aplicacion
ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = str(ROOT / "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Añade `backend/src` a sys.path para que las pruebas puedan importar los paquetes `config` y `modules`
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# También añade el directorio de pruebas para poder importar módulos auxiliares (tests/helpers)
TESTS_DIR = str(Path(__file__).resolve().parent)
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import all models to ensure they're registered with metadata
from modules.users import models as user_models
from modules.teams import models as team_models
from modules.players import models as player_models
from modules.fantasy_teams import models as fantasy_team_models
from modules.leagues import models as league_models
from config.database import Base
from helpers.factories import create_user


@pytest.fixture
def db_session():
    """
    Provides a fresh in-memory SQLite database for each test.
    
    This fixture:
    - Creates tables based on all imported models
    - Provides a clean session for testing
    - Automatically cleans up after the test
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session):
    """
    Creates a test user for use in tests.
    
    Provides a convenient way to get a user with default values
    for tests that need foreign key references.
    """
    return create_user(db_session)
