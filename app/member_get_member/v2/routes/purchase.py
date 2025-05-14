from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.database.db import get_session
from fastapi import status
from app.auth.auth_bearer import JWTBearer
from app.src.clickbus.clickbus import Orders
from app.member_get_member.v2.crud.purchase import create_purchase
from app.member_get_member.v2.crud.invitations import set_stage
from app.member_get_member.v2.crud.promoter import get_promoter_link_id_by_promoter_id
from app.member_get_member.v2.models.purchase import MGM_Purchases
from app.member_get_member.v2.schema.purchase import CreatePurchase, PurchaseBase
from app.member_get_member.v2.exeptions.exceptions import MemberAlreadyExists, MemberGetMemberException

# Inicializa o roteador da aplicação
router = APIRouter()

# Configura dependências comuns a todos os endpoints do router
router_configs = {
    "dependencies": [Depends(JWTBearer(token_types=["access", "refresh"]))]
}

# Prefixo padrão para identificação dos endpoints no Swagger
tag_prefix = "[ Member get member ]"

@router.post(
    "/purchase/{promoter_id}",
    response_model=MGM_Purchases,
    tags=[f"{tag_prefix} tracking"],
    **router_configs
)
async def purchase(
    purchase: CreatePurchase,
    promoter_id : uuid.UUID ,
    request: Request,
    session: AsyncSession = Depends(get_session),
    clickbus_orders:Orders = Depends(Orders),
):
    try:
        async with session.begin():
            
            order = await  clickbus_orders.get_order(purchase.order_id)
            
            order_response = order.json()
            
            departure_time = await clickbus_orders.get_departure_date(
                order_response=order_response
            )
            
            purchase_schema = await create_purchase(
                purchase=purchase,
                session=session,
                departure_time=departure_time,
                promoter_id=promoter_id
            )
            
            promoter_link_id = await get_promoter_link_id_by_promoter_id(
                promoter_id=promoter_id,
                session=session,
                request=request
            )
            
            await set_stage(
                invited_id=purchase.invited_id,
                promoter_link_id=promoter_link_id,
                stage="purchase_approved",
                session=session
            )
        
            response = purchase_schema
            return response 
    
    # Tratamento genérico para outros tipos de exceção
    except Exception as e:
        MemberGetMemberException(
            request=request,
            message=str(e)
        )