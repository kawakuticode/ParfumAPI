from sqlmodel import JSON, SQLModel, Field
from sqlalchemy import Column
from typing import Optional

class ParfumBase(SQLModel):
    name: str
    brand_id: int
    launch_year: int
    concentration: str
    fragrance_family: str
    gender_target: str
    image_url: Optional[str] = None
    notes: dict = Field(default={}, sa_column=Column(JSON))

class Parfum(ParfumBase, table=True):
    __tablename__ = "parfums"
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    brand_id: int = Field(index=True, foreign_key="brands.id")