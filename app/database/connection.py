from sqlalchemy.orm import sessionmaker
import json
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.exc import SQLAlchemyError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERECT_FILE = os.path.join(BASE_DIR, 'secrets.json')
serects = json.loads(open(SERECT_FILE).read())
DB = serects["DB"]

DB_URL = f"mysql+aiomysql://{DB['user']}:{DB['password']}@{DB['host']}/{DB['database']}"

engine = create_async_engine(DB_URL, echo=True, pool_pre_ping=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
