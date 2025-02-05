from typing import Annotated
from datetime import datetime, timedelta, timezone
import jwt
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from account.schema import UserCreate, UserOut, Token, UserInDB
from account.models import Account
from database.db import SessionDep



router = APIRouter()

SECRET_KEY = "7c21f06b792e69d5856b6c1089c6ac846aee516d900959dcd7676c9d09df3e0c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(password, password_hash):
    return pwd_context.verify(password, password_hash)


async def get_user(db: SessionDep, username: str) -> UserInDB | None:
    user = await db.scalar(select(Account).where(Account.username == username))
    if user:
        return UserInDB.model_validate(user)
    return None

async def authenticate_user(db: SessionDep, username: str, password: str):
    user = await get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: SessionDep) -> UserOut:
    # 创建新用户对象
    new_user = Account(
        username=user.username,        
        password_hash=get_password_hash(user.password),  # 加密密码
    )

    # 尝试将用户添加到数据库中
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)  # 刷新以获取完整对象（如自增 ID）
    except IntegrityError:
        # 处理用户名或邮箱的唯一性冲突
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists.",
        )

    return UserOut.model_validate(new_user)  # 返回新创建的用户对象



@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )  # 修正过期时间
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES,
    )