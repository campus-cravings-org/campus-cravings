from fastapi import Request, Form
from fastapi.responses import RedirectResponse
from app.dependencies import SessionDep
from app.dependencies.auth import IsUserLoggedIn, get_current_user
from app.models.review import Review
from sqlmodel import select
from . import router

@router.post("/reviews/{place_id}")
async def submit_review(
    request: Request,
    place_id: int,
    db: SessionDep,
    user_logged_in: IsUserLoggedIn,
    rating: int = Form(...),
    comment: str = Form(None),
):
    if not user_logged_in:
        return RedirectResponse("/login", status_code=302)
    
    user = await get_current_user(request, db)

    existing = db.exec(
        select(Review).where(Review.user_id == user.id, Review.place_id == place_id)
    ).first()

    if not existing:
        review = Review(user_id=user.id, place_id=place_id, rating=rating, comment=comment)
        db.add(review)
        db.commit()

    return RedirectResponse(f"/places/{place_id}", status_code=302)