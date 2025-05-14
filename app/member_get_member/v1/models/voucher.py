from sqlmodel import Field
from datetime import datetime
import uuid
from app.apps.member_get_member.v1.schemas.vouchers import VoucherBase
from typing import Optional


class MGM_vouchers(VoucherBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)  # ID único
    member_id: uuid.UUID = Field(foreign_key="mgm_members.id")  # FK para membro
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
