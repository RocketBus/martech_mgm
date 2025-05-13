from sqlmodel import SQLModel, Field,Relationship
import uuid
from datetime import datetime

class UserBase(SQLModel):
    username: str
    email: str
    password: str

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    
class UserCreate(SQLModel):
    username: str
    email: str
    password: str

class UserResponse(SQLModel):
    id:uuid.UUID
    username: str
    email: str

class UserLogin(SQLModel):
    username: str
    password: str

class TokenResponse(SQLModel):
    access_token: str
    refresh_token: str


class TokenVerifyResponse(SQLModel):
    token:bool