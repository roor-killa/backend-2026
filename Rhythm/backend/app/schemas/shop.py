from pydantic import BaseModel


class ShopItem(BaseModel):
    item_type: str
    price: int
    description: str


class PurchaseRequest(BaseModel):
    user_id: str
    item_type: str
    quantity: int


class PurchaseResponse(BaseModel):
    success: bool
    new_balance: float
    new_shield_count: int
    purchase_id: str
