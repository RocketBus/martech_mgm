import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.database import crud
from app.member_get_member.v2.models.members import MGM_Members
from app.member_get_member.v2.models.links import MGM_Links
from app.member_get_member.v2.crud.links import create_link,get_link_schema_by_member_id
from app.member_get_member.v2.schema.member import (
    MembersBase,
    CreateBase,
    MemberLinkResponse,
    MembersResponse
    )


async def get_member_by_id(id:uuid,session:AsyncSession):
    member = await crud.search_value(
        model=MGM_Members,value=id,column_name='id',session=session
    )
    return member


async def get_member_by_user_id(user_id:str,session:AsyncSession)->MGM_Members:
    member = await crud.search_value(
        model=MGM_Members,value=user_id,column_name='user_id',session=session
    )
    return member


async def set_member(member:CreateBase,is_promoter: bool,session:AsyncSession)-> MembersResponse:
    
    if is_promoter:
        schema = MembersBase(**member.dict(), is_promoter=True)
    else:
        schema = MembersBase(**member.dict(), was_invited=True)
        
    mgm_member = MGM_Members(**schema.dict())
    session.add(mgm_member)
    await session.flush()
    
    link_schema = await create_link(member=mgm_member,session=session)
    session.add(link_schema)
   
    link_response = MemberLinkResponse(
        link_id=link_schema.id,
        link=link_schema.url
    )
    
    response = MembersResponse(
        **mgm_member.dict(),
        link=link_response,
    )
    return response