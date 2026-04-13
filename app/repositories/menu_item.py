from sqlmodel import Session, select
from app.models.menu_item import MenuItem


def get_by_place_id(session: Session, place_id: int) -> list[MenuItem]:
    return session.exec(select(MenuItem).where(MenuItem.place_id == place_id)).all()


def delete_by_place_id(session: Session, place_id: int):
    items = get_by_place_id(session, place_id)
    for item in items:
        session.delete(item)
    session.commit()


def create(session: Session, item: MenuItem) -> MenuItem:
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
