from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

import uuid
import asyncio
from typing import List

from app.member_get_member.v2.schema.member import CreateBase,MembersResponse
from app.member_get_member.v2.exeptions.exceptions import MemberAlreadyExists,MemberGetMemberException
from app.auth.auth_bearer import JWTBearer
from app.src.database import crud
from app.member_get_member.v2.crud.members import set_member
from app.database.db import get_session

router = APIRouter()

router_configs = {
    "dependencies": [Depends(JWTBearer(token_types=["access", "refresh"]))]
}

tag_prefix = "[ Member get member ]"

@router.post(
    "/promoter",
    response_model=MembersResponse,
    tags=[f"{tag_prefix} create"],
    **router_configs
)
async def create_promoter(
    member: CreateBase,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    try:
    
        async with session.begin():
            response = await set_member(member=member,is_promoter=True,session=session)
        return response.to_base64()
    
    except IntegrityError as e:
        MemberAlreadyExists(request=request,error_message=str(e.orig).lower(),notify_slack=True)
        
    except Exception as e:
        MemberGetMemberException(request=request, message=str(e))
    
