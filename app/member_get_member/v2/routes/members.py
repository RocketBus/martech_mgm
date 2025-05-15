from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session

from app.auth.auth_bearer import JWTBearer
from app.member_get_member.v2.schema.member import (
    MembersResponse
    )
from app.member_get_member.v2.crud.promoter import get_member


# Inicializa o roteador da aplicação
router = APIRouter()

# Configura dependências comuns a todos os endpoints do router
router_configs = {
    "dependencies": [Depends(JWTBearer(token_types=["access", "refresh"]))]
}

# Prefixo padrão para identificação dos endpoints no Swagger
tag_prefix = "[ Member get member ]"

@router.get(
    "/member/email/{email}",
    response_model=MembersResponse,
    tags=[f"{tag_prefix} information by"],
    **router_configs
)
async def get_promoter_by_email(
    email: str,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    response = await get_member(email,'email',session,request)
    return response.to_base64()

@router.get(
    "/member/user_id/{user_id}",
    response_model=MembersResponse,
    tags=[f"{tag_prefix} information by"],
    **router_configs
)
async def get_promoter_by_user_id(
    user_id: str,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    response = await get_member(user_id,'user_id',session,request)
    return response.to_base64()