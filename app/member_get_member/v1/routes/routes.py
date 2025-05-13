from typing import List, Dict
from datetime import datetime
import uuid
import asyncio

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.auth.auth_bearer import JWTBearer
from app.services.clickbus.clickbus import Orders
from app.src.crud import search_value

# CRUD imports
from app.apps.member_get_member.v1.crud.members import (
    set_members, get_member_my_email, get_member_by_promoter,
    create_member_response_schema, get_member_by_id,get_member_by_user_id
)
from app.apps.member_get_member.v1.crud.links import (
    set_click_tracking, get_click_count, get_link_schema_by_member_id
)
from app.apps.member_get_member.v1.crud.invitations import (
    set_stage, count_stages
)
from app.apps.member_get_member.v1.crud.purchases import (
    create_purchase, get_orders_departured, get_order_by_order
)
from app.apps.member_get_member.v1.crud.vouhcer import set_voucher
from app.src.crud import update_field

# Schema imports
from app.apps.member_get_member.v1.schemas.members import (
    MembersCreate, MembersResponse, InvitedResponse
)
from app.apps.member_get_member.v1.schemas.links import (
    LinkCountResponse, LinkIdResponse
)
from app.apps.member_get_member.v1.schemas.invitations import CreateStages
from app.apps.member_get_member.v1.schemas.purchases import CreatePurchase
from app.apps.member_get_member.v1.schemas.vouchers import Voucher,VoucherBase
from app.services.scheduler.scheduler import ActionScheduler

# Model imports
from app.apps.member_get_member.v1.models.members import MGM_Members
from app.apps.member_get_member.v1.models.invitations import MGM_Invitations
from app.apps.member_get_member.v1.models.purchases import MGM_Purchases

from app.apps.users.crud.request import request_log
from app.services.slack.slack import SlackAlerts

from app.apps.member_get_member.v1.exeptions.exceptions import MemberGetMemberException,MemberGetMemberUserDoesExists,MemberGetMemberInvitedExist

router = APIRouter()
router_configs = {
    "dependencies":[Depends(JWTBearer())]
}
tag_prefix = "[ Member get member ]"

@router.post("/create/promoter", response_model=List[MembersResponse], **router_configs,tags=[f"{tag_prefix} create"])
async def create_promoter(members: List[MembersCreate], request:Request, session: AsyncSession = Depends(get_session)):
    e = None
    try:
        async with session.begin():
            members_response = await set_members(members, True, session)
            if not members_response:
                response = []
                return response
            response_tasks = [create_member_response_schema(member, session) for member in members_response]
            response = await asyncio.gather(*response_tasks)
            return response
    except (Exception,HTTPException) as ex:
        print('Erro na criação de promoter:',e)
        e = ex
        raise MemberGetMemberException(message=str(e),request=request)
    finally:
        # Executar o request_log após os blocos except
        await request_log(
            request=request,
            campaign="MGM",
            details="Promoters created successfully." if 'response' in locals() else str(e),
            session=session
        )


@router.post("/create/invited/{promoter_id}",response_model=InvitedResponse, **router_configs,tags=[f"{tag_prefix} create"])
async def create_invited(member: MembersCreate, promoter_id : str, request : Request, session: AsyncSession = Depends(get_session)):
    e = None
    try:
        async with session.begin():
            members_response = await set_members([member],False,session)
            if not members_response:
                get_member = await get_member_my_email(email=member.email,session=session)
                if get_member.is_promoter:
                    raise MemberGetMemberInvitedExist(
                        status_code=status.HTTP_409_CONFLICT,
                        detail={"error": "Member cannot be registered as a guest because they are already an active promoter of the campaign"}
                    )
                
            stage = "guest_registered"
            
            voucher = Voucher()
            voucher_response = voucher.create(
                is_promoter=False,
                email=member.email
            )
            
            member_response_Schema = await create_member_response_schema(members_response[0],session)
            
            
            link_schema = await get_link_schema_by_member_id(
                member_id=uuid.UUID(promoter_id),
                session=session
            )
            
            await set_voucher(
                voucher=voucher_response,
                member_id=member_response_Schema.id,
                session=session
            )
            await set_stage(
                invited_id=member_response_Schema.id,
                promoter_link_id=link_schema[0].id,
                stage=stage,
                session=session
            )
            
            response = InvitedResponse(invited=member_response_Schema,voucher=voucher_response).to_base64()
            return response
    except MemberGetMemberInvitedExist as ex:
        e = ex
        raise ex
    except (Exception,HTTPException) as ex:
        e = ex
        raise MemberGetMemberException(message=str(e),request=request)
    
    finally:
        await request_log(
            request=request,
            campaign="MGM",
            details="Invited created successfully." if 'response' in locals() else str(e),
            session=session
        )    


