from sqlmodel import Field, SQLModel
from typing import Optional
from pydantic import EmailStr


class UserBase(SQLModel,):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role: str = "user"  #default role is user, admin role is for management

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)