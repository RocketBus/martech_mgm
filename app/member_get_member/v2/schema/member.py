import uuid 
from enum import Enum
from datetime import datetime
from sqlmodel import SQLModel, Field

from app.src.utils import encode_base64

class InputType(str, Enum):
    INNER_BASE = 'inner base'
    MANUALLY = 'manually'
    INVITED = "invited"
    PROMOTER = "promoter"


class CreateBase(SQLModel):
    email: str = Field(unique=True)
    user_id : str = Field(unique=True)
    input_type: InputType 


class MembersBase(CreateBase):
    is_promoter : bool
    was_invited : bool = False

    
class MemberLinkResponse(SQLModel):
    link_id: uuid.UUID
    link : str


class MembersResponse(MembersBase):
    id: uuid.UUID
    decode_user_id: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    link : MemberLinkResponse


    class Config:
        orm_mode = True

    
    def id_to_uuid(id: str) -> uuid.UUID:
        return uuid.UUID(id)


    def to_base64(self):
        self.email = encode_base64(self.email)
        return self