from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid
from enum import Enum
from typing import List
import base64

from app.src.utils import encode_base64
from app.apps.member_get_member.v1.schemas.vouchers import VoucherBase
# from app.services.clickbus.cupons import VoucherMicroservice
# from app.config.settings import MGM_DISCOUNT_ID,MGM_VOUCHER_CAMPAIGN_INDICADO
# from app.src.utils import generate_token,future_date
# from fastapi import HTTPException, status


class InputType(str, Enum):
    INNER_BASE = 'inner base'
    MANUALLY = 'manually'
    THROUGH_CAMPAIGN = 'through campaign'
    NEW_USER = 'new user'
    EXTERNAL_BASE = 'external base'
    INVATED = "invited"

class CreateBase(SQLModel):
    email: str = Field(unique=True)  
    user_id : str
    input_type: InputType 
    
class MembersBase(CreateBase):
    is_promoter : bool
    was_invited : bool = False
    
class MembersCreate(CreateBase):
    
    def set_promoter(self, is_promoter: bool) -> MembersBase:
        
        return MembersBase(
            **self.dict(), 
            is_promoter=is_promoter,
            was_invited=False if is_promoter else True
        )

class MemberLinkResponse(SQLModel):
    link_id: uuid.UUID
    link : str

class MembersResponse(MembersBase):
    id: uuid.UUID
    decode_user_id: int
    created_at: datetime = Field(default_factory=datetime.now)
    link : MemberLinkResponse

    class Config:
        orm_mode = True
    
    def id_to_uuid(id: str) -> uuid.UUID:
        return uuid.UUID(id)
    
    
    def encode_email_to_base64(email):
        return encode_base64(email)


    def to_base64(self):
        self.email = encode_base64(self.email)
        # self.decode_user_id = self.user_id
        return self


# class InvitedEmail(SQLModel):
#     email : str
#     quantity : int
    
# class InvitedVoucher(SQLModel):
#     discount_id: str = MGM_DISCOUNT_ID
#     code: str = Field(default_factory=generate_token)
#     campaign_name: str = MGM_VOUCHER_CAMPAIGN_INDICADO
#     quantity: int = 1
#     start_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#     end_at: str = Field(default_factory=lambda: future_date(5).strftime("%Y-%m-%d %H:%M:%S"))  # Data final do cupom (A negociar na politica)
#     only_logged_user: bool = True
#     is_round_trip: bool = False
#     is_active: bool = True
#     is_first_purchase: bool = True
#     email: List[InvitedEmail]

#     def create(self):
#         voucher = VoucherMicroservice()
#         status_code,response = voucher.create_voucher(
#             payload=self.dict()
#         )
        
#         if status_code != 201:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=response['error']
#             )
#         return
    
class InvitedResponse(SQLModel):
    invited:MembersResponse
    voucher:VoucherBase
    
    def to_base64(self):
        self.invited = self.invited.to_base64()
        self.voucher = self.voucher.code_to_base64()
        return self