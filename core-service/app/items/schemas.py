from pydantic import BaseModel


class ItemCreate(BaseModel):
    title: str
    description: str | None = None


class ItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class ItemResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str | None

    model_config = {"from_attributes": True}
