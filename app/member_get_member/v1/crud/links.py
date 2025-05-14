from sqlalchemy.ext.asyncio import AsyncSession
from app.apps.member_get_member.v1.models.links import MGM_Links,MGM_ClickTracking
from app.apps.member_get_member.v1.schemas.links import LinkCountResponse
from app.apps.member_get_member.v1.models.members import MGM_Members
from sqlalchemy.future import select
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List
import uuid
from app.src.crud import exists_in,search_value

async def _register_links(member_id : uuid, session: AsyncSession):
    link = MGM_Links.create_with_url(member_id)
    session.add(link)
    return link

async def create_links(members : List[MGM_Members], session : AsyncSession):
    links_response = []
    for member in members:
        response = await _register_links(member.id,session)
        links_response.append(response)
    return links_response

async def get_link_schema_by_member_id(member_id:uuid,session:AsyncSession)->MGM_Links:
    response = await search_value(
        model=MGM_Links,value=member_id,column_name='member_id',session=session
    )
    return response

async def _click_count(link_id : str, session : AsyncSession):
    query = (
        select(func.count(MGM_ClickTracking.id))
        .where(MGM_ClickTracking.link_id == link_id)
    )
    result = await session.execute(query)
    click_count = result.scalar()  # Retorna a contagem como um inteiro
    return click_count

async def get_click_count(member_id : str, session : AsyncSession):
    try:
        async with session.begin():
            member_uuid = uuid.UUID(member_id)
            link_schema = await get_link_schema_by_member_id(member_id=member_uuid,session=session)
            click_count = await _click_count(link_id=link_schema[0].id,session=session)
            response = LinkCountResponse(link_id=link_schema[0].id,count=click_count)
            return response
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error: {e}"
        )

async def set_click_tracking(promotor_id : str, session: AsyncSession):
    try:
        async with session.begin():
            member_uuid = uuid.UUID(promotor_id)
            exists = await exists_in(model=MGM_Members,items=[member_uuid],column_name='id',session=session)
            if exists == []:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="promotor_id not found.")
            link_schema = await get_link_schema_by_member_id(member_uuid,session=session)
            traking_schema  = MGM_ClickTracking(link_id=link_schema[0].id)
            session.add(traking_schema)
            return HTTPException(status_code=status.HTTP_200_OK,detail="successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro: {e}"
        )