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
    review = Review(user_id=user.id, place_id=place_id, rating=rating, comment=comment)
    db.add(review)
    db.commit()
    return RedirectResponse(f"/places/{place_id}", status_code=302)

@router.post("/reviews/delete/{review_id}")
async def delete_review(
    request: Request,
    review_id: int,
    db: SessionDep,
    user_logged_in: IsUserLoggedIn,
):
    if not user_logged_in:
        return RedirectResponse("/login", status_code=302)
    user = await get_current_user(request, db)
    review = db.get(Review, review_id)
    if review and review.user_id == user.id:
        place_id = review.place_id
        db.delete(review)
        db.commit()
        return RedirectResponse(f"/places/{place_id}", status_code=302)
    return RedirectResponse("/places", status_code=302)

@router.post("/reviews/edit/{review_id}")
async def edit_review(
    request: Request,
    review_id: int,
    db: SessionDep,
    user_logged_in: IsUserLoggedIn,
    rating: int = Form(...),
    comment: str = Form(None),
):
    if not user_logged_in:
        return RedirectResponse("/login", status_code=302)
    user = await get_current_user(request, db)
    review = db.get(Review, review_id)
    if review and review.user_id == user.id:
        review.rating = rating
        review.comment = comment
        db.add(review)
        db.commit()
        return RedirectResponse(f"/places/{review.place_id}", status_code=302)
    return RedirectResponse("/places", status_code=302)