from sqlmodel import Field, SQLModel
from typing import Optional

class Favourite(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    place_id: int = Field(foreign_key="place.id")