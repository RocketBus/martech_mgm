from sqlmodel import Field, SQLModel
import uuid
    
class LinkCountResponse(SQLModel):
    link_id : uuid.UUID
    count : int
    
class LinkIdResponse(SQLModel):
    link_id : str
    url : str
