import httpx
from sqlmodel import Session, select
from app.models.menu_item import MenuItem
from app.models.place import Place

SHEETY_URL = "https://api.sheety.co/ed5b787d81ffb37813f8cfcf95dcb2f1/campusCravingsMenu1/sheet1"


async def sync_menu_from_sheety(session: Session) -> int:
    async with httpx.AsyncClient() as client:
        response = await client.get(SHEETY_URL)
        response.raise_for_status()
        data = response.json()

    items = data.get("sheet1", [])

    # Build a name -> place_id map for quick lookup
    places = session.exec(select(Place)).all()
    place_map = {place.name.lower(): place.id for place in places}

    # Clear existing menu items and re-sync
    existing = session.exec(select(MenuItem)).all()
    for item in existing:
        session.delete(item)
    session.commit()

    count = 0
    for item in items:
        place_name = item.get("placeName", "").lower()
        place_id = place_map.get(place_name)
        if place_id is None:
            continue  # skip items whose place isn't in our DB

        session.add(MenuItem(
            name=item.get("itemName", ""),
            description=item.get("description"),
            price=float(item.get("price", 0)),
            place_id=place_id,
        ))
        count += 1

    session.commit()
    return count
