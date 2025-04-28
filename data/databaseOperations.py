
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

class DatabaseOperations:
    def __init__(self, engine):
        self.engine = engine

    async def create_db_and_tables(self):
        async with self.engine.begin() as conn:
            try:
                await conn.run_sync(SQLModel.metadata.drop_all)
                await conn.run_sync(SQLModel.metadata.create_all)
            except Exception as error_db:
                print(f"An error occurred: {error_db}")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:  
        async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
                yield session
