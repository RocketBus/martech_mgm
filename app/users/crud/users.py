from sqlalchemy.ext.asyncio import AsyncSession
from app.users.models.users import User
from sqlalchemy.future import select
from fastapi import HTTPException, status
from passlib.hash import bcrypt


def __user_does_not_exist()->HTTPException:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Username does not exist"
    )
    

async def user_exists(username:str,email:str,session:AsyncSession) -> None:
    query = select(User).where((User.username == username) | (User.email == email))
    result = await session.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
            )
    return True


async def get_user_by_id(user_id:str,session:AsyncSession)->User:
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalars().first()
    if not user:
        raise __user_does_not_exist()
    return user


async def get_email(email:str,session:AsyncSession)->User:
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    user = result.scalars().first()
    if not user:
        raise __user_does_not_exist()
    return user


async def get_username(username: str, session: AsyncSession) -> User:
    query = select(User).where(User.username == username)
    result = await session.execute(query)
    user = result.scalars().first()
    if not user:
        raise __user_does_not_exist()
    return user


async def password_hash(password:str):
    return  bcrypt.hash(password)


async def user_login(password: str,username : str,session: AsyncSession) -> bool:
    user = await get_username(username=username,session=session)
    if not bcrypt.verify(password,user.password):
        raise HTTPException(status_code=400,detail="wrong username or password")
    return user
    
    
async def create_admin(session: AsyncSession, username: str, email: str, password: str) -> User:
    await user_exists(username,email,session)
    password = await password_hash(password)
    user = User(username=username,password=password,email=email)
    session.add(user) 
    await session.commit()
    await session.refresh(user)
    return user