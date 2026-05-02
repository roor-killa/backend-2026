import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from ..models.user import User
from ..models.purchase import Purchase
from ..schemas.shop import ShopItem, PurchaseRequest, PurchaseResponse
from ..utils.exceptions import UserNotFoundError, InsufficientFundsError, InvalidQuantityError
from ..config import settings


SHOP_ITEMS = [
    ShopItem(item_type="shield", price=settings.shield_price, description="Protects against one missed note"),
]


class ShopService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def get_shop_items(self) -> list[ShopItem]:
        return SHOP_ITEMS

    async def purchase_shields(self, data: PurchaseRequest) -> PurchaseResponse:
        if data.quantity <= 0:
            raise InvalidQuantityError("Quantity must be at least 1")

        item = next((i for i in SHOP_ITEMS if i.item_type == data.item_type), None)
        if not item:
            raise ValueError(f"Unknown item type: {data.item_type}")

        total_cost = item.price * data.quantity

        # Single conditional UPDATE — no SELECT needed on the happy path
        result = await self.db.execute(
            update(User)
            .where(User.id == data.user_id, User.account_funds >= total_cost)
            .values(
                account_funds=User.account_funds - total_cost,
                shields_owned=User.shields_owned + data.quantity,
            )
            .returning(User)
        )
        user = result.scalar_one_or_none()

        if not user:
            # Determine whether user doesn't exist or funds are insufficient
            check = await self.db.execute(
                select(User.account_funds).where(User.id == data.user_id)
            )
            funds = check.scalar_one_or_none()
            if funds is None:
                raise UserNotFoundError(f"User '{data.user_id}' not found")
            raise InsufficientFundsError(needed=total_cost, available=float(funds))

        purchase = Purchase(
            id=str(uuid.uuid4()),
            user_id=data.user_id,
            item_type=data.item_type,
            quantity=data.quantity,
            cost=total_cost,
        )
        self.db.add(purchase)
        await self.db.flush()

        return PurchaseResponse(
            success=True,
            new_balance=float(user.account_funds),
            new_shield_count=user.shields_owned,
            purchase_id=purchase.id,
        )

    async def get_purchase_history(self, user_id: str) -> list[Purchase]:
        result = await self.db.execute(select(Purchase).where(Purchase.user_id == user_id))
        return list(result.scalars().all())
