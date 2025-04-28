
from sqlmodel import SQLModel
from typing import Optional, List
from datetime import date


class BrandBase (SQLModel ): 
  name: str
  country_origin : str
  description : str
  date_of_creation: date
  url : str