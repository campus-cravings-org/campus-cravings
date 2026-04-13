import uvicorn
from fastapi import FastAPI, Request, status
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from app.routers import templates, static_files, router, api_router
from app.config import get_settings
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import create_db_and_tables
    from sqlmodel import Session, select
    from app.database import engine
    from app.models.user import User
    from app.models.place import Place
    from app.models.menu_item import MenuItem
    from app.models.review import Review
    from app.utilities.security import encrypt_password
    create_db_and_tables()
    # Seed default users on startup
    with Session(engine) as session:
        if not session.exec(select(User).where(User.username == "bob")).first():
            session.add(User(username="bob", email="bob@mail.com", password=encrypt_password("bobpass"), role="user"))
        if not session.exec(select(User).where(User.username == "admin")).first():
            session.add(User(username="admin", email="admin@mail.com", password=encrypt_password("adminpass"), role="admin"))
        session.commit()
    # Seed default places
    with Session(engine) as session:
            if not session.exec(select(Place)).first():
                session.add(Place(name="Dee & Vees", description="Creole Food", category="Creole", image_url="https://images.unsplash.com/photo-1544025162-d76694265947?w=400"))
                session.add(Place(name="La Bloom Café", description="Coffee, Drinks and Food items", category="Cafe", image_url="https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400"))
                session.add(Place(name="Caribbean Natural Juices", description="Fresh Juices", category="Drinks", image_url="https://images.unsplash.com/photo-1622597467836-f3285f2131b8?w=800"))
                session.add(Place(name="Celes and Son", description="Home-style Creole Cooking", category="Creole", image_url="https://images.unsplash.com/photo-1544025162-d76694265947?w=400"))
                session.add(Place(name="Maureen's Cuisine", description="Pies, Sandwiches & Snacks", category="Snacks", image_url="https://images.unsplash.com/photo-1509722747041-616f39b57569?w=400"))
                session.add(Place(name="Oriental Cuisine", description="Chinese Food", category="Chinese", image_url="https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400"))
                session.add(Place(name="Lee's Doubles", description="Doubles and local street food", category="Street Food", image_url="https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400"))
                session.add(Place(name="Juman's Roti Shop", description="Roti and curries", category="Roti", image_url="https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400"))
                session.add(Place(name="Pita Pit", description="Wraps and Paninis", category="Wraps", image_url="https://images.unsplash.com/photo-1509722747041-616f39b57569?w=400"))
                session.add(Place(name="Rituals Coffee House", description="Coffee, Drinks & Food Items", category="Cafe", image_url="https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400"))
                session.add(Place(name="Linda's", description="Pastries, Salads, Breads & Juices", category="Bakery", image_url="https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=400"))
                session.add(Place(name="Ave 5055", description="Desserts", category="Desserts", image_url="https://images.unsplash.com/photo-1551024601-bec78aea704b?w=400"))
                session.add(Place(name="The Gourmet Pot", description="Contemporary Cuisine", category="Fine Dining", image_url="https://images.unsplash.com/photo-1544025162-d76694265947?w=400"))
                session.add(Place(name="KFC", description="Fries and Chicken", category="Fast Food", image_url="https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400"))
                session.add(Place(name="Subway", description="Sub Sandwiches", category="Fast Food", image_url="https://images.unsplash.com/photo-1509722747041-616f39b57569?w=400"))
                session.add(Place(name="Benny's BBQ & Burgers", description="Burgers & BBQ", category="Burgers", image_url="https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400"))
                session.add(Place(name="Boba and Brew Café", description="Pastries, Smoothies and Ice Cream", category="Cafe", image_url="https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400"))
                session.add(Place(name="AI Mohammed", description="Burgers and sandwiches", category="Burgers", image_url="https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400"))
                session.commit()
    # Sync menu from Sheety on startup
    with Session(engine) as session:
        from app.services.menu_service import sync_menu_from_sheety
        try:
            synced = await sync_menu_from_sheety(session)
            print(f"[startup] Synced {synced} menu items from Sheety")
        except Exception as e:
            print(f"[startup] Menu sync failed (continuing anyway): {e}")
    yield


app = FastAPI(middleware=[
    Middleware(SessionMiddleware, secret_key=get_settings().secret_key)
],
    lifespan=lifespan
)   

app.include_router(router)
app.include_router(api_router)
app.mount("/static", static_files, name="static")

@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_redirect_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        request=request, 
        name="401.html",
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=get_settings().app_host, port=get_settings().app_port, reload=get_settings().env.lower()!="production")