from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from sqlmodel import select, and_, update
import uuid

from app.member_get_member.v2.models.members import MGM_Members
from app.member_get_member.v2.models.links import MGM_Links
from app.member_get_member.v2.models.vouchers import MGM_vouchers
from app.member_get_member.v2.schema.vouchers import VoucherBase,Voucher,VoucherBaseResponse,DiscountBase
from app.member_get_member.v2.exeptions.exceptions import MemberGetMemberException
from app.member_get_member.v2.schema.member import (
    MemberLinkResponse,
    MembersResponse
    )
from app.member_get_member.v2.crud.links import get_link_schema_by_member_id
from app.src.database import crud
from app.config.settings import environment_secrets,ENVIRONMENT_LOCAL


async def get_promoter_link_id_by_promoter_id(promoter_id:uuid.UUID,session:AsyncSession,request:Request)->uuid.UUID:
    promoter_link = await crud.search_value(
        model=MGM_Links,
        value=promoter_id,
        column_name="member_id",
        session=session
    )
    if not promoter_link:
        MemberGetMemberException(
            request=request,
            message="Promoter_id not found",
            status_code=404
        )
    return promoter_link[0].id

async def get_vouchers_by_member_id(value:str, column_name:str, session:AsyncSession, request:Request):
    member = await crud.search_value(model=MGM_Members, value=value, column_name=column_name, session=session)
    if not member:
        MemberGetMemberException(
            request=request,
            message="Member not found",
            status_code=404
        )   
    member_id = member[0].id
    vouchers = await crud.search_value(model=MGM_vouchers, value=member_id, column_name="member_id", session=session)
    if not vouchers:
        MemberGetMemberException(
            request=request,
            message="Vouchers not found",
            status_code=404
        )
        
    schema = Voucher()
    response = []
    for voucher in vouchers:
        voucher_base_schema = VoucherBase(**voucher.dict())
        if ENVIRONMENT_LOCAL == 'prod':
            data = schema._get_voucher(voucher_id=voucher.discount_id)
            discount_response = data['discount']
            discount_base_schema = DiscountBase(
                fixedValue=discount_response['fixedValue'],
                minPurchaseValue=discount_response['minPurchaseValue'],
                maxDiscountValue=discount_response['maxDiscountValue'],
                value=discount_response['value']
            )
        if ENVIRONMENT_LOCAL == 'dev':
            discount_base_schema = DiscountBase(
                fixedValue=True,
                minPurchaseValue=0,
                maxDiscountValue=20,
                value=20
            
            )
        response.append(
            VoucherBaseResponse(
                voucher=voucher_base_schema.to_base64(),
                discount=discount_base_schema
            )
        )
    return response

async def get_member(value:str,column_name:str,session:AsyncSession,request:Request)->MGM_Members:
    mgm_member = await crud.search_value(
        model=MGM_Members,value=value,column_name=column_name,session=session
    )
    if not mgm_member:
        MemberGetMemberException(request=request, message="Member not found",notify_slack=False,status_code=status.HTTP_404_NOT_FOUND)

    link_schema = await get_link_schema_by_member_id(mgm_member[0].id,session)
    if not link_schema:
        MemberGetMemberException(request=request, message="Link not found",notify_slack=False)
    
    link_response = MemberLinkResponse(
        link_id=link_schema[0].id,
        link=link_schema[0].url
    )
    
    response = MembersResponse(
        **mgm_member[0].dict(),
        link=link_response,
    )
    
    return response