@router.post("/set/invited/stages/{promoter_id}",response_model=MGM_Invitations, **router_configs,tags=[f"{tag_prefix} create"])
async def set_stages(stage : CreateStages, promoter_id , request:Request, session : AsyncSession = Depends(get_session)):
    try:
        async with session.begin():
            link_schema = await get_link_schema_by_member_id(
                member_id=uuid.UUID(promoter_id),
                session=session
            )
            if not link_schema:
                raise HTTPException(
                    status_code=500,
                    detail="promoter_id does not exist"
                )
                
            response = await set_stage(
                invited_id=uuid.UUID(stage.invited_id),
                promoter_link_id=link_schema[0].id,
                stage=stage.stage,
                session=session
            )
            return response    
    except (Exception,HTTPException) as ex:
        e = ex
        raise MemberGetMemberException(message=str(e),request=request)
    
    finally:
        await request_log(
            request=request,
            campaign="MGM",
            details="successfully." if 'response' in locals() else str(e),
            session=session
        )  


@router.post("/click/tracking/{promotor_id}",tags=[f"{tag_prefix} create"])
async def click_tracking(promotor_id:str,request : Request, session : AsyncSession = Depends(get_session)):
    e = None
    try:
        response =  await set_click_tracking(promotor_id=promotor_id,session=session)  
        return response
    except (Exception,HTTPException) as ex:
        e = ex
        raise MemberGetMemberException(message=str(e),request=request)
    
    finally:
        await request_log(
            request=request,
            campaign="MGM",
            details="successfully." if 'response' in locals() else str(e),
            session=session
        ) 


@router.patch("/accept/{invited_id}",response_model=MembersResponse, **router_configs,tags=[f"{tag_prefix} create"])
async def accept(invited_id : str,request : Request, session : AsyncSession = Depends(get_session)):
    e = None
    try:
        async with session.begin():
            response = await update_field(
                model=MGM_Members,
                where_column="id",
                where_value=uuid.UUID(invited_id),
                column_name_to_update="is_promoter",
                new_value=True,
                session=session
            )
            response = await create_member_response_schema(response,session)
            
            return response 
    except (Exception,HTTPException) as ex:
        e = ex
        raise MemberGetMemberException(message=str(e),request=request)
    
    finally:
        await request_log(
            request=request,
            campaign="MGM",
            details="successfully." if 'response' in locals() else str(e),
            session=session
        )  
        
        
@router.post("/puchases/{promoter_id}", response_model=MGM_Purchases, **router_configs,tags=[f"{tag_prefix} create"])
async def purchase(
    purchase : CreatePurchase, 
    promoter_id : uuid.UUID ,
    request : Request, 
    session : AsyncSession = Depends(get_session), 
    clickbus_orders:Orders = Depends(Orders),
    slack: SlackAlerts = Depends(SlackAlerts)
    ):
    e = None
    try:
        async with session.begin():
            order = await  clickbus_orders.get_order(purchase.order_id)
            order_response = order.json()
            departure_time = await clickbus_orders.get_departure_date(
                order_response=order_response
            )
            purchase_schema = await create_purchase(
                purchase=purchase,session=session,departure_time=departure_time,promoter_id=promoter_id
            )
            link_schema = await get_link_schema_by_member_id(
                member_id=promoter_id,
                session=session
            )
          
            if len(link_schema) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="promoter id not found."
                )
            await set_stage(
                invited_id=purchase.invited_id,
                promoter_link_id=link_schema[0].id,
                stage="purchase_approved",
                session=session
            )
            response = purchase_schema
            return response 
  
    except (Exception,HTTPException) as ex:
        e = ex
        raise MemberGetMemberException(message=str(e),request=request)
    finally:
        await request_log(
            request=request,
            campaign="MGM",
            details="successfully." if 'response' in locals() else str(e),
            session=session
        ) 


@router.get("/departured/voucher/", **router_configs,tags=[f"{tag_prefix} create"])
async def departure_vucher(
    request : Request,
    session : AsyncSession = Depends(get_session),
):
    try:
        e = None
        orders =  await get_orders_departured(session=session)
        if not orders:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='No orders found.'
            )
        scheduler = ActionScheduler()
        scheduler.activate()
        await scheduler.addJob(
            'mgm_departure_invited',{'orders':orders,'session':session,'request':request}
        )
        return HTTPException(
            status_code=200,
            detail="Processo iniado"
        )
    except (Exception) as ex:
        e = ex
        raise MemberGetMemberException(message=str(e),request=request)
    finally:
        await request_log(
            request=request,
            campaign="MGM",
            details="Automação de vouchers para rpomotores iniciada." if 'response' in locals() else str(e),
            session=session
        )  
    
        
