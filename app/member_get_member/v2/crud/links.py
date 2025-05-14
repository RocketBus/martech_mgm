import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select

from app.src.database import crud
from app.member_get_member.v2.models.members import MGM_Members
from app.member_get_member.v2.models.links import MGM_Links,MGM_ClickTracking


async def _register_link(member_id : uuid, session: AsyncSession):
    link = MGM_Links.create_with_url(member_id)
    session.add(link)
    return link

async def _click_count(link_id : str, session : AsyncSession):
    query = (
        select(func.count(MGM_ClickTracking.id))
        .where(MGM_ClickTracking.link_id == link_id)
    )
    result = await session.execute(query)
    click_count = result.scalar()  # Retorna a contagem como um inteiro
    return click_count


async def create_link(member : MGM_Members, session : AsyncSession):
    response = await _register_link(member.id,session)
    return response


async def get_link_schema_by_member_id(member_id:uuid,session:AsyncSession)->MGM_Links:
    response = await crud.search_value(
        model=MGM_Links,value=member_id,column_name='member_id',session=session
    )
    return response