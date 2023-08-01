from pydantic import BaseModel, EmailStr
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from typing import Optional
from pydantic.types import conint

# defining a class in the main schema or BaseModel so that requests can be validated
# Pydantic handles schema and error responses
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True # creating default value therefore optional

class PostCreate(PostBase):
    pass

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    email: EmailStr
    votes: int


class Post(BaseModel):
    id: int
    title: str
    content: str
    published: bool = True
    user_id: int

    #class Config:
     #   orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserInfo(BaseModel):
    id: int
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)
