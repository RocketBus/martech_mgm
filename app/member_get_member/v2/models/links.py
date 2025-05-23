from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid


class MGM_ClickTracking(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    link_id: uuid.UUID = Field(foreign_key="mgm_links.id")
    clicked_at: Optional[datetime] = Field(default_factory=datetime.now)

    # Relacionamento opcional com a tabela MGM_Links
    link: Optional["MGM_Links"] = Relationship(back_populates="clicks")


class MGM_Links(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    member_id: uuid.UUID = Field(foreign_key="mgm_members.id")
    url: str
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    # Relacionamento para rastrear os cliques
    clicks: list[MGM_ClickTracking] = Relationship(back_populates="link")


    @classmethod
    def create_with_url(cls, member_id: uuid.UUID) -> "MGM_Links":
        url = f"https://www.clickbus.com.br?utm_source=automatic&utm_medium=crm&utm_campaign=member-get-member-convidado&utm_term=invited&utm_content={member_id}"
        return cls(member_id=member_id, url=url)
