from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import uuid
from app.database.db import get_session
from app.auth.auth_bearer import JWTBearer
from app.member_get_member.v2.schema.member import CreateBase, MembersResponse, InvitedResponse, VoucherBase
from app.member_get_member.v2.models.members import MGM_Members
from app.member_get_member.v2.models.links import MGM_Links
from app.member_get_member.v2.crud.members import set_member
from app.member_get_member.v2.crud.vouchers import set_voucher
from app.member_get_member.v2.crud.invitations import set_stage
from app.member_get_member.v2.exeptions.exceptions import MemberAlreadyExists, MemberGetMemberException
from app.src.database import crud

# Criação do roteador da API
router = APIRouter()

# Configuração padrão para rotas protegidas com autenticação JWT
router_configs = {
    "dependencies": [Depends(JWTBearer(token_types=["access", "refresh"]))]
}

# Prefixo usado para nomear as tags da rota
tag_prefix = "[ Member get member ]"

@router.post(
    "/invited/{promoter_id}",
    response_model=InvitedResponse,
    tags=[f"{tag_prefix} create"],
    **router_configs
)
async def create_invited(
    promoter_id: uuid.UUID,
    member: CreateBase,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """
# Create Invited Member

Cria um member convidado no programa **Member Get Member**.

#### Etapas:

1. Cria o member utilizando os dados fornecidos.
2. Gera um voucher associado ao novo member.

   > Obs: em ambiente de `dev`, a geração do voucher não está disponível.
3. Registra o estágio `"guest_registered"` para o member convidado.

Em caso de erro de integridade (por exemplo, se o member já existir), uma exceção personalizada é lançada.

#### Parâmetros:

* **promoter\_id** (str): ID do member proprietário do link de indicação acessado.
* **member** (CreateBase): Dados do novo member.
* **request** (Request): Objeto da requisição, utilizado para logging e monitoramento.
* **session** (AsyncSession): Sessão assíncrona com o banco de dados.

#### Retorno:

* **MembersResponse**: Dados do member criado. Informações sensíveis são codificadas em base64.

#### Exceções:

* **MemberAlreadyExists**: Lançada se o member já existir no banco de dados.
* **MemberGetMemberException**: Lançada para erros não tratados.

    """
    try:
        stage = "guest_registered"

        # Início da transação
        async with session.begin():
            
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
            # Criação do membro (não é um promotor neste contexto)
            member_schema = await set_member(member=member, is_promoter=False, session=session)
            await session.flush()  # Garante que o ID e outros valores sejam atualizados
            # Geração do voucher associado ao membro
            voucher_response = await set_voucher(member=member_schema, session=session)
            await session.flush()  # Garante que o ID e outros valores sejam atualizados
            # Registro do estágio atual do membro convidado
            await set_stage(
                invited_id=member_schema.id,
                promoter_link_id=promoter_link[0].id,
                stage=stage,
                session=session
            )
            
            voucher_schema = VoucherBase(
                voucher_id=voucher_response.voucher_id,
                code=voucher_response.code,
                end_at=voucher_response.end_at
            )
            
            response = InvitedResponse(
                invited=member_schema.to_base64(),
                voucher=voucher_schema.to_base64()
            )

            # Retorno dos dados do membro em formato codificado
            return response

    # Tratamento para erros de duplicidade (membro já existente)
    except IntegrityError as e:
        MemberAlreadyExists(
            request=request,
            error_message=str(e.orig).lower(),
            notify_slack=True
        )

    # Tratamento genérico para outros tipos de exceção
    except Exception as e:
        MemberGetMemberException(
            request=request,
            message=str(e)
        )
