from fastapi import Request
from fastapi.responses import HTMLResponse
from app.dependencies import SessionDep
from app.dependencies.auth import IsUserLoggedIn, get_current_user
from app.models.place import Place
from app.models.favourite import Favourite
from app.models.review import Review
from sqlmodel import select
from . import router, templates

@router.get("/places", response_class=HTMLResponse)
async def browse_places_view(
    request: Request,
    db: SessionDep,
    user_logged_in: IsUserLoggedIn,
    search: str = None,
    category: str = None,
    rating: int = None
):
    user = None
    fav_place_ids = []
    if user_logged_in:
        user = await get_current_user(request, db)
        favs = db.exec(select(Favourite).where(Favourite.user_id == user.id)).all()
        fav_place_ids = [f.place_id for f in favs]

    all_reviews = db.exec(select(Review)).all()
    avg_ratings = {}
    review_counts = {}
    all_places_for_ratings = db.exec(select(Place)).all()
    for place in all_places_for_ratings:
        place_reviews = [r for r in all_reviews if r.place_id == place.id]
        review_counts[place.id] = len(place_reviews)
        if place_reviews:
            avg_ratings[place.id] = round(sum(r.rating for r in place_reviews) / len(place_reviews), 1)
        else:
            avg_ratings[place.id] = None

    query = select(Place)
    if search:
        query = query.where(Place.name.ilike(f"%{search}%"))
    if category:
        query = query.where(Place.category == category)
    places = db.exec(query).all()

    if rating:
        places = [p for p in places if avg_ratings.get(p.id) and int(avg_ratings[p.id]) == rating]

    categories = sorted(set(p.category for p in all_places_for_ratings))

    # Recommendations based on favourited categories
    recommendations = []
    if user and user.role != "admin" and fav_place_ids:
        fav_places = db.exec(select(Place).where(Place.id.in_(fav_place_ids))).all()
        fav_categories = set(p.category for p in fav_places)
        if fav_categories:
            recommendations = db.exec(
                select(Place).where(
                    Place.category.in_(fav_categories),
                    Place.id.not_in(fav_place_ids)
                )
            ).all()
            # Sort by highest rated first, then limit to 3
            recommendations = sorted(
                recommendations,
                key=lambda p: avg_ratings.get(p.id) or 0,
                reverse=True
            )[:3]

    return templates.TemplateResponse(request=request, name="browse_places.html", context={
        "places": places,
        "user": user,
        "search": search,
        "categories": categories,
        "selected_category": category,
        "selected_rating": rating,
        "fav_place_ids": fav_place_ids,
        "avg_ratings": avg_ratings,
        "review_counts": review_counts,
        "recommendations": recommendations
    })