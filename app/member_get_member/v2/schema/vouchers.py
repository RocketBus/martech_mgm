from sqlmodel import SQLModel, Field
import uuid
from typing import List
from app.src.clickbus.cupons import VoucherMicroservice
from app.config.settings import environment_secrets,ENVIRONMENT_LOCAL
from app.src.utils import generate_token,future_date,datetime_now,encode_base64
from fastapi import HTTPException, status


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
    discount_id : str
    code: str
    campaign_name: str = Field(default="MGM_INDICADO")
    end_at: str

    def to_base64(self):
        """Retorna uma nova instância com os campos codificados em base64."""
        return  VoucherBase(
            voucher_id=encode_base64(self.voucher_id),
            discount_id=encode_base64(self.discount_id),
            code=encode_base64(self.code),
            campaign_name=self.campaign_name,
            end_at=self.end_at
        )
    
class DiscountBase(SQLModel):
    fixedValue: bool
    minPurchaseValue: float
    maxDiscountValue: float
    value: float

class VoucherBaseResponse(SQLModel):
    voucher: VoucherBase
    discount: DiscountBase
    

class VoucherEmail(SQLModel):
    email : str
    quantity : int


class Voucher(SQLModel):
    voucher_id : str = "e5ddcb30-a215-4100-824f-a7814c2469c4"
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


    def _create_voucher(self):
        voucher = VoucherMicroservice()
        status_code,response = voucher.create_voucher(
            payload=self.dict()
        )
        if status_code != 201:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response['error']
            )
        return response

    
    def _get_voucher(self,voucher_id:str = None):
        if voucher_id is None:
            voucher_id = self.voucher_id
        ms = VoucherMicroservice()
        status,response = ms.get_voucher_by_id(voucher_id=self.voucher_id)
        if status != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response['error']
            )
        return response
   
        
    def create(self,is_promoter:bool,email:str) ->VoucherBase:
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
        
        response = self._create_voucher()
        
        self.voucher_id = response['id']
        return VoucherBase(
            voucher_id=self.voucher_id,
            discount_id=self.discount_id,
            campaign_name=self.campaign_name,
            code=self.code,
            end_at=self.end_at
        )
