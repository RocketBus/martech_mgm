from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid
from typing import List, Optional
from app.apps.member_get_member.v1.schemas.members import MembersBase
from app.services.amplitude.amplitude import AmplitudeHashGenerator
import asyncio

amplitude = AmplitudeHashGenerator()

def decode_user_id_default(user_id: Optional[str]) -> Optional[int]:
    return amplitude.sync_decode(hash=user_id)

class MGM_Members(MembersBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    decode_user_id: Optional[int] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.user_id:
            self.decode_user_id = decode_user_id_default(self.user_id)