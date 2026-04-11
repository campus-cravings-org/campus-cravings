from sqlmodel import Field, SQLModel
from typing import Optional

class Place(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  #auto gen prim key
    name: str                                                
    description: str                                         
    category: str                                              #like fast food, coffee shop, restaurant etc
    image_url: Optional[str] = None                            # image for the place but its optional
    google_maps_url: Optional[str] = None                      # google maps link for directions