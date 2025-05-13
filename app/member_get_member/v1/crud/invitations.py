from app.apps.member_get_member.v1.models.invitations import MGM_Invitations
from app.apps.member_get_member.v1.schemas.invitations import StageCount,InputType

from fastapi import HTTPException, status
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select 
from sqlalchemy import func

async def count_stages(link_id:uuid.UUID,session:AsyncSession):
    stmt = (
        select(MGM_Invitations.stage, func.count(MGM_Invitations.stage))
        .group_by(MGM_Invitations.stage)
    ).where(MGM_Invitations.link_id==link_id)

    results = await session.execute(stmt)
    counts = {row[0]: row[1] for row in results.all()}
    for stage in InputType:
        counts.setdefault(stage.value, 0)
    return counts



async def set_stage(invited_id:uuid.UUID,promoter_link_id:uuid.UUID,stage:str,session:AsyncSession) -> MGM_Invitations:
    try:
        schema = MGM_Invitations(
            stage=stage,
            member_id=invited_id,
            link_id=promoter_link_id
        )
        session.add(schema)
        await session.flush()
        return schema
  
    except Exception as e:
        raise e