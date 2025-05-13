from sqlmodel import Field
from datetime import datetime
import uuid
from app.apps.member_get_member.v1.schemas.purchases import PurchasesBase
from typing import Optional

class MGM_Purchases(PurchasesBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)  # ID único
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
