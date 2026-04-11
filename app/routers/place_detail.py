from fastapi import Request
from fastapi.responses import HTMLResponse
from app.dependencies import SessionDep
from app.dependencies.auth import IsUserLoggedIn, get_current_user
from app.models.place import Place
from app.models.menu_item import MenuItem
from app.models.review import Review
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
    if user_logged_in:
        user = await get_current_user(request, db)

    place = db.get(Place, place_id)
    menu_items = db.exec(select(MenuItem).where(MenuItem.place_id == place_id)).all()
    reviews = db.exec(select(Review).where(Review.place_id == place_id)).all()

    template_name = "place_detail.html"

    return templates.TemplateResponse(request=request, name=template_name, context={
        "place": place,
        "menu_items": menu_items,
        "reviews": reviews,
        "user": user,
    })