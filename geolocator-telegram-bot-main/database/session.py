from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from bot.Config import DATABASE_URL  # убедись, что этот путь корректен

# Подключение к PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True)

# Асинхронная фабрика сессий
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)