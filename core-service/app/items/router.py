from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.items.repository import ItemRepository
from app.items.schemas import ItemCreate, ItemResponse, ItemUpdate
from app.items.service import ItemService

router = APIRouter(prefix="/items", tags=["items"])


def get_service(db: AsyncSession = Depends(get_db)) -> ItemService:
    return ItemService(ItemRepository(db))


@router.get("", response_model=list[ItemResponse])
async def list_items(
    user_id: str = Depends(get_current_user_id),
    svc: ItemService = Depends(get_service),
):
    return await svc.get_all(user_id)


@router.post("", response_model=ItemResponse, status_code=201)
async def create_item(
    data: ItemCreate,
    user_id: str = Depends(get_current_user_id),
    svc: ItemService = Depends(get_service),
):
    return await svc.create(data, user_id)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: str,
    user_id: str = Depends(get_current_user_id),
    svc: ItemService = Depends(get_service),
):
    return await svc.get_by_id(item_id, user_id)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: str,
    data: ItemUpdate,
    user_id: str = Depends(get_current_user_id),
    svc: ItemService = Depends(get_service),
):
    return await svc.update(item_id, data, user_id)


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: str,
    user_id: str = Depends(get_current_user_id),
    svc: ItemService = Depends(get_service),
):
    await svc.delete(item_id, user_id)
