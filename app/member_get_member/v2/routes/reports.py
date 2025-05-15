
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import uuid
from typing import Dict
from app.database.db import get_session
from app.member_get_member.v2.schema.report import ReportBase
from app.member_get_member.v2.crud.promoter import get_promoter_link_id_by_promoter_id
from app.member_get_member.v2.crud.invitations import count_stages
from app.auth.auth_bearer import JWTBearer
from app.member_get_member.v2.crud.members import set_member
from app.member_get_member.v2.schema.member import (
    CreateBase,
    MembersResponse
    )
from app.member_get_member.v2.exeptions.exceptions import MemberAlreadyExists, MemberGetMemberException


# Inicializa o roteador da aplicação
router = APIRouter()

# Configura dependências comuns a todos os endpoints do router
router_configs = {
    "dependencies": [Depends(JWTBearer(token_types=["access", "refresh"]))]
}

# Prefixo padrão para identificação dos endpoints no Swagger
tag_prefix = "[ Member get member ]"
@router.get("/reports/{promoter_id}",response_model=ReportBase,**router_configs,tags=[f"{tag_prefix} report"])
async def get_promoter_reports(promoter_id : str,request: Request, session : AsyncSession = Depends(get_session)):
    pass
    try:
        
        promoter_id = uuid.UUID(promoter_id)
        promoter_link_id =  await get_promoter_link_id_by_promoter_id(promoter_id,session=session,request=request)
        response =  await count_stages(link_id=promoter_link_id,session=session)
        return response
  
    except Exception as e:
        MemberGetMemberException(
            request=request,
            message=str(e)
        )