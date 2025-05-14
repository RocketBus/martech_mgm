from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.config.settings import environment_secrets
from app.database.db import init_db

# Importação dos modelos para que o SQLModel reconheça e crie as tabelas
from app.member_get_member.v2.models.members import MGM_Members
from app.member_get_member.v2.models.links import MGM_Links, MGM_ClickTracking
from app.member_get_member.v2.models.invitations import MGM_Invitations
from app.member_get_member.v2.models.vouchers import MGM_vouchers
from app.member_get_member.v2.models.purchase import MGM_Purchases

# Importação das rotas
from app.users.routes import routes as user_route
from app.member_get_member.v2.routes import (
    promoter as mgm_promoter,
    invited as mgm_invited,
    members as mgm_members,
    link as mgm_link,
    purchase as mgm_purchase
)

# Origens permitidas para CORS
origins = [
    "https://www.clickbus.com.br"
]

# Instância do FastAPI com documentação desabilitada publicamente
app = FastAPI(
    title=settings.title,
    summary=settings.summary,
    description=settings.description,
    version=settings.VERSION,
    docs_url=None,           # Desativa /docs público
    redoc_url=None,          # Desativa /redoc público
    openapi_url=None         # Desativa /openapi.json público
)

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Autenticação básica para proteger a documentação
security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = environment_secrets["ROOTUSERNAME"]
    correct_password = environment_secrets["ROOTPASSWORD"]
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )

@app.get("/docs", include_in_schema=False)
def custom_swagger_ui(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    return get_swagger_ui_html(
        openapi_url="/openapi.json", title="Documentação protegida"
    )

@app.get("/openapi.json", include_in_schema=False)
def openapi(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    return get_openapi(
        title=settings.title,
        version=settings.VERSION,
        description=settings.description,
        summary=settings.summary,
        routes=app.routes
    )
# Inicialização do banco de dados ao subir a aplicação
@app.on_event("startup")
async def on_startup():
    await init_db()

# Inclusão das rotas
mgm_prefix = "/api/v2"

app.include_router(user_route.router, prefix="/admin")
app.include_router(mgm_promoter.router, prefix=mgm_prefix)
app.include_router(mgm_members.router, prefix=mgm_prefix)
app.include_router(mgm_purchase.router, prefix=mgm_prefix)
app.include_router(mgm_invited.router, prefix=mgm_prefix)
app.include_router(mgm_link.router, prefix=mgm_prefix)
