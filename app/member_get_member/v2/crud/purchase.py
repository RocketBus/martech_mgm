from app.member_get_member.v2.models.purchase import MGM_Purchases
from app.member_get_member.v2.schema.purchase import CreatePurchase
from app.src.database.crud import search_value
from app.src.utils import datetime_now
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List
import uuid
from sqlmodel import select, and_, update

from sqlmodel import update
from sqlalchemy.ext.asyncio import AsyncSession

from sqlmodel import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def update_orders_departured(order_id: str, succes_or_fail: bool, session: AsyncSession):
    config = {
        True: {"status": "departured", "departure": True},
        False: {"status": "Order inválida", "departure": False}  
    }

    # Executa o update
    query = (
        update(MGM_Purchases)
        .where(MGM_Purchases.order_id == order_id)
        .values(**config[succes_or_fail])
    )
    
    await session.execute(query)
    # await session.commit()

    # Buscar o registro atualizado
    query = select(MGM_Purchases).where(MGM_Purchases.order_id == order_id)
    result = await session.execute(query)
    updated_order = result.scalar_one_or_none()

    return updated_order


async def get_orders_departured(session : AsyncSession):
    query = select(MGM_Purchases.order_id).where(and_(
        MGM_Purchases.departure_time <= datetime_now(True),
        MGM_Purchases.status == 'new',
        MGM_Purchases.departure == False
    )
    )
    result = await session.execute(query)
    orders = result.scalars().all()
    return orders

async def get_order_by_order(order_id:str,session:AsyncSession)->List[MGM_Purchases]:
    response = await search_value(
        model=MGM_Purchases,
        value=order_id,
        column_name='order_id',
        session=session,
    )
    return response

async def create_purchase(purchase : CreatePurchase, departure_time : datetime, promoter_id : uuid.UUID,session : AsyncSession, status: str = 'new'):
    try:
        await order_id_exist(purchase.order_id,session)
        purchase_schema = MGM_Purchases(
        invited_id=purchase.invited_id,
        promoter_id=promoter_id,
        order_id=purchase.order_id,
        departure_time=departure_time,
        departure=False,
        status=status
        )
        session.add(purchase_schema)
        return purchase_schema
    except Exception as e:
        raise Exception(str(e))

async def order_id_exist(order_id,session)->None:
    response = await search_value(
        model=MGM_Purchases,
        value=order_id,
        column_name='order_id',
        session=session,
    )
    if len(response) > 0:
        raise Exception('order_id already exists')

