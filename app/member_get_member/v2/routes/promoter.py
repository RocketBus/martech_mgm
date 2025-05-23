from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List
from app.database.db import get_session

from app.auth.auth_bearer import JWTBearer
from app.member_get_member.v2.crud.members import set_member
from app.member_get_member.v2.crud.promoter import get_vouchers_by_member_id,delete_member
from app.member_get_member.v2.schema.member import (
    CreateBase,
    MembersResponse
    )
from app.src.utils import decode_base64
from app.member_get_member.v2.models.members import MGM_Members
from app.member_get_member.v2.schema.vouchers import VoucherBase
from app.member_get_member.v2.exeptions.exceptions import MemberAlreadyExists, MemberGetMemberException


# Inicializa o roteador da aplicação
router = APIRouter()

# Configura dependências comuns a todos os endpoints do router
router_configs = {
    "dependencies": [Depends(JWTBearer(token_types=["access", "refresh"]))]
}

# Prefixo padrão para identificação dos endpoints no Swagger
tag_prefix = "[ Member get member ]"

@router.post(
    "/promoter",
    response_model=MembersResponse,
    tags=[f"{tag_prefix} create"],
    **router_configs
)
async def create_promoter(
    member: CreateBase,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """
    Endpoint para criação de um member do tipo promotor no programa Member Get Member.

    A função:
    - Valida autenticação via JWTBearer.
    - Cria o member como promotor, salvando os dados no banco de forma transacional.
    - Retorna a resposta codificada em base64 com os dados do member.
    
    o campo de email no payload precisa estar em `base64`

    Args:
        member (CreateBase): Dados recebidos no corpo da requisição.
        request (Request): Objeto de requisição FastAPI, usado em exceções.
        session (AsyncSession): Sessão de banco de dados injetada via dependência.

    Returns:
        MembersResponse: Objeto com os dados do member criado, codificados com `to_base64()`.

    Raises:
        MemberAlreadyExists: Exceção tratada para members duplicados (via `IntegrityError`).
        MemberGetMemberException: Exceção genérica para outros erros.
    """
    try:
        # Inicia a transação assíncrona para persistir os dados do promotor
        async with session.begin():
            member_email = member.email
            decode_email = decode_base64(member_email)
            member.email = decode_email
            # raise
            response = await set_member(member=member, is_promoter=True, session=session)

        # Retorna a resposta formatada (codificada em base64)
        return response.to_base64()

    except IntegrityError as e:
        # Caso o e-mail já exista no banco, lança exceção customizada
        MemberAlreadyExists(request=request, error_message=str(e.orig).lower(), notify_slack=True)

    except Exception as e:
        # Trata exceções genéricas, com logging e rastreamento
        MemberGetMemberException(request=request, message=str(e))

@router.delete(
    "/member/delete/{email}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=[f"{tag_prefix} delete"],
    **router_configs
)
async def delete_member_by_email(
    email: str,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    try:
        async with session.begin():
            await delete_member(email=email, session=session, request=request)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        raise MemberGetMemberException(request=request, message=str(e))

@router.get(
    "/member/vouchers/email/{email}",
    # response_model=List[VoucherBase],
    tags=[f"{tag_prefix} information by"],
    **router_configs
)
async def get_vouchers_by_email(
    email : str,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    vouchers = await get_vouchers_by_member_id(value=email,column_name='email', session=session, request=request)
    return vouchers


@router.get(
    "/member/vouchers/user_id/{user_id}",
    response_model=List[VoucherBase],
    tags=[f"{tag_prefix} information by"],
    **router_configs
)
async def get_vouchers_by_user_id(
    user_id : str,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    vouchers = await get_vouchers_by_member_id(value=user_id,column_name='user_id', session=session, request=request)
    return vouchers