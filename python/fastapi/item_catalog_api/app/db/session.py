from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.db.base import Base

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True  
)

# Factory for creating async session objects
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Dependency: provides a session to each endpoint
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session