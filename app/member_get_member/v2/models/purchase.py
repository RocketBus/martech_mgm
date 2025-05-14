from sqlmodel import Field
from datetime import datetime
import uuid
from app.member_get_member.v2.schema.purchase import PurchaseBase
from typing import Optional

class MGM_Purchases(PurchaseBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)  # ID único
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
