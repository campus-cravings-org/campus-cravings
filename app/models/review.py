from sqlmodel import Field, SQLModel
from typing import Optional

class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  
    rating: int                                                 #rating out of 5 
    comment: Optional[str] = None                               #optional comment to go with rating 
    user_id: int = Field(foreign_key="user.id")                 #links review to a User
    place_id: int = Field(foreign_key="place.id")               #links review to a Place