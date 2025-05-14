from app.member_get_member.v2.models.invitations import MGM_Invitations
from app.member_get_member.v2.schema.invitations import StageCount, InputType

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select 
from sqlalchemy import func

async def count_stages(link_id: uuid.UUID, session: AsyncSession) -> dict:
    """
    Conta a quantidade de membros por estágio com base no `link_id` do promotor.

    Agrupa as entradas na tabela `MGM_Invitations` por `stage`, retornando a contagem
    de convidados por cada estágio. Garante que todos os estágios possíveis definidos
    no enum `InputType` estejam presentes no resultado, mesmo que com valor 0.

    Args:
        link_id (uuid.UUID): Identificador único do link do promotor.
        session (AsyncSession): Sessão assíncrona com o banco de dados.

    Returns:
        dict: Um dicionário com o nome do estágio como chave e a contagem como valor.
    """
    stmt = (
        select(MGM_Invitations.stage, func.count(MGM_Invitations.stage))
        .group_by(MGM_Invitations.stage)
    ).where(MGM_Invitations.link_id == link_id)

    results = await session.execute(stmt)

    # Constrói um dicionário com as contagens por estágio
    counts = {row[0]: row[1] for row in results.all()}

    # Garante que todos os estágios possíveis estejam presentes com valor 0 se não houverem registros
    for stage in InputType:
        counts.setdefault(stage.value, 0)

    return counts


async def set_stage(
    invited_id: uuid.UUID,
    promoter_link_id: uuid.UUID,
    stage: str,
    session: AsyncSession
) -> MGM_Invitations:
    """
    Registra um novo estágio para um membro convidado no programa MGM.

    Cria um novo registro na tabela `MGM_Invitations` associando o membro
    convidado, o link do promotor e o estágio atual.

    Args:
        invited_id (uuid.UUID): ID do membro que foi convidado.
        promoter_link_id (uuid.UUID): ID do link do promotor que realizou o convite.
        stage (str): Nome do estágio atual (ex: "guest_registered").
        session (AsyncSession): Sessão assíncrona com o banco de dados.

    Returns:
        MGM_Invitations: Instância criada da tabela `MGM_Invitations`.

    Raises:
        Exception: Caso ocorra algum erro na criação do registro.
    """
    try:
        schema = MGM_Invitations(
            stage=stage,
            member_id=invited_id,
            link_id=promoter_link_id
        )
        session.add(schema)
        return schema

    except Exception as e:
        raise e  # Relança a exceção para tratamento externo
