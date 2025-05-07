
from sqlmodel import Field
from typing import Optional, List
from datetime import datetime
from models.parfumModel import ParfumBase

#SQL model

class Parfum(ParfumBase, Table = True) : 
 __tablename__ = "parfum"
 id:Optional[int] = Field(default=None, nullable=False, primary_key = True ) 
 brand_id: int = Field(index = True, foreign_key="brand.id")

 
 #notes: List["ParfumNote"] = []  # Relationship to PerfumeNote
 #dupes : List["Dupe"]  = []
 
 

 
 '''
class Note(SQLModel, Table = True) : 
    __tablename__ = "note"
    id: int = Field(primary_key = True ) 
    name: str
    description: str | None = None
    image_url: Optional[str] = None
    
class ParfumNote(SQLModel, Table= True):
    __tablename__ = "parfum_note"
    id: int = Field(primary_key = True ) 
    note_id: int = Field ( index=True, foreign_key= "note.id")
    #note_type: str  # e.g., Top, Middle, Base: str  #to be analyzed

class Dupe(SQLModel, Table = True) : 
 __tablename__ = "dupe"
 id:int = Field(primary_key = True ) 
 name: str
 brand_id: int = Field(index = True, foreign_key="brand.id")
 fragance_family: str 
 gender_target: str 
 image_url: Optional[str] = None
 notes: List["ParfumNote"] = []
 similarity_score: float

'''