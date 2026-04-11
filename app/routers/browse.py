from fastapi import Request
from fastapi.responses import HTMLResponse
from app.dependencies import SessionDep
from app.dependencies.auth import IsUserLoggedIn, get_current_user
from app.models.place import Place
from sqlmodel import select
from . import router, templates

@router.get("/places", response_class=HTMLResponse)
async def browse_places_view(
    request: Request,
    db: SessionDep,
    user_logged_in: IsUserLoggedIn,
    search: str = None,
    category: str = None
):
    user = None
    if user_logged_in:
        user = await get_current_user(request, db)
    
    query = select(Place)
    if search:
        query = query.where(Place.name.contains(search))
    if category:
        query = query.where(Place.category == category)
    places = db.exec(query).all()

    # Get all unique categories for dropdown
    all_places = db.exec(select(Place)).all()
    categories = sorted(set(p.category for p in all_places))

    return templates.TemplateResponse(request=request, name="browse_places.html", context={
        "places": places,
        "user": user,
        "search": search,
        "categories": categories,
        "selected_category": category
    })