from enum import Enum
from sqlmodel import SQLModel
import uuid

class InputType(str, Enum):
    GUEST_REGISTERED = "guest_registered"  # Convidado cadastrado
    SELECTED_TICKET = "selected_ticket"  # Escolheu passagem
    APPLIED_COUPON = "applied_coupon"  # Inseriu cupom
    COMPLETED_PURCHASE = "completed_purchase"  # Finalizou compra
    PURCHASE_APPROVED = "purchase_approved"  # Compra aprovada
    GUEST_BOARDED = "guest_boarded"  # Convidado embarcou

class InvitationsBase(SQLModel):
    stage: InputType  # Tipo de estágio da entrada, baseado em InputType

class CreateStages(SQLModel):
    invited_id : str
    stage : InputType
    
class StageCount(SQLModel):
    stage: InputType
    count: int
