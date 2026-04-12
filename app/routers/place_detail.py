from fastapi import Request
from fastapi.responses import HTMLResponse
from app.dependencies import SessionDep
from app.dependencies.auth import IsUserLoggedIn, get_current_user
from app.models.place import Place
from app.models.menu_item import MenuItem
from app.models.review import Review
from app.models.favourite import Favourite
from app.models.user import User
from sqlmodel import select
from . import router, templates

@router.get("/places/{place_id}", response_class=HTMLResponse)
async def place_detail_view(
    request: Request,
    place_id: int,
    db: SessionDep,
    user_logged_in: IsUserLoggedIn,
):
    user = None
    fav_place_ids = []
    if user_logged_in:
        user = await get_current_user(request, db)
        favs = db.exec(select(Favourite).where(Favourite.user_id == user.id)).all()
        fav_place_ids = [f.place_id for f in favs]

    place = db.get(Place, place_id)
    menu_items = db.exec(select(MenuItem).where(MenuItem.place_id == place_id)).all()
    
    reviews = db.exec(select(Review).where(Review.place_id == place_id)).all()
    reviews_with_users = []
    for review in reviews:
        reviewer = db.get(User, review.user_id)
        reviews_with_users.append({
            "review": review,
            "username": reviewer.username if reviewer else "Anonymous"
        })

    return templates.TemplateResponse(request=request, name="place_detail.html", context={
        "place": place,
        "menu_items": menu_items,
        "reviews": reviews_with_users,
        "user": user,
        "fav_place_ids": fav_place_ids
    })