from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..schemas.shop import ShopItem, PurchaseRequest, PurchaseResponse
from ..services.shop_service import ShopService

router = APIRouter(prefix="/shop", tags=["shop"])


@router.get("/items", response_model=list[ShopItem])
async def get_shop_items(db: AsyncSession = Depends(get_db)):
    service = ShopService(db)
    return service.get_shop_items()


@router.post("/purchase", response_model=PurchaseResponse)
async def purchase(data: PurchaseRequest, db: AsyncSession = Depends(get_db)):
    service = ShopService(db)
    return await service.purchase_shields(data)
