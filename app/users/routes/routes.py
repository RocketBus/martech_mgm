
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db import get_session
from app.users.models.users import UserResponse, UserCreate, TokenResponse, UserLogin, TokenVerifyResponse
from app.auth.auth_handler import sign_jwt
from app.auth.auth_bearer import JWTBearer
from app.users.crud.users import create_admin,get_email,get_username,user_login
from app.config.settings import environment_secrets,ENVIRONMENT_LOCAL

router = APIRouter()

@router.post('/login', response_model=TokenResponse, tags=['users'])
async def login(user: UserLogin, request: Request, response: Response, session: AsyncSession = Depends(get_session)):
    try:
        user = await user_login(username=user.username, session=session, password=user.password)

        access_token = sign_jwt(
            user.id,
            expires=600, # 10min
            token_type="access"
        )

        refresh_token = sign_jwt(
            user.id,
            expires=3600 * 24 * 7,  # 7 dias, por exemplo
            token_type="refresh"
        )

        # Armazenar o access token como cookie seguro
        response.set_cookie(
            key='a_mgm',
            value=access_token,
            httponly=True,
            secure=True if ENVIRONMENT_LOCAL == 'prod' else False
        )
        response.set_cookie(
            key='r_mgm',
            value=refresh_token,
            httponly=True,
            secure=True if ENVIRONMENT_LOCAL == 'prod' else False
        )

        return TokenResponse(access_token=access_token,refresh_token=refresh_token)

    except HTTPException as e:
        raise e

    

@router.get("/verify",
            dependencies=[Depends(JWTBearer())],
            response_model=TokenVerifyResponse,
            tags=['users'],
)
async def verify_token():
    pass
    return TokenVerifyResponse(token=True)

@router.post("/create/{access_token}", response_model=UserResponse,tags=['users'])
async def create_user(user_create: UserCreate,access_token:str, session: AsyncSession = Depends(get_session)):
    try:
        if access_token != environment_secrets['ACCESS_TOKEN']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Access_token inválido."
            )
        user = await create_admin(
            session=session,
            username=user_create.username,
            email=user_create.email,
            password=user_create.password
        )
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


