import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import ENVIRONMENT_LOCAL

from app.member_get_member.v2.schema.vouchers import Voucher,VoucherBase
from app.member_get_member.v2.schema.member import MembersResponse
from app.member_get_member.v2.models.vouchers import MGM_vouchers

async def set_voucher(member: MembersResponse, session: AsyncSession,is_promoter:bool = False) -> VoucherBase:
    """
    Cria e associa um voucher a um membro convidado no programa MGM.

    Utiliza a classe `Voucher` para gerar os dados do voucher e então
    persiste um novo registro na tabela `MGM_vouchers`, ligando o voucher ao membro.

    Args:
        member (MembersResponse): Objeto com os dados do membro convidado.
        session (AsyncSession): Sessão assíncrona do banco de dados.

    Returns:
        MGM_vouchers: Instância criada e associada ao voucher do membro.

    Raises:
        Exception: Propaga qualquer erro ocorrido na criação do voucher.
    """
    try:
        # Cria uma nova instância de voucher com os dados do membro (não é promotor)
        voucher = Voucher()
        
        if ENVIRONMENT_LOCAL == 'prod':
            voucher.create(
                is_promoter=is_promoter,
                email=member.email
            )
        
        # Cria o modelo de banco de dados associando o voucher ao membro
        voucher_invited = MGM_vouchers(
            voucher_id=voucher.voucher_id,
            code=voucher.code,
            end_at=voucher.end_at,
            member_id=member.id
        )
        session.add(voucher_invited)
        await session.flush()  # Garante que o ID e outros valores sejam atualizados

        return VoucherBase(
            voucher_id=voucher_invited.voucher_id,
            code=voucher_invited.code,
            end_at=voucher_invited.end_at
        )

    except Exception as e:
        raise e  # Relança exceções para tratamento externo
