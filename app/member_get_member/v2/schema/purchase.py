from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class CreatePurchase(SQLModel):
    invited_id : uuid.UUID = Field(foreign_key="mgm_members.id")  # FK para membro
    order_id : str

class PurchaseBase(SQLModel):
    departure : bool
    order_id : str
    status : str
    invited_id : uuid.UUID
    promoter_id : uuid.UUID
    departure_time : datetime
    

    