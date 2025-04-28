
from sqlmodel import Field
from models.brandbase import BrandBase
from typing import Optional, List


class Brand(BrandBase, Table = True) : 
 __tablename__ = "brand"
 id:Optional[int] = Field(default=None, nullable=False, primary_key = True ) 
