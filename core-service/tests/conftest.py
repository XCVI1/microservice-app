import pytest_asyncio
import respx
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Фейковый user_id для тестов
FAKE_USER_ID = "test-user-123"


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Мокаем вызов к auth-service — возвращаем валидный токен
    with respx.mock(
        base_url="http://auth-service:8001", assert_all_called=False
    ) as mock:
        mock.post("/api/v1/auth/validate").mock(
            return_value=Response(
                200,
                json={"valid": True, "user_id": FAKE_USER_ID, "email": "test@test.com"},
            )
        )
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauth_client(db_session: AsyncSession) -> AsyncClient:
    """Клиент с невалидным токеном — auth-service возвращает valid=False."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with respx.mock(base_url="http://auth-service:8001") as mock:
        mock.post("/api/v1/auth/validate").mock(
            return_value=Response(200, json={"valid": False})
        )
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    app.dependency_overrides.clear()
