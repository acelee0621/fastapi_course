from typing import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


SQLITE_DATABASE_URL = "sqlite+aiosqlite:///./course.db"

engine = create_async_engine(
    SQLITE_DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(class_=AsyncSession, expire_on_commit=False, bind=engine)


# 异步会话依赖
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


# 使用 Annotated 标注会话依赖
SessionDep = Annotated[AsyncSession, Depends(get_db)]
