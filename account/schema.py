import email
from pydantic import BaseModel, EmailStr
from datetime import datetime



class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: EmailStr    
    


class UserInDB(User):
    id: int
    password_hash: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str 
    email:EmailStr  
    password: str


class UserOut(User):
    id: int
    created_time: datetime

    class Config:
        from_attributes = True


