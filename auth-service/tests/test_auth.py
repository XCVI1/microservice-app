# bandit: disable: B101, B105
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"
ME_URL = "/api/v1/auth/me"
VALIDATE_URL = "/api/v1/auth/validate"

VALID_USER = {
    "email": "user@example.com",
    "password": "secret123",  # nosec
    "first_name": "John",
    "last_name": "Doe",
}


# ─── Health ──────────────────────────────────────────────────────────────

async def test_liveness(client: AsyncClient):
    response = await client.get("/health/live")
    assert response.status_code == 200  # nosec
    assert response.json()["status"] == "ok"  # nosec
    assert response.json()["service"] == "auth"  # nosec


async def test_readiness(client: AsyncClient):
    response = await client.get("/health/ready")
    assert response.status_code == 200  # nosec
    assert response.json()["status"] == "ok"  # nosec
    assert response.json()["db"] == "ok"  # nosec


# ─── Register ───────────────────────────────────────────────────────────────


async def test_register_success(client: AsyncClient):
    response = await client.post(REGISTER_URL, json=VALID_USER)
    assert response.status_code == 201  # nosec
    data = response.json()
    assert "access_token" in data  # nosec
    assert "refresh_token" in data  # nosec
    assert data["token_type"] == "bearer"  # nosec


async def test_register_duplicate_email(client: AsyncClient):
    await client.post(REGISTER_URL, json=VALID_USER)
    response = await client.post(REGISTER_URL, json=VALID_USER)
    assert response.status_code == 409  # nosec


async def test_register_invalid_email(client: AsyncClient):
    response = await client.post(
        REGISTER_URL, json={**VALID_USER, "email": "not-an-email"}
    )
    assert response.status_code == 422  # nosec


async def test_register_missing_fields(client: AsyncClient):
    response = await client.post(REGISTER_URL, json={"email": "user@example.com"})
    assert response.status_code == 422  # nosec


# ─── Login ────────────────────────────────────────────────────────────────────


async def test_login_success(client: AsyncClient):
    await client.post(REGISTER_URL, json=VALID_USER)
    response = await client.post(
        LOGIN_URL,
        json={"email": VALID_USER["email"], "password": VALID_USER["password"]},  # nosec
    )
    assert response.status_code == 200  # nosec
    assert "access_token" in response.json()  # nosec


async def test_login_wrong_password(client: AsyncClient):
    await client.post(REGISTER_URL, json=VALID_USER)
    response = await client.post(
        LOGIN_URL,
        json={"email": VALID_USER["email"], "password": "wrongpassword"},  # nosec
    )
    assert response.status_code == 401  # nosec


async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post(
        LOGIN_URL,
        json={"email": "ghost@example.com", "password": "password"},  # nosec
    )
    assert response.status_code == 401  # nosec


# ─── Refresh ──────────────────────────────────────────────────────────────────


async def test_refresh_success(client: AsyncClient):
    reg = await client.post(REGISTER_URL, json=VALID_USER)
    refresh_token = reg.json()["refresh_token"]
    response = await client.post(REFRESH_URL, json={"refresh_token": refresh_token})
    assert response.status_code == 200  # nosec
    assert "access_token" in response.json()  # nosec


async def test_refresh_invalid_token(client: AsyncClient):
    response = await client.post(
        REFRESH_URL,
        json={"refresh_token": "invalid.token.here"},  # nosec
    )
    assert response.status_code == 401  # nosec


async def test_refresh_with_access_token(client: AsyncClient):
    reg = await client.post(REGISTER_URL, json=VALID_USER)
    access_token = reg.json()["access_token"]
    response = await client.post(REFRESH_URL, json={"refresh_token": access_token})
    assert response.status_code == 401  # nosec


# ─── Me ───────────────────────────────────────────────────────────────────────


async def test_me_success(client: AsyncClient):
    reg = await client.post(REGISTER_URL, json=VALID_USER)
    access_token = reg.json()["access_token"]
    response = await client.get(
        ME_URL, headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200  # nosec
    data = response.json()
    assert data["email"] == VALID_USER["email"]  # nosec
    assert data["first_name"] == VALID_USER["first_name"]  # nosec


async def test_me_no_token(client: AsyncClient):
    response = await client.get(ME_URL)
    assert response.status_code == 403  # nosec


async def test_me_invalid_token(client: AsyncClient):
    response = await client.get(
        ME_URL,
        headers={"Authorization": "Bearer invalid.token"},  # nosec
    )
    assert response.status_code == 401  # nosec


# ─── Validate ─────────────────────────────────────────────────────────────────


async def test_validate_valid_token(client: AsyncClient):
    reg = await client.post(REGISTER_URL, json=VALID_USER)
    access_token = reg.json()["access_token"]
    response = await client.post(VALIDATE_URL, json={"token": access_token})
    assert response.status_code == 200  # nosec
    data = response.json()
    assert data["valid"] is True  # nosec
    assert data["user_id"] is not None  # nosec


async def test_validate_invalid_token(client: AsyncClient):
    response = await client.post(VALIDATE_URL, json={"token": "invalid.token"})  # nosec
    assert response.status_code == 200  # nosec
    assert response.json()["valid"] is False  # nosec


async def test_validate_refresh_token_rejected(client: AsyncClient):
    reg = await client.post(REGISTER_URL, json=VALID_USER)
    refresh_token = reg.json()["refresh_token"]
    response = await client.post(VALIDATE_URL, json={"token": refresh_token})
    assert response.status_code == 200  # nosec
    assert response.json()["valid"] is False  # nosec
