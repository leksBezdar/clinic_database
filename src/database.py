from sqlalchemy import MetaData, NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from .config import settings
from .db_convention import DB_NAMING_CONVENTION


Base = declarative_base()
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)


if settings.MODE == "TEST":
    DATABASE_URL = settings.TEST_DATABASE_URL
    DATABASE_PARAMS = {"poolclass": NullPool}
elif settings.MODE == "PROD":
    DATABASE_URL = settings.PROD_DATABASE_URL
    DATABASE_PARAMS = {}
else:
    DATABASE_URL = settings.DATABASE_URL
    DATABASE_PARAMS = {}


async_engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)
