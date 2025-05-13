from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.db import init_db


from app.member_get_member.v2.models.members import MGM_Members
from app.member_get_member.v2.models.links import MGM_Links,MGM_ClickTracking
from app.member_get_member.v2.models.invitations import MGM_Invitations
from app.member_get_member.v2.models.vouchers import MGM_vouchers

from app.users.routes import routes as user_route
from app.member_get_member.v2.routes import (
    promoter as mgm_promoter,
    invited as mgm_invited,
    members as mgm_members
    )

origins = [
    "https://www.clickbus.com.br"
]

app = FastAPI(
    title=settings.title,
    summary=settings.summary,
    description=settings.description,
    version=settings.VERSION,
   
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Lista de origens permitidas
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)


@app.on_event("startup")
async def on_startup():
    await init_db()

mgm_prefix = "/v2"

app.include_router(user_route.router, prefix="/admin")
app.include_router(mgm_promoter.router, prefix=mgm_prefix)
app.include_router(mgm_members.router, prefix=mgm_prefix)
app.include_router(mgm_invited.router, prefix=mgm_prefix)
