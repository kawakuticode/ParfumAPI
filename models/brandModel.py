from typing import Optional, List
from datetime import date
from sqlmodel import SQLModel, Field
from typing import Optional


class BrandBase (SQLModel ): 
  name: str
  country_origin : str
  description : str
  date_of_creation: date
  url : str

class Brand(BrandBase, table = True) : 
 __tablename__ = "brands"
 id:Optional[int] = Field(default=None,  primary_key = True, nullable=False) 