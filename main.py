
from typing import Union, Optional
from fastapi import Depends, FastAPI, Request , HTTPException , Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from datetime import date, datetime
from sqlalchemy import text
from models.parfumModel import Parfum, ParfumBase 
from models.brandModel import Brand, BrandBase 
from data.databaseOperations import DatabaseOperations
from data.databaseConfig import DatabaseConfig


import traceback
import asyncio
import pyodbc
import json



class Main:
     def __init__(self):
        self.app = FastAPI()
       # Load credentials from config file
        with open("config.json", "r") as file:
            config = json.load(file)
        
        self.db_config = DatabaseConfig(
            driver=config["driver"],
            server=config["server"],
            port=config["port"],
            database=config["database"],
            username=config["username"],
            password=config["password"]
        )
   
        
         
        
        self.db_config.check_ip()
        self.engine = self.db_config.get_engine()
        self.db_operations = DatabaseOperations(self.engine)

        self.app.add_event_handler("startup", self.startup_event)
        self.app.add_event_handler("shutdown", self.shutdown_event)
        self.app.exception_handler(Exception)(self.global_exception_handler)


        #Register routes
        self.app.get("/")(self.read_root)
        self.app.get("/parfums", response_model=list[ParfumBase])(self.get_parfums)
        #self.app.post("/parfums")(self.add_parfum)
        # else : 
        #    print("Unable to connect to database .... :'( !!")
     async def startup_event(self):  
         if await self.db_operations.connection_database_status() : 
                await self.db_operations.create_db_and_tables()
         else :
                print("Unable to connect to database .... shutting down the server !")
                await self.shutdown_event()

     async def shutdown_event(self):
         with open("log.txt", mode="a") as log:
             log.write('Application shutdown at %s.\n' % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

     async def global_exception_handler(self, request: Request, exc: Exception):
         traceback.print_exc()  # Log the exception
         return JSONResponse(
             status_code=500,
             content={"message": "Internal Server Error"}
         )
     '''
     async def add_data_to_db(self, session: AsyncSession = Depends(DatabaseOperations.get_session)):
         async with session:
             session.add_all(brands)
             await session.commit()
             session.add_all(parfums)
             await session.commit()
      '''
     
     def read_root(self):
         return {"Welcome": "Parfum data base"}
     
  

     async def get_parfums(
        name: Optional[str] = Query(None, description="Name of the parfum to filter"),
        session: AsyncSession = Depends(DatabaseOperations.get_session),
        limit: int = 10,
        offset: int = 0
        ) -> list[ParfumBase]:
        try:
            # Build the query dynamically
            query = select(Parfum).offset(offset).limit(limit)
            if name:
                query = query.where(Parfum.name == name)
        
                # Execute the query
                result = await session.exec(query)
                parfums = result.scalars().all()
        
            # Convert to response model
            return [ParfumBase(**parfum.dict()) for parfum in parfums]

        except Exception as e:
            print(f"Error fetching parfums: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch parfums")
    
'''

     async def add_parfum(self, parfum: ParfumCreate, session: AsyncSession = Depends(DatabaseOperations.get_session)):
         new_parfum = Parfum(name=parfum.name, brand_id=parfum.brand_id, launch_year=parfum.launch_year, concentration=parfum.concentration, fragance_family=parfum.fragance_family, gender_target=parfum.gender_target, image_url=parfum.image_url)
         session.add(new_parfum)
         await session.commit()
         await session.refresh(new_parfum)
         return new_parfum
'''


# Create an instance of Main and expose the app
main = Main()
app = main.app

 # Run the main function
if __name__ == "__main__":
     asyncio.run(main.startup_event())
