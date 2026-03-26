import pytest
from httpx import AsyncClient

from tests.conftest import FAKE_USER_ID

pytestmark = pytest.mark.asyncio

ITEMS_URL = "/api/v1/items"
AUTH_HEADER = {"Authorization": "Bearer fake-token"}


# ─── Health ───────────────────────────────────────────────────────────────────


async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "core"


# ─── Auth guard ───────────────────────────────────────────────────────────────


async def test_list_items_no_token(unauth_client: AsyncClient):
    response = await unauth_client.get(ITEMS_URL, headers=AUTH_HEADER)
    assert response.status_code == 401


async def test_create_item_no_token(unauth_client: AsyncClient):
    response = await unauth_client.post(
        ITEMS_URL,
        json={"title": "Test"},
        headers=AUTH_HEADER,
    )
    assert response.status_code == 401


# ─── Create ───────────────────────────────────────────────────────────────────


async def test_create_item_success(client: AsyncClient):
    response = await client.post(
        ITEMS_URL,
        json={"title": "My item", "description": "Some description"},
        headers=AUTH_HEADER,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My item"
    assert data["description"] == "Some description"
    assert data["user_id"] == FAKE_USER_ID
    assert "id" in data


async def test_create_item_without_description(client: AsyncClient):
    response = await client.post(
        ITEMS_URL,
        json={"title": "No desc"},
        headers=AUTH_HEADER,
    )
    assert response.status_code == 201
    assert response.json()["description"] is None


async def test_create_item_missing_title(client: AsyncClient):
    response = await client.post(
        ITEMS_URL,
        json={"description": "No title"},
        headers=AUTH_HEADER,
    )
    assert response.status_code == 422


# ─── List ─────────────────────────────────────────────────────────────────────


async def test_list_items_empty(client: AsyncClient):
    response = await client.get(ITEMS_URL, headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json() == []


async def test_list_items_returns_own_items(client: AsyncClient):
    await client.post(ITEMS_URL, json={"title": "Item 1"}, headers=AUTH_HEADER)
    await client.post(ITEMS_URL, json={"title": "Item 2"}, headers=AUTH_HEADER)

    response = await client.get(ITEMS_URL, headers=AUTH_HEADER)
    assert response.status_code == 200
    assert len(response.json()) == 2


# ─── Get ──────────────────────────────────────────────────────────────────────


async def test_get_item_success(client: AsyncClient):
    created = await client.post(
        ITEMS_URL, json={"title": "Get me"}, headers=AUTH_HEADER
    )
    item_id = created.json()["id"]

    response = await client.get(f"{ITEMS_URL}/{item_id}", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json()["id"] == item_id


async def test_get_item_not_found(client: AsyncClient):
    response = await client.get(f"{ITEMS_URL}/nonexistent-id", headers=AUTH_HEADER)
    assert response.status_code == 404


# ─── Update ───────────────────────────────────────────────────────────────────


async def test_update_item_success(client: AsyncClient):
    created = await client.post(
        ITEMS_URL, json={"title": "Old title"}, headers=AUTH_HEADER
    )
    item_id = created.json()["id"]

    response = await client.put(
        f"{ITEMS_URL}/{item_id}",
        json={"title": "New title"},
        headers=AUTH_HEADER,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New title"


async def test_update_item_not_found(client: AsyncClient):
    response = await client.put(
        f"{ITEMS_URL}/nonexistent-id",
        json={"title": "New title"},
        headers=AUTH_HEADER,
    )
    assert response.status_code == 404


# ─── Delete ───────────────────────────────────────────────────────────────────


async def test_delete_item_success(client: AsyncClient):
    created = await client.post(
        ITEMS_URL, json={"title": "Delete me"}, headers=AUTH_HEADER
    )
    item_id = created.json()["id"]

    response = await client.delete(f"{ITEMS_URL}/{item_id}", headers=AUTH_HEADER)
    assert response.status_code == 204

    # Проверяем что item удалён
    get_response = await client.get(f"{ITEMS_URL}/{item_id}", headers=AUTH_HEADER)
    assert get_response.status_code == 404


async def test_delete_item_not_found(client: AsyncClient):
    response = await client.delete(f"{ITEMS_URL}/nonexistent-id", headers=AUTH_HEADER)
    assert response.status_code == 404
