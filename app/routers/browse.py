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
    search: str = None
):
    # Get current user if logged in
    user = None
    if user_logged_in:
        user = await get_current_user(request, db)
    
    # Get all places, filter by search if provided
    query = select(Place)
    if search:
        query = query.where(Place.name.contains(search))
    places = db.exec(query).all()
    
    return templates.TemplateResponse(request=request, name="browse_places.html", context={
        "places": places,
        "user": user,
        "search": search
    })