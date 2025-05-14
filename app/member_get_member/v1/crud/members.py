from sqlalchemy.ext.asyncio import AsyncSession
from app.apps.member_get_member.v1.models.members import MGM_Members
from app.apps.member_get_member.v1.models.links import MGM_Links
from app.apps.member_get_member.v1.models.invitations import MGM_Invitations
from app.apps.member_get_member.v1.schemas.members import MembersCreate,MembersResponse,MemberLinkResponse
from fastapi import HTTPException, status
from typing import List
import uuid
import asyncio
from app.src.crud import exists_in,search_value
from app.apps.member_get_member.v1.crud.links import get_link_schema_by_member_id
from app.src.utils import datetime_now
from datetime import datetime

async def _create_schema(member:MembersCreate,is_promoter : bool)->MGM_Members:
    response = member.set_promoter(is_promoter)
    return MGM_Members(**response.dict())

async def get_member_by_user_id(user_id:str,session:AsyncSession)->MGM_Members:
    response = await search_value(
        model=MGM_Members,value=user_id,column_name='user_id',session=session
    )
    return response

async def _get_new_members(members_schema:List[MGM_Members],session:AsyncSession)->MGM_Members:
    emails_list = [member.email for member in members_schema]
    members_exists = await exists_in(
        model=MGM_Members,items=emails_list,column_name='email',session=session
    )
    
    if len(members_exists) == 0:
        return members_schema
    elif len(members_exists) == len(members_schema):
        return None
   
    new_members = [member for member in members_schema if member.email not in members_exists]
    return new_members


async def _create_link(member:MGM_Members)->MGM_Links:
    return MGM_Links.create_with_url(member.id)

async def set_members(members:MembersCreate,is_promoter : bool,session:AsyncSession)->MGM_Members:
    
    try:
        members_tasks = [_create_schema(member,is_promoter) for member in members]
        members_schema = await asyncio.gather(*members_tasks)
    
        new_members = await _get_new_members(members_schema,session)
        if not new_members:
            return None
        session.add_all(new_members)
        await session.flush()
        
        links_tasks = [_create_link(member) for member in new_members]
        links_schema = await asyncio.gather(*links_tasks)
        session.add_all(links_schema)
        
        return new_members
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def create_member_response_schema(member : MGM_Members,session : AsyncSession)->MembersResponse:
 
    link_schema = await get_link_schema_by_member_id(member_id=member.id,session=session)
    link_schema= link_schema[0]
    link_response_schema = MemberLinkResponse(
        link_id=link_schema.id,
        link=link_schema.url
    )
    member_response_schema = MembersResponse(
        **member.dict(),
        link=link_response_schema
    ).to_base64()
    return member_response_schema

async def get_member_by_promoter(is_promoter : bool, session : AsyncSession):
    response = await search_value(
        model=MGM_Members,
        value=is_promoter,
        column_name="is_promoter",
        session=session
    )
    return response

async def get_member_by_id(member_id:uuid.UUID,session : AsyncSession):
    response = await search_value(
            model=MGM_Members,
            value=member_id,
            column_name="id",
            session=session
        )
    return await get_member_response(response,session)


async def get_member_my_email(email:str, session: AsyncSession):
    response = await search_value(
        model=MGM_Members,
        value=email,
        column_name="email",
        session=session
    )
    return await get_member_response(response,session)

async def get_member_response(member:MGM_Members,session:AsyncSession):
    if len(member) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Member does not exist yet.'
            )
    return await create_member_response_schema(
        member=member[0],
        session=session
    )