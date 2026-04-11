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
            session.add(Place(name="KFC", description="Crispy fried chicken and sides", category="Fast Food", image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTkWhY1XzawqvlvUpmgw0GhOhTxg5cVu_XSmw&s"))
            session.add(Place(name="Rituals Coffee", description="Premium coffee and light bites", category="Cafe", image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQRrIvdMVwFuo0cMkLRMN3yIsozXr5Lv3yBXA&s"))
            session.add(Place(name="Subway", description="Fresh subs made your way", category="Fast Food", image_url="https://m.media-amazon.com/images/G/01/AdProductsWebsite/images/CaseStudies/Subway_-_Thumbnail._TTW_.jpg"))
            session.add(Place(name="Starbucks", description="Coffee drinks and pastries", category="Cafe", image_url="https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400"))
            session.add(Place(name="The Breakfast Shed", description="Local breakfast favourites", category="Local", image_url="https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=400"))
            session.add(Place(name="Island Grill", description="Caribbean grilled meats and sides", category="Local", image_url="https://images.unsplash.com/photo-1544025162-d76694265947?w=400"))
            session.add(Place(name="Pizza Hut", description="Pan pizzas and pasta", category="Pizza", image_url="https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400"))
            session.commit()
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