@router.get("/members/{is_promoter}",response_model=List[MGM_Members], **router_configs,tags=[f"{tag_prefix} informations"])
async def get_members(is_promoter : bool ,request : Request, session : AsyncSession = Depends(get_session)):
    e = None
    try: 
        response =  await get_member_by_promoter(is_promoter=is_promoter,session=session)
        return response
    except (Exception,HTTPException) as ex:
        e = ex
        raise MemberGetMemberException(message=str(e),request=request)
    
    finally:
        await request_log(
            request=request,
            campaign="MGM",
            details="successfully" if 'response' in locals() else str(e),
            session=session
        ) 


@router.get("/member/{user_id}",response_model=MembersResponse,tags=[f"{tag_prefix} informations"])
async def get_by_user_id(user_id : str, request: Request, session : AsyncSession = Depends(get_session)):
    e = None
    data = {
        "request": request,
        "campaign": 'MGM',
        "session":session
    }
    try:
        user =  await get_member_by_user_id(user_id=user_id,session=session)
        if not user:
            detail = "user_id does not exist yet."
            await request_log(
                details=detail,
                **data
            )
            raise MemberGetMemberUserDoesExists(
                status_code=status.HTTP_200_OK,
                detail={
                    "status":400,"message":detail
                }
            )
        
        response = await create_member_response_schema(user[0],session)
        return response
    
    except MemberGetMemberUserDoesExists as ex:
        e = detail
        raise ex
    except (Exception,HTTPException) as ex:
        e = ex
        raise MemberGetMemberException(message=str(e),request=request)
    
    finally:
        await request_log(
            details="successfully." if 'response' in locals() else str(e),
            **data
        )   


@router.get("/link/id/{member_id}",response_model=LinkIdResponse, **router_configs,tags=[f"{tag_prefix} informations"])
async def get_link_by_member_id(member_id : str,request: Request, session : AsyncSession = Depends(get_session)):
    e = None
    try:
        member_uuid = uuid.UUID(member_id)
        link_schema =  await get_link_schema_by_member_id(member_uuid,session=session)
        response =  LinkIdResponse(link_id=str(link_schema[0].id),url=link_schema[0].url)
        return response
    
    except (Exception,HTTPException) as ex:
        e = ex
        raise MemberGetMemberException(message=str(e),request=request)
    finally:
        await request_log(
            request=request,
            campaign="MGM",
            details="successfully." if 'response' in locals() else str(e),
            session=session
        ) 


@router.get("/members/id/{id}",response_model=MembersResponse,**router_configs, tags=[f"{tag_prefix} informations"])
async def get_members_by_id(id : str,request: Request, session : AsyncSession = Depends(get_session)):
    e = None
    try:
        response = await get_member_by_id(member_id=uuid.UUID(id),session=session)
        return  response
    
    except (Exception,HTTPException) as ex:
        e = ex
        raise MemberGetMemberException(message=str(e),request=request)
    finally:
        await request_log(
            request=request,
            campaign="MGM",
            details="Invited created successfully." if 'response' in locals() else str(e),
            session=session
        ) 


@router.get("/members/email/{email}",response_model=MembersResponse,**router_configs, tags=[f"{tag_prefix} informations"])
async def get_members_by_email(email : str,request: Request, session : AsyncSession = Depends(get_session)):
    e = None
    try:
        member = await get_member_my_email(email=email,session=session)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Member does not exist yet.'
            )
        response =   MembersResponse.from_orm(member)
        return response
    
    except (Exception,HTTPException) as ex:
        e = ex
        raise MemberGetMemberException(message=str(e),request=request)
    finally:
        await request_log(
            request=request,
            campaign="MGM",
            details="successfully." if 'response' in locals() else str(e),
            session=session
        )


@router.get("/click/count/{member_id}",response_model=LinkCountResponse, **router_configs,tags=[f"{tag_prefix} reports"])
async def click_count(member_id : str,request: Request, session : AsyncSession = Depends(get_session)):
    e= None
    try:
        response =  await get_click_count(member_id= member_id, session=session)
        return response
    except (Exception,HTTPException) as ex:
        e = ex
        raise MemberGetMemberException(message=str(e),request=request)
    finally:
        await request_log(
            request=request,
            campaign="MGM",
            details="successfully." if 'response' in locals() else str(e),
            session=session
        )


@router.get("/reports/{promoter_id}",response_model= Dict[str,int],**router_configs,tags=[f"{tag_prefix} reports"])
async def get_promoter_reports(promoter_id : str,request: Request, session : AsyncSession = Depends(get_session)):
    e = None
    try:
        
        promoter_id = uuid.UUID(promoter_id)
        link_schema =  await get_link_schema_by_member_id(promoter_id,session=session)
        link_id = link_schema[0].id
        response =  await count_stages(link_id=link_id,session=session)
        return response
    except (Exception,HTTPException) as ex:
        e = ex
        raise MemberGetMemberException(message=str(e),request=request)
    finally:
        await request_log(
            request=request,
            campaign="MGM",
            details="successfully." if 'response' in locals() else str(e),
            session=session
        )