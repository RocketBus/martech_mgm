from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import uuid
from app.database.db import get_session

from app.auth.auth_bearer import JWTBearer
from app.member_get_member.v2.models.links import MGM_ClickTracking
from app.member_get_member.v2.models.links import MGM_Links
from app.member_get_member.v2.schema.links import LinkCountResponse
from app.src.database import crud
from app.member_get_member.v2.crud.links import _click_count
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
    "/link/click/{promoter_id}",
    response_model=MGM_ClickTracking,
    tags=[f"{tag_prefix} tracking"],
    **router_configs
)
async def set_click(
    promoter_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
        # Início da transação
        try:
            async with session.begin():
                
                promoter_link = await crud.search_value(
                    model=MGM_Links,
                    value=promoter_id,
                    column_name="member_id",
                    session=session
                )
                
                if not promoter_link:
                    MemberGetMemberException(
                        request=request,
                        message="Promoter_id not found",
                        status_code=404
                    )
                
                traking_schema  = MGM_ClickTracking(link_id=promoter_link[0].id)
                session.add(traking_schema)
                await session.flush()  # Garante que o ID e outros valores sejam atualizados
                
                return traking_schema
      
        # Tratamento genérico para outros tipos de exceção
        except Exception as e:
            MemberGetMemberException(
                request=request,
                message=str(e)
            )


@router.get(
    "/link/count/{promoter_id}",
    response_model=LinkCountResponse,
    tags=[f"{tag_prefix} tracking"],
    **router_configs
)
async def get_link_count(
    promoter_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    try:
        promoter_link = await crud.search_value(
            model=MGM_Links,
            value=promoter_id,
            column_name="member_id",
            session=session
        )
        
        if not promoter_link:
            MemberGetMemberException(
                request=request,
                message="Promoter_id not found",
                status_code=404
            )
        
        click_count = await _click_count(promoter_link[0].id, session)
        response = LinkCountResponse(link_id=promoter_link[0].id,count=click_count)
        return response
    
    except Exception as e:
        MemberGetMemberException(
            request=request,
            message=str(e)
        )