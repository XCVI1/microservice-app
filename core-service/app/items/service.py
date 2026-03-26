from fastapi import HTTPException, status

from app.items.models import Item
from app.items.repository import ItemRepository
from app.items.schemas import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, repo: ItemRepository):
        self.repo = repo

    async def get_all(self, user_id: str) -> list[Item]:
        return await self.repo.get_all(user_id)

    async def get_by_id(self, item_id: str, user_id: str) -> Item:
        item = await self.repo.get_by_id(item_id, user_id)
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
        return item

    async def create(self, data: ItemCreate, user_id: str) -> Item:
        item = Item(
            user_id=user_id,
            title=data.title,
            description=data.description,
        )
        return await self.repo.create(item)

    async def update(self, item_id: str, data: ItemUpdate, user_id: str) -> Item:
        item = await self.get_by_id(item_id, user_id)
        if data.title is not None:
            item.title = data.title
        if data.description is not None:
            item.description = data.description
        return await self.repo.update(item)

    async def delete(self, item_id: str, user_id: str) -> None:
        item = await self.get_by_id(item_id, user_id)
        await self.repo.delete(item)
