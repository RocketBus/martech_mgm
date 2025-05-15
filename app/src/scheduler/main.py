import pandas as pd
from typing import List
from io import StringIO
from datetime import datetime
from fastapi import Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.utils import decode_base64
from app.src.clickbus.clickbus import Orders
from app.config.settings import environment_secrets,ENVIRONMENT_LOCAL,VOUCHER_MOCK
from app.src.salesForce.sales_force import SFTPUploader

from app.member_get_member.v2.schema.vouchers import Voucher
from app.member_get_member.v2.crud.invitations import set_stage
from app.member_get_member.v2.crud.vouchers import set_voucher
from app.member_get_member.v2.crud.promoter import get_member
from app.member_get_member.v2.crud.purchase import update_orders_departured
from app.member_get_member.v2.exeptions.exceptions import MemberGetMemberException


async def mgm_departure_invited(orders : List[str], session : AsyncSession, request : Request):
    clickbus_order = Orders()
    sftp_conn:SFTPUploader = SFTPUploader(
        host=environment_secrets['SALES_FORCE_SFTP_HOST'],
        username=environment_secrets['SALES_FORCE_SFTP_USERNAME'],
        password=environment_secrets['SALES_FORCE_SFTP_PASSWORD']
    )

    results  = []
    try:
        async with session.begin():
            for order in orders:
                order_response = await clickbus_order.get_order(order_id=order)
                order_is_valid = await clickbus_order.status_order_is_valid(order_response.json())
                response = await  update_orders_departured(
                    order_id=order,
                    succes_or_fail=order_is_valid,
                    session=session
                )
                
                if not order_is_valid:
                    continue
                
                member = await get_member(value=response.promoter_id,column_name="id",session=session,request=request)
                
                voucer_response = await set_voucher(
                    member=member,
                    session=session,
                    is_promoter=True
                )
                
                await set_stage(
                    invited_id=response.invited_id,
                    promoter_link_id=member.link.link_id,
                    stage="guest_boarded",
                    session=session
                )
                
                promoter_response = {
                    "Email do comprador":member.email,
                    "Link":member.link.link,
                    "Código":voucer_response.code,
                    "Valor":"20,00",
                    "Validade":datetime.strptime(voucer_response.end_at,'%Y-%m-%d %H:%M:%S').strftime("%D %X")
                }
                
                
                results.append(promoter_response)
            
            df = pd.DataFrame(results)
            if df.empty:
                e = 'Nenhuma order válida.'
                return
         
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            
            sftp_conn.connect()
            sftp_conn.upload_csv(
                csv_data_io=csv_buffer,
                remote_path='/Import/membergetmember/promoters/cupom/promoters_cupom.csv'
            )
            sftp_conn.disconnect()
            success = True
            return 
    except (Exception,HTTPException) as e:
            raise MemberGetMemberException(message=str(e),request=request)
