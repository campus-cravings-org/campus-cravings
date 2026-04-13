from fastapi import Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep
from app.models.menu_item import MenuItem
from app.models.place import Place
from sqlmodel import select
from . import router, templates

@router.get("/admin/places/{place_id}/menu", response_class=HTMLResponse)
async def admin_menu_view(request: Request, place_id: int, user: AdminDep, db: SessionDep):
    place = db.get(Place, place_id)
    menu_items = db.exec(select(MenuItem).where(MenuItem.place_id == place_id)).all()
    return templates.TemplateResponse(request=request, name="admin_menu_items.html", context={
        "user": user,
        "place": place,
        "menu_items": menu_items
    })

@router.post("/admin/places/{place_id}/menu/add")
async def admin_add_menu_item(
    request: Request,
    place_id: int,
    user: AdminDep,
    db: SessionDep,
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...)
):
    item = MenuItem(place_id=place_id, name=name, description=description, price=price)
    db.add(item)
    db.commit()
    return RedirectResponse(url=f"/admin/places/{place_id}/menu", status_code=302)

@router.post("/admin/places/{place_id}/menu/edit/{item_id}")
async def admin_edit_menu_item(
    request: Request,
    place_id: int,
    item_id: int,
    user: AdminDep,
    db: SessionDep,
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...)
):
    item = db.get(MenuItem, item_id)
    if item:
        item.name = name
        item.description = description
        item.price = price
        db.add(item)
        db.commit()
    return RedirectResponse(url=f"/admin/places/{place_id}/menu", status_code=302)

@router.post("/admin/places/{place_id}/menu/delete/{item_id}")
async def admin_delete_menu_item(
    request: Request,
    place_id: int,
    item_id: int,
    user: AdminDep,
    db: SessionDep
):
    item = db.get(MenuItem, item_id)
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url=f"/admin/places/{place_id}/menu", status_code=302)