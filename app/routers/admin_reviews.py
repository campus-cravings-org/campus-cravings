from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep
from app.models.review import Review
from app.models.place import Place
from app.models.user import User
from sqlmodel import select
from . import router, templates

@router.get("/admin/reviews", response_class=HTMLResponse)
async def admin_reviews_view(request: Request, user: AdminDep, db: SessionDep):
    reviews = db.exec(select(Review)).all()
    reviews_with_info = []
    for review in reviews:
        place = db.get(Place, review.place_id)
        reviewer = db.get(User, review.user_id)
        reviews_with_info.append({
            "review": review,
            "place_name": place.name if place else "Unknown",
            "username": reviewer.username if reviewer else "Unknown"
        })
    return templates.TemplateResponse(request=request, name="admin_reviews.html", context={
        "user": user,
        "reviews": reviews_with_info
    })

@router.post("/admin/reviews/delete/{review_id}")
async def admin_delete_review(request: Request, review_id: int, user: AdminDep, db: SessionDep):
    review = db.get(Review, review_id)
    if review:
        db.delete(review)
        db.commit()
    return RedirectResponse(url="/admin/reviews", status_code=302)