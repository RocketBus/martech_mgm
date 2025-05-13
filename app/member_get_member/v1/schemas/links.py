from typing import List, Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
from app.apps.member_get_member.v1.models.links import MGM_Links,MGM_ClickTracking
import uuid
    
class LinkCountResponse(SQLModel):
    link_id : uuid.UUID
    count : int
    
class LinkIdResponse(SQLModel):
    link_id : str
    url : str
    
