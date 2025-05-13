from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

import uuid
import asyncio
from typing import List

from app.member_get_member.v2.schema.member import CreateBase,MembersResponse,MembersBase
from app.member_get_member.v2.models.members import MGM_Members
from app.database.db import get_session
from app.auth.auth_bearer import JWTBearer

from app.src.database import crud

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
    search = await crud.search_value(
        model=MGM_Members,
        value=member.user_id,
        column_name="user_id",
        session=session,
        
    )
    
    if search:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists."
        )
    
    schema = MembersBase(**member.dict(),is_promoter=True)
    pass