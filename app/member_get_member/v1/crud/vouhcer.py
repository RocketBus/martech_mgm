from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import uuid

from app.apps.member_get_member.v1.schemas.vouchers import VoucherBase
from app.apps.member_get_member.v1.models.voucher import MGM_vouchers

async def set_voucher(voucher:VoucherBase,member_id:uuid.UUID,session:AsyncSession):
    try:
        voucher_invited = MGM_vouchers(
            voucher_id=voucher.voucher_id,
            code=voucher.code,
            end_at=voucher.end_at,
            member_id=member_id
        )
        session.add(voucher_invited)
        return voucher_invited
   
    except Exception as e:
        
        raise e