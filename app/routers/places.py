from fastapi import Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from . import router, templates
from app.models.place import Place
from sqlmodel import select
from app.utilities.flash import flash

# View all places (admin panel)
@router.get("/admin/places", response_class=HTMLResponse)
async def admin_places_view(request: Request, db: SessionDep, current_user: AuthDep):
    if current_user.role != "admin":
        return RedirectResponse(url=request.url_for("index_view"), status_code=status.HTTP_303_SEE_OTHER)
    places = db.exec(select(Place)).all()
    return templates.TemplateResponse(request=request, name="admin_places.html", context={"places": places, "user": current_user})

# Add a place
@router.post("/admin/places/add", response_class=HTMLResponse)
async def add_place(request: Request, db: SessionDep, current_user: AuthDep,
    name: str = Form(), description: str = Form(), category: str = Form(), image_url: str = Form(default=None)):
    if current_user.role != "admin":
        return RedirectResponse(url=request.url_for("index_view"), status_code=status.HTTP_303_SEE_OTHER)
    place = Place(name=name, description=description, category=category, image_url=image_url)
    db.add(place)
    db.commit()
    flash(request, "Place added successfully!", "success")
    return RedirectResponse(url=request.url_for("admin_places_view"), status_code=status.HTTP_303_SEE_OTHER)

# Edit a place
@router.post("/admin/places/edit/{place_id}", response_class=HTMLResponse)
async def edit_place(request: Request, place_id: int, db: SessionDep, current_user: AuthDep,
    name: str = Form(), description: str = Form(), category: str = Form(), image_url: str = Form(default=None)):
    if current_user.role != "admin":
        return RedirectResponse(url=request.url_for("index_view"), status_code=status.HTTP_303_SEE_OTHER)
    place = db.get(Place, place_id)
    place.name = name
    place.description = description
    place.category = category
    place.image_url = image_url
    db.commit()
    flash(request, "Place updated!", "success")
    return RedirectResponse(url=request.url_for("admin_places_view"), status_code=status.HTTP_303_SEE_OTHER)

# Delete a place
@router.post("/admin/places/delete/{place_id}", response_class=HTMLResponse)
async def delete_place(request: Request, place_id: int, db: SessionDep, current_user: AuthDep):
    if current_user.role != "admin":
        return RedirectResponse(url=request.url_for("index_view"), status_code=status.HTTP_303_SEE_OTHER)
    place = db.get(Place, place_id)
    db.delete(place)
    db.commit()
    flash(request, "Place deleted!", "success")
    return RedirectResponse(url=request.url_for("admin_places_view"), status_code=status.HTTP_303_SEE_OTHER)