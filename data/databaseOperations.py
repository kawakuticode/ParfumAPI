from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy import text
import logging

from models.brandModel import Brand
from models.parfumModel import Parfum
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

class DatabaseOperations:
    def __init__(self, engine):
        self.engine = engine

    async def connection_database_status(self) -> bool:
        try:
            async with self.engine.begin() as conn:
                # Execute the query
                query = text("SELECT name, collation_name FROM sys.databases")
                result = await conn.execute(query)
                
                # Process the results
                databases = [{"name": row[0], "collation_name": row[1]} for row in result ]
                for db in databases:
                    print(f"Name: {db['name']}\nCollation Name: {db['collation_name']}\n")
                print("connected to the database sucessfully....")
                return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    async def create_db_and_tables(self):
        try:
            async with self.engine.begin() as conn:
                print(SQLModel.metadata.tables)
                # Drop and create tables using SQLModel's metadata
                await conn.run_sync(SQLModel.metadata.drop_all)
                await conn.run_sync(Brand.metadata.create_all)
                print("Database table Brand created successfully.")

                await conn.execute(
                text("INSERT INTO brand (name, country_origin, description, date_of_creation, url) "
                     "VALUES (:name, :country_origin, :description, :date_of_creation, :url)"),
                [{"name": "Giorgio Armani", "country_origin": "Italy",
                  "description": "A luxury fashion house founded in 1975.",
                  "date_of_creation": "1975-07-24", "url": "https://www.armani.com"}]
            )
                print("Sample data inserted into `brand` table.")

                await conn.run_sync(Parfum.metadata.create_all)
            # Optional: Insert sample data into the `parfum` table
                await conn.execute(
                text("INSERT INTO parfum (name, brand_id, launch_year, concentration, fragance_family, gender_target, image_url) "
                     "VALUES (:name, :brand_id, :launch_year, :concentration, :fragance_family, :gender_target, :image_url)"),
                [{"name": "Armani Code", "brand_id": 1, "launch_year": 2004,
                  "concentration": "Eau de Parfum", "fragance_family": "Woody Aromatic",
                  "gender_target": "Male", "image_url": "https://www.armani.com"}]
            )               
                 

              
                

      
            
            print("Sample data inserted into `parfum` table.")
        except Exception as error_db:
            print(f"An error occurred: {error_db}")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            yield session
