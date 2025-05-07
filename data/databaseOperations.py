import time
import urllib
from sqlalchemy.ext import asyncio
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy import text
import logging
import json
import pyodbc
from models.brandModel import Brand
from models.parfumModel import Parfum

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

class DatabaseOperations:
    
    def __init__(self, engine):
        self.engine = engine
       

    async def connection_database_status(self) -> bool:
        transient_errors = ['28000']
        max_retries = 2
        retry_delay = 5  # Seconds

        for attempt in range(1, max_retries + 1):
            try:
                async with self.engine.begin() as conn:
                    query = text("SELECT name, collation_name FROM sys.databases")
                    result = await conn.execute(query)
                    databases = [{"name": row[0], "collation_name": row[1]} for row in result]

                    for db in databases:
                        print(f"Connected successfully to: {db['name']} - {db['collation_name']}")
                    return True

            except pyodbc.Error as ex:
               
                error_code = str(ex.args[0])
                print(f"Caught exception: {ex}")
                
                if error_code in transient_errors:

                    print(f"Transient error {error_code} detected. Retrying with new engine parameters... ({attempt}/{max_retries})")

                    with open("configAD.json", "r") as file:
                        config_active_directory = json.load(file)       
                        odbc_string = (
                        f"DRIVER={config_active_directory["driver"]};"
                        f"SERVER=tcp:{config_active_directory["server"]},{config_active_directory["port"]};"
                        f"DATABASE={config_active_directory["database"]};"
                        f"UID={config_active_directory["username"]};"
                        f"PWD={config_active_directory["password"]};"
                        )
   
                        print(odbc_string)
                        connection_url = f"mssql+aioodbc:///?odbc_connect={urllib.parse.quote_plus(odbc_string)}"
 
                        # Replace engine with new parameters
                        self.engine = create_async_engine(f"mssql+aioodbc:///?odbc_connect={connection_url}",
                        future=True,
                        echo=True
                        )   
                    await asyncio.sleep(retry_delay)  
                else:
                    
                    print(f"Critical error {error_code}. Unable to connect.")
                    return False

            print("Maximum retry attempts reached. Connection failed.")
            return False

    async def create_db_and_tables(self):
        try:
            async with self.engine.begin() as conn:

                print(SQLModel.metadata.tables)
                # Drop and create tables using SQLModel's metadata
                await conn.run_sync(SQLModel.metadata.drop_all)
                await conn.run_sync(Brand.metadata.create_all)
                print("Database table Brands created successfully.")

                # Optional: Insert sample data into the `brand` table 
                await conn.execute(
                text("INSERT INTO brands (name, country_origin, description, date_of_creation, url) "
                     "VALUES (:name, :country_origin, :description, :date_of_creation, :url)"),
                [{"name": "Giorgio Armani", "country_origin": "Italy",
                  "description": "A luxury fashion house founded in 1975.",
                  "date_of_creation": "1975-07-24", "url": "https://www.armani.com"}]
            )
                print("Sample data inserted into `brands` table.")
            
                await conn.run_sync(Parfum.metadata.create_all)
                print("Database table Parfums created successfully.")

                notes = {
                    "top": ["Vert de Bergamote", "Bergamot Heart (sourced from Calabria, Italy)"],
                    "mid": ["Clary Sage Heart (from Provence, France)", "Resinoid Iris (from Morocco)"],
                    "base": ["Tonka Bean", "Cedarwood"]
}
                # Optional: Insert sample data into the `parfum` table
                await conn.execute(
                text("INSERT INTO parfums (name, brand_id, launch_year, concentration, fragrance_family, gender_target, image_url , notes) "
                     "VALUES (:name, :brand_id, :launch_year, :concentration, :fragance_family, :gender_target, :image_url, :notes)"),
                [{"name": "Armani Code", "brand_id": 1, "launch_year": 2004,
                  "concentration": "Eau de Parfum", "fragance_family": "Woody Aromatic",
                  "gender_target": "Male", "image_url": "https://www.armani.com" , "notes": json.dumps(notes)}]
            )                          
            print("Sample data inserted into `parfums` table.")
        except Exception as error_db:
            print(f"An error occurred: {error_db}")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            yield session
