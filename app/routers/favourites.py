from fastapi import Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.models.place import Place
from app.models.favourite import Favourite
from sqlmodel import select
from . import router, templates

# View favourites page
@router.get("/favourites", response_class=HTMLResponse)
async def favourites_view(request: Request, db: SessionDep, user: AuthDep):
    favs = db.exec(select(Favourite).where(Favourite.user_id == user.id)).all()
    place_ids = [f.place_id for f in favs]
    places = db.exec(select(Place).where(Place.id.in_(place_ids))).all()
    return templates.TemplateResponse(request=request, name="favourites.html", context={
        "places": places,
        "user": user,
        "fav_place_ids": place_ids
    })

# Add to favourites
@router.post("/favourites/add/{place_id}")
async def add_favourite(request: Request, place_id: int, db: SessionDep, user: AuthDep):
    existing = db.exec(select(Favourite).where(Favourite.user_id == user.id, Favourite.place_id == place_id)).first()
    if not existing:
        db.add(Favourite(user_id=user.id, place_id=place_id))
        db.commit()
    referer = request.headers.get("referer", "/places")
    return RedirectResponse(url=referer, status_code=status.HTTP_303_SEE_OTHER)

# Remove from favourites
@router.post("/favourites/remove/{place_id}")
async def remove_favourite(request: Request, place_id: int, db: SessionDep, user: AuthDep):
    fav = db.exec(select(Favourite).where(Favourite.user_id == user.id, Favourite.place_id == place_id)).first()
    if fav:
        db.delete(fav)
        db.commit()
    referer = request.headers.get("referer", "/favourites")
    return RedirectResponse(url=referer, status_code=status.HTTP_303_SEE_OTHER)