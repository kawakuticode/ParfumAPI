from sqlmodel import SQLModel, Field
from typing import Optional

class ParfumBase(SQLModel):
     name: str
     brand_id: int
     launch_year: int
     concentration: str
     fragance_family: str
     gender_target: str
     image_url: Optional[str] = None


class Parfum(ParfumBase, table=True):
     __tablename__ = "parfum"
     id: Optional[int] = Field(default=None, primary_key=True)
     brand_id: int = Field(index=True, foreign_key="brand.id")

class ParfumCreate(ParfumBase):
     pass