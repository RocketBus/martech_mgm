import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request, status, HTTPException

from app.database.db import get_session
from app.auth.auth_bearer import JWTBearer
from app.src.clickbus.clickbus import Orders
from app.src.scheduler.scheduler import ActionScheduler

from app.member_get_member.v2.crud.invitations import set_stage
from app.member_get_member.v2.crud.purchase import create_purchase,get_orders_departured
from app.member_get_member.v2.crud.promoter import get_promoter_link_id_by_promoter_id
from app.member_get_member.v2.models.purchase import MGM_Purchases
from app.member_get_member.v2.schema.purchase import CreatePurchase
from app.member_get_member.v2.exeptions.exceptions import MemberGetMemberException

# Inicializa o roteador da aplicação
router = APIRouter()

# Define as dependências padrão para todos os endpoints deste roteador
router_configs = {
    "dependencies": [Depends(JWTBearer(token_types=["access", "refresh"]))]
}

# Prefixo utilizado na documentação Swagger para agrupar os endpoints
tag_prefix = "[ Member get member ]"

@router.post(
    "/purchase/{promoter_id}",
    response_model=MGM_Purchases,
    tags=[f"{tag_prefix} tracking"],
    **router_configs
)
async def purchase(
    purchase: CreatePurchase,
    promoter_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    clickbus_orders: Orders = Depends(Orders),
):
    """
    Endpoint responsável por registrar uma compra associada a um promotor.

    Parâmetros:
    - purchase (CreatePurchase): Vincular order_id de um pedido a uma compra feita pelo convidado de um promotor.
    - promoter_id (uuid.UUID): Identificador do promotor responsável pela indicação.
    - request (Request): Objeto de requisição HTTP do FastAPI.
    - session (AsyncSession): Sessão de banco de dados assíncrona.
    - clickbus_orders (Orders): Serviço externo da ClickBus para busca de pedidos(order).

    Retorna:
    - Um objeto `MGM_Purchases` representando a compra registrada.
    """

    try:
        # Inicia uma transação assíncrona no banco de dados (Respeitar atomicidade)
        async with session.begin():
            
            # Busca os detalhes do pedido no serviço externo da ClickBus
            order = await clickbus_orders.get_order(purchase.order_id)
            order_response = order.json()

            # Obtém a data de embarque com base na resposta do pedido
            departure_time = await clickbus_orders.get_departure_date(
                order_response=order_response
            )

            # Registra a compra no banco de dados com os dados coletados
            purchase_schema = await create_purchase(
                purchase=purchase,
                session=session,
                departure_time=departure_time,
                promoter_id=promoter_id
            )

            # Obtém o ID do link do promotor (usado para rastreamento)
            promoter_link_id = await get_promoter_link_id_by_promoter_id(
                promoter_id=promoter_id,
                session=session,
                request=request
            )

            # Atualiza o estágio do convidado para "purchase_approved"
            await set_stage(
                invited_id=purchase.invited_id,
                promoter_link_id=promoter_link_id,
                stage="purchase_approved",
                session=session
            )

            # Retorna o schema da compra registrada
            return purchase_schema
    
    except Exception as e:
        # Lança exceção customizada com a mensagem do erro capturado
        MemberGetMemberException(
            request=request,
            message=str(e)
        )



@router.get("/departured/voucher/", **router_configs,tags=[f"{tag_prefix} create"])
async def departure_vucher(
    request : Request,
    session : AsyncSession = Depends(get_session),
):
    try:
        e = None
        orders =  await get_orders_departured(session=session)
        if not orders:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='No orders found.'
            )
        scheduler = ActionScheduler()
        scheduler.activate()
        await scheduler.addJob(
            'mgm_departure_invited',{'orders':orders,'session':session,'request':request}
        )
        return HTTPException(
            status_code=200,
            detail="Processo iniado"
        )
    except (Exception) as e:
        MemberGetMemberException(message=str(e),request=request)
   