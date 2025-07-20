import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_todo.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Удаляем тестовую базу если есть
    if os.path.exists("test_todo.db"):
        os.remove("test_todo.db")
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    yield
    # Можно удалить базу после тестов, если нужно
    if os.path.exists("test_todo.db"):
        os.remove("test_todo.db")


@pytest.fixture()
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
