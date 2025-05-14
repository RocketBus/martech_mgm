from sqlmodel import Field
from datetime import datetime
import uuid
from app.apps.member_get_member.v1.schemas.invitations import InvitationsBase
from typing import Optional

class MGM_Invitations(InvitationsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)  # ID único
    member_id: uuid.UUID = Field(foreign_key="mgm_members.id")  # FK para membro
    link_id: uuid.UUID = Field(foreign_key="mgm_links.id")  # FK para link
    create_at: Optional[datetime] = Field(default_factory=datetime.now)
