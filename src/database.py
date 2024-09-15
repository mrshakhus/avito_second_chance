from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import settings

if settings.MODE == "TEST":
    DATABASE_URL = "postgresql+asyncpg://postgres:2406@localhost:5432/test_tenders"
    DATABASE_PARAMS ={"poolclass": NullPool}
    pass
else:
    DATABASE_URL = settings.POSTGRES_CONN
    DATABASE_PARAMS ={}

engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass