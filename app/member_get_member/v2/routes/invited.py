from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import uuid
from app.database.db import get_session
from app.auth.auth_bearer import JWTBearer
from app.member_get_member.v2.schema.member import CreateBase, InvitedResponse, VoucherBase
from app.member_get_member.v2.schema.invitations import CreateStages
from app.member_get_member.v2.models.invitations import MGM_Invitations
from app.member_get_member.v2.models.links import MGM_Links
from app.member_get_member.v2.crud.members import set_member
from app.member_get_member.v2.crud.vouchers import set_voucher
from app.member_get_member.v2.crud.invitations import set_stage
from app.member_get_member.v2.crud.promoter import get_promoter_link_id_by_promoter_id
from app.member_get_member.v2.exeptions.exceptions import MemberAlreadyExists, MemberGetMemberException
from app.config.settings import ENVIRONMENT_LOCAL,VOUCHER_MOCK

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
3. Registra o estágio `"guest_registered"` para o member convidado.

Em caso de erro de integridade (por exemplo, se o member já existir), uma exceção personalizada é lançada.

#### Retorno:

* Os dados do convidado são codificado (`Base64`).

#### Exceções:

* **MemberAlreadyExists**: Lançada se o member já existir no banco de dados.
* **MemberGetMemberException**: Lançada para erros não tratados.

    """
    try:
        stage = "guest_registered"

        # Início da transação
        async with session.begin():
            
            promoter_link_id = await get_promoter_link_id_by_promoter_id(promoter_id=promoter_id,session=session,request=request)
            # Criação do membro (não é um promotor neste contexto)
            member_schema = await set_member(member=member, is_promoter=False, session=session)
            
            # Geração do voucher associado ao membro
            voucher_response = await set_voucher(member=member_schema, session=session)
            # Registro do estágio atual do membro convidado
            await set_stage(
                invited_id=member_schema.id,
                promoter_link_id=promoter_link_id,
                stage=stage,
                session=session
            )
            
            response = InvitedResponse(
                invited=member_schema.to_base64(),
                voucher=voucher_response.to_base64()
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

@router.post(
    "/tracking/{promoter_id}",
    response_model=MGM_Invitations,
    tags=[f"{tag_prefix} tracking"],
    **router_configs
)
async def tracking(
    promoter_id: uuid.UUID,
    stage: CreateStages,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """
    # **Tracking de Estágio do Convidado**

    Este recurso registra e acompanha os estágios de progresso de um **convidado** no programa **Member Get Member**.

    ---

    ###  Estágios disponíveis

    Cada estágio representa um ponto específico da jornada do convidado, desde o cadastro até o embarque. Alguns são registrados automaticamente pelo sistema.

    - **guest_registered**  
    Convidado cadastrado na campanha.  
    _Registro automático ao cadastrar um convidado via o endpoint_ `/invited/{promoter_id}`.

    - **selected_ticket**  
    Convidado escolheu uma passagem.  
    _Registro manual._

    - **applied_coupon**  
    Convidado inseriu um cupom.  
    _Registro manual._

    - **completed_purchase**  
    Convidado finalizou a compra.  
    _Registro manual._

    - **purchase_approved**  
    Compra aprovada após validação do pagamento.  
    _Registro automático após confirmação do pagamento._

    - **guest_boarded**  
    Convidado embarcou na viagem.  
    _Registro automático após validação de que a data de embarque é anterior à data atual._
    """

    try:
        promoter_link_id = await get_promoter_link_id_by_promoter_id(
            promoter_id=promoter_id,
            session=session,
            request=request
        )

        response = await set_stage(
            invited_id=stage.invited_id,
            promoter_link_id=promoter_link_id,
            stage=stage.stage,
            session=session
        )

        return response
    
    except Exception as e:
        raise MemberGetMemberException(
            request=request,
            message=str(e)
        )
