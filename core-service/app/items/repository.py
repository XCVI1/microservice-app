from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.items.models import Item


class ItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, user_id: str) -> list[Item]:
        result = await self.db.execute(select(Item).where(Item.user_id == user_id))
        return list(result.scalars().all())

    async def get_by_id(self, item_id: str, user_id: str) -> Item | None:
        result = await self.db.execute(
            select(Item).where(Item.id == item_id, Item.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, item: Item) -> Item:
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def update(self, item: Item) -> Item:
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete(self, item: Item) -> None:
        await self.db.delete(item)
        await self.db.commit()
