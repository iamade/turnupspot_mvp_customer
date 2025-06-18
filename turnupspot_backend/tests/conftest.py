import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+1234567890"
    }


@pytest.fixture
def test_sport_group_data():
    return {
        "name": "Test Football Group",
        "description": "A test football group",
        "sport_type": "football",
        "venue_name": "Test Stadium",
        "venue_address": "123 Test Street",
        "venue_latitude": 40.7128,
        "venue_longitude": -74.0060,
        "max_teams": 8,
        "max_players_per_team": 11,
        "playing_days": ["monday", "wednesday", "friday"],
        "game_start_time": "18:00",
        "game_end_time": "20:00"
    }


@pytest.fixture
def test_event_data():
    from datetime import datetime, timedelta
    
    return {
        "title": "Test Event",
        "description": "A test event",
        "event_type": "party",
        "start_datetime": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "end_datetime": (datetime.utcnow() + timedelta(days=7, hours=3)).isoformat(),
        "venue_name": "Test Venue",
        "venue_address": "456 Test Avenue",
        "is_free": True,
        "ticket_price": 0.0
    }