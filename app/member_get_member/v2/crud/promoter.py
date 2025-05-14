from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from sqlmodel import select, and_, update
import uuid

from app.member_get_member.v2.models.members import MGM_Members
from app.member_get_member.v2.models.links import MGM_Links
from app.member_get_member.v2.exeptions.exceptions import MemberGetMemberException
from app.member_get_member.v2.schema.member import (
    MemberLinkResponse,
    MembersResponse
    )
from app.member_get_member.v2.crud.links import get_link_schema_by_member_id
from app.src.database import crud


async def get_promoter_link_id_by_promoter_id(promoter_id:uuid.UUID,session:AsyncSession,request:Request)->MGM_Members:
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
    return promoter_link[0].id


async def get_member(value:str,column_name:str,session:AsyncSession,request:Request)->MGM_Members:
    mgm_member = await crud.search_value(
        model=MGM_Members,value=value,column_name=column_name,session=session
    )
    if not mgm_member:
        MemberGetMemberException(request=request, message="Member not found",notify_slack=False,status_code=status.HTTP_404_NOT_FOUND)

    link_schema = await get_link_schema_by_member_id(mgm_member[0].id,session)
    if not link_schema:
        MemberGetMemberException(request=request, message="Link not found",notify_slack=False)
    
    link_response = MemberLinkResponse(
        link_id=link_schema[0].id,
        link=link_schema[0].url
    )
    
    response = MembersResponse(
        **mgm_member[0].dict(),
        link=link_response,
    )
    
    return response