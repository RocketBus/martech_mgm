from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid
from enum import Enum
from typing import List
from app.services.clickbus.cupons import VoucherMicroservice
from app.config.settings import environment_secrets,ENVIRONMENT_LOCAL
from app.src.utils import generate_token,future_date,datetime_now
from fastapi import HTTPException, status
import base64

def mgm_code_renerator():
    code = generate_token(7).upper()
    return f"MGM_{code}"


def set_start_at():
    now = datetime_now(True)
    return now.strftime("%Y-%m-%d %H:%M:%S")

def set_end_at():
    end = future_date(5)
    return end.strftime("%Y-%m-%d %H:%M:%S")
    
class VoucherBase(SQLModel):
    voucher_id: str
    code: str
    end_at: str

    def code_to_base64(self):
        voucher_b = self.voucher_id.encode('utf-8')
        base64_bytes = base64.b64encode(voucher_b)
        base64_voucher_id = base64_bytes.decode('utf-8')
        self.voucher_id = base64_voucher_id
        return self

class VoucherEmail(SQLModel):
    email : str
    quantity : int


class Voucher(SQLModel):
    voucher_id : str = None
    discount_id: str = environment_secrets['MGM_DISCOUNT_ID_INVITED']
    code: str = Field(default_factory=mgm_code_renerator)
    campaign_name: str = environment_secrets['MGM_VOUCHER_CAMPAIGN_INDICADO']
    quantity: int = 1
    start_at: str = Field(default_factory=set_start_at)
    end_at: str = Field(default_factory=set_end_at)  # Data final do cupom (A negociar na politica)
    only_logged_user: bool = True
    is_round_trip: bool = False
    is_active: bool = True
    is_first_purchase: bool = True
    origin:str =  "8"
    email: List[VoucherEmail] = Field(default_factory=list)

    def create(self,is_promoter:bool,email:str):
        if is_promoter:
            self.campaign_name = environment_secrets['MGM_VOUCHER_CAMPAIGN_PROMOTOR']
            self.discount_id = environment_secrets['MGM_DISCOUNT_ID_PROMOTER']
            self.is_first_purchase = False
            self.end_at = future_date(30).strftime("%Y-%m-%d %H:%M:%S")
        if ENVIRONMENT_LOCAL == 'dev':
            self.is_active = False
        
        self.email.append(VoucherEmail(
            email=email,
            quantity=1
        ))
        
        voucher = VoucherMicroservice()
        status_code,response = voucher.create_voucher(
            payload=self.dict()
        )
        
        if status_code != 201:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response['error']
            )
        
        self.voucher_id = response['id']
        return VoucherBase(
            voucher_id=self.voucher_id,
            code=self.code,
            end_at=self.end_at
        )