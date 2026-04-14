from fastapi import HTTPException
from app.dependencies import SessionDep
from app.repositories.menu_item import get_by_place_id
from . import api_router


@api_router.get("/menu/{place_id}")
def get_menu(place_id: int, db: SessionDep):
    items = get_by_place_id(db, place_id)
    return [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": item.price,
        }
        for item in items
    ]
