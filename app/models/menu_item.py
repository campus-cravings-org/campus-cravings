from sqlmodel import Field, SQLModel
from typing import Optional

class MenuItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  
    name: str                                                    
    description: Optional[str] = None                           
    price: float                                                 
    place_id: int = Field(foreign_key="place.id")               #links this item to a Place