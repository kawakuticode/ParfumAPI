from typing import Union
from fastapi import Depends, FastAPI, Request
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from datetime import date
import traceback
import asyncio
import pyodbc

from data.parfum import Parfum
from data.brand import Brand
from models.parfumModel import ParfumBase, ParfumCreate
from data.databaseOperations import DatabaseOperations
from data.databaseConfig import DatabaseConfig

 # Sample data
brands = [Brand(name="Giorgio Armani", country_origin="Italy", description="Giorgio Armani is a luxury fashion house founded by Giorgio Armani, which designs, manufactures, distributes, and retails haute couture, ready-to-wear, leather goods, shoes, accessories, and fragrances.", date_of_creation=date(1975, 7, 24), url="https://www.armani.com"),
           # Add other brands here...
          ]

parfums = [Parfum(name="Armani Code", brand_id=1, launch_year=2004, concentration="Eau de Parfum", fragance_family="Woody Aromatic", gender_target="Male", image_url="https://www.armani.com/en-us/giorgio-armani/armani-code-75-ml-eau-de-parfum-cod-LD342900-NLP-75ML/"),
            # Add other parfums here...
           ]

class Main:
     def __init__(self):
        self.app = FastAPI()
        self.db_config = DatabaseConfig(
             driver = '',                            
             server = '',
             port = '',
             database = '', 
             username = '',
             password = ''
         )
        print(pyodbc.drivers())
         
        #if (self.db_config.can_connect()) :
        self.db_config.check_ip()
        self.engine = self.db_config.get_engine()
        self.db_operations = DatabaseOperations(self.engine)

        self.app.add_event_handler("startup", self.startup_event)
        self.app.add_event_handler("shutdown", self.shutdown_event)
        self.app.exception_handler(Exception)(self.global_exception_handler)

        self.app.get("/")(self.read_root)
        self.app.get("/parfums", response_model=list[Parfum])(self.get_parfums)
        self.app.post("/parfums")(self.add_parfum)
        # else : 
        #    print("Unable to connect to database .... :'( !!")
     async def startup_event(self):
         await self.db_operations.create_db_and_tables()
         await self.add_data_to_db()

     async def shutdown_event(self):
         with open("log.txt", mode="a") as log:
             log.write('Application shutdown at %s.\n' % date.now().strftime("%Y-%m-%d %H:%M:%S"))

     async def global_exception_handler(self, request: Request, exc: Exception):
         traceback.print_exc()  # Log the exception
         return JSONResponse(
             status_code=500,
             content={"message": "Internal Server Error"}
         )

     async def add_data_to_db(self, session: AsyncSession = Depends(DatabaseOperations.get_session)):
         async with session:
             session.add_all(brands)
             await session.commit()
             session.add_all(parfums)
             await session.commit()

     def read_root(self):
         return {"Welcome": "Parfum data base"}

     async def get_parfums(self, session: AsyncSession = Depends(DatabaseOperations.get_session)):
         try:
             result = await session.exec(select(Parfum))
             parfums = result.scalars().all()
             return [Parfum(name=parfum.name) for parfum in parfums]
         except ValueError:
             raise ValueError("This is an intentional error")

     async def add_parfum(self, parfum: ParfumCreate, session: AsyncSession = Depends(DatabaseOperations.get_session)):
         new_parfum = Parfum(name=parfum.name, brand_id=parfum.brand_id, launch_year=parfum.launch_year, concentration=parfum.concentration, fragance_family=parfum.fragance_family, gender_target=parfum.gender_target, image_url=parfum.image_url)
         session.add(new_parfum)
         await session.commit()
         await session.refresh(new_parfum)
         return new_parfum



# Create an instance of Main and expose the app
main = Main()
app = main.app

 # Run the main function
if __name__ == "__main__":
     asyncio.run(main.startup_event